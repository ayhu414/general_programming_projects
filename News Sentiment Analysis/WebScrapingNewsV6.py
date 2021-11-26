import requests
import html5lib
import bs4
import re
import datetime
# To identify countries mentioned in the headlines
from geotext import GeoText
import csv
import pandas as pd

# A python file containing constants used across the project, e.g.
# dictionary mapping news source names to their URLS
import CONSTANTS as const

# Motivation: Create single "universal" web scraper that can return headlines from
# all 4 news sources: South China Morning Post (SCMP), NBC News, BBC, and
# Russia Today (RT). 

# Final output: Two pandas dataframes.
# i) countries mentioned in headlines, frequency of mentions, 
# news sources of mentions
# ii) words from headlines, news sources

# Strategy for creating universal web scraper:
# All news websites' headlines can be clicked into.
# So all the headline text must be in html <a> tags (links).
# For these news sources (and likely for others), the <a>
# tags or their parents must have some sort of class name
# indicating that they are news sources (e.g. "title" is in
# class name). 
# So scrape around a tags and their parents that have the right
# class names for a universal web scraper that works for all sources.

def check_tag_ok(tag):
    '''
    Check if an html tag is ok to scrape. Returns boolean. 
    (Is it a news article tag, or some other element of the website?)
    '''
    if tag.has_attr('class'):
        for class_name in tag['class']:
            # We only need the tag's class name to contain one of 
            # the class_markers stored in the CONSTANTS python file
            # to infer that tag is about a link.

            if any(class_marker in class_name for class_marker 
                in const.class_markers):

                return True
    else:
        return False


def get_links_objects(string_url):
    '''
    Given a news website url as string, returns list of
    the relevant html <a> tags that contain headlines.
    '''
    newspage_main = requests.get(string_url)
    soup_main = bs4.BeautifulSoup(newspage_main.content, 'html5lib')
    all_heading_tags = soup_main.find_all(const.tags_to_scrape)

    # List of <a> tags to return
    all_a_tags = []

    for heading_tag in all_heading_tags:
        if check_tag_ok(heading_tag):
            # If we come across an ok tag that is an <a> tag
            # already, check for whether it is a duplicate, and if
            # not, add it. 
            if heading_tag.name == 'a' \
            and heading_tag not in all_a_tags:
                all_a_tags.append(heading_tag)

            else:
                # If we come across an ok tag that is not an <a> tag,
                # e.g. a div, then add all its a tags not currently
                # in the list. 
                for a in heading_tag.find_all('a', href=True):
                    if a not in all_a_tags:
                        all_a_tags.append(a)

    return all_a_tags


def create_raw_string_from_as(found_a_objects):
    '''
    Given a list of found_a_objects, returns one raw string 
    concatenated from the text attribute of all the ok <a> tags 
    (as, as in plural of a).
    '''

    l = []
    for a in found_a_objects:

        # Logic: Check if a tag itself is ok to follow (does a tag refer to a
        # news article/story?), if the a tag's parent is ok to follow, or if
        # a tag has any children ok to folow. Then if yes to any of these,
        # append the text of the <a> tag to list.

        if check_tag_ok(a) or check_tag_ok(a.parent) or \
        any(check_tag_ok(child) for child in a.findChildren()):

            a_no_blanks = a.text.strip()

            if re.match('^[a-zA-Z0-9]+', a_no_blanks) and a_no_blanks not in l \
            and not a_no_blanks.startswith(const.ignore_articles):
                # Want to ignore e.g. trivial Lifestyle articles
                l.append(a_no_blanks)

    raw_string = ' '.join(l)

    return raw_string


def filter_raw_string(raw_string, return_country_freq=False):
    '''
    Given a raw string scraped from <a> tags, cleans it and
    scans each word in the raw string for country mentions.
    Also given a boolean, returns either a list of individual 
    filtered words or dictionary of countries mentioned to 
    number of mentions.
    '''
    valid_word_filter = re.findall(r'[a-zA-Z0-9]+', raw_string)
    filtered_words = []
    country_freq = {}
    for word in valid_word_filter:
        # Want to filte out e.g. "3 min ago" time markers
        for time_prefix in const.time_fillers:
            if word.startswith(time_prefix):
                word = word.strip(time_prefix)

        # GeoText will give us the 2-letter ISO country code of a
        # single word. We scan each word for a country mention. 
        country_pointer = list(GeoText(word).country_mentions)

        # If word is a country mention, it gets added to country_freq
        # dictionary. 
        if country_pointer != []:
            filtered_words.append(word)
            for country in country_pointer:
                if country not in country_freq:
                    country_freq[country] = 0
                country_freq[country] += 1
        else:
            # Process word into filtered_words list
            if len(word) >= 2:
                if word in const.english_words_set \
                and word not in const.abv_set:
                    filtered_words.append(word.lower())
                if word in const.abv_set:
                    filtered_words.append(word)

    filtered_words = [word for word in filtered_words \
    if word not in const.blacklist]

    if return_country_freq:
        return country_freq
    else:
        return filtered_words


def run_scraper(link_to_scrape, return_country_freq=False):
    '''
    Given a single string link to scrape and a boolean specifcation of
    whether to return country to frequency or list of filtered words, 
    returns specified output.
    '''

    links_scraped = get_links_objects(link_to_scrape)
    raw_string = create_raw_string_from_as(links_scraped)

    if return_country_freq:
        return filter_raw_string(raw_string, return_country_freq=True)
    else:
        return filter_raw_string(raw_string, return_country_freq=False)


def convert_to_pandas(list_of_links, return_country_df=False):
    '''
    Given a list of string links and a specification of what dataframe
    to return, returns either a pandas dataframe of filtered words scraped
    or a pandas dataframe of country mentions, along with a time stamp of
    scraping.
    '''
    
    time_now = datetime.datetime.now()
    time_stamp = time_now.strftime("%Y-%m-%d_%H:%M")

    country_freq_source = []
    word_source = []
    for link in list_of_links:
        news_source = const.news_sites_to_names[link]

        news_words = run_scraper(link, return_country_freq=False)
        countries_and_freq = run_scraper(link, return_country_freq=True)

        for word in news_words:
            word_source.append((word, news_source))

        for country, freq in countries_and_freq.items():
            country_freq_source.append((country, freq, news_source))

    word_source_df = pd.DataFrame(word_source)
    countries_freq_df = pd.DataFrame(country_freq_source)

    if return_country_df:
        return countries_freq_df, time_stamp
    else:
        return word_source_df, time_stamp



