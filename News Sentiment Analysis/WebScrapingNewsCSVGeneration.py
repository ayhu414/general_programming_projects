from WebScrapingNewsV6 import *

# Purpose of file:
# This file was used to generate all the past data csvs in scraped_csvs

def generate_csvs(list_of_links):
    '''
    Given a list of string links to scrape, generates two csvs of words scraped 
    and country frequencies for news source at the exact time of scraping.
    '''
    time_stamp = datetime.datetime.now()
    words_csv_name = 'words{}'.format(time_stamp)
    countries_csv_name = 'countries{}'.format(time_stamp)

    words_csv= open(words_csv_name, 'w')
    countries_csv = open(countries_csv_name, 'w')

    words_csv_writer = csv.writer(words_csv, delimiter=',')
    countries_csv_writer = csv.writer(countries_csv, delimiter=',')

    for link in list_of_links:
        news_source = const.news_sites_to_names[link]
        news_words = run_scraper(link, return_country_freq=False)
        for word in news_words:
            words_csv_writer.writerow([word, news_source])

        countries_and_freq = run_scraper(link, return_country_freq=True)

        for country, freq in countries_and_freq.items():
            countries_csv_writer.writerow([country, freq, news_source])


    words_csv.close()
    countries_csv.close()

generate_csvs(const.list_of_links)