import CONSTANTS as const
import WebScrapingNewsV6 as web_scraper
import get_dates # for fetching past data from scraped_csvs folder
import generate_map as gmp
import generate_countries_plot as gcp
import generate_wordcloud as gwc
import create_Markov_training as mk_training
# ^ Import Markov model used to guess what news source user's input sounds
# most like. 
import nlp 
# ^ For natural language processing, determining whether news sounds positive
# or negative.

# Purpose of this code:
# Create various initial figures to be loaded into Dash app.
# Generally, figures are initialized to represent all 4 news
# sources in one. 
# These initial figures are used extensively in app_features.py. 

# Live data figures:
# Get live countries and words dfs, with time stamps from web scraper.
# Also initialize live map and wordcloud. 
live_scraped_countries_df, live_time_stamp \
    = web_scraper.convert_to_pandas(const.list_of_links, return_country_df=True)

live_countries_map = \
    gmp.create_plotly_map(live_scraped_countries_df, live_time_stamp,
                          news_source='', globe_style=True)

live_word_df, live_current_time_stamp = \
    web_scraper.convert_to_pandas(const.list_of_links, return_country_df=False)

# Update the png file for wordcloud. Please refer to the generate_wordcloud.py
# documentation. But general idea is that Dash does not accept wordcloud objects,
# so they must be exported to png, and we add that wordcloud as image to Dash app.
gwc.export_wordcloud_to_png(live_word_df, news_source='', current_words=True)
live_wordcloud_file = './live_scraped_wordcloud.png'

# Past data figures:
sorted_times, times_to_countries_dfs = \
    get_dates.get_past_data(get_country_times=True)

# Initialize all past maps and wordclouds from the earliest time data.
earliest_time_stamp = sorted_times[0]
earliest_countries_df = times_to_countries_dfs[earliest_time_stamp]
earliest_countries_map = \
    gmp.create_plotly_map(earliest_countries_df, earliest_time_stamp,
                          news_source='', globe_style=True)

countries_time_plot = \
    gcp.make_country_freq_time_graph(sorted_times, times_to_countries_dfs, source='')

sorted_times, times_to_words_dfs =\
    get_dates.get_past_data(get_country_times=False)

earliest_time_stamp = sorted_times[0]
earliest_words_df = times_to_words_dfs[earliest_time_stamp]
gwc.export_wordcloud_to_png(earliest_words_df, news_source='', current_words=False)
past_wordcloud_file = './past_scraped_wordcloud.png'

# Training strings for Markov model used in app component that guesses what news
# source user input sounds most like. 
str_NBC, str_RT, str_SCMP, str_BBC = mk_training.generate_training_string()

# Table of dates to whether the news was positive or negative on that date 
# (using nlp natural language processing), for the news source specified.  
initial_sentiment_table = \
    nlp.generate_sentiment_plotly_table(news_source='')

