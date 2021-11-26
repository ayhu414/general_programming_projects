import numpy as np
import pandas as pd
import plotly as plt
import datetime
import plotly.express as px
import get_dates 
# ^ To get all of the past data scraped from scraped_csvs folder

# Purpose of this code:
# Generate a plotly line plot of dates to frequencies of country mentions
# for the top 5 overall countries of each news source (top 5 over past data
# collection period) 


def create_total_tbl(date_lst, date_country_dct):
    '''
    Given a list of string dates in chronological order and a dictionary 
    mapping those dates to pandas dataframes of country mentions, returns
    a dataframe combining each of the individual dataframes with their times.
    '''
    l = []

    for date in date_lst:
        processing_df = date_country_dct[date].copy()
        processing_df['date']= date
        l.append(processing_df)

    country_freq_time_df = pd.concat(l)
    country_freq_time_df.columns = ['country', 'count','news_site','date']
    return country_freq_time_df


def make_country_freq_time_graph(date_lst, date_country_dct, source=''):
    '''
    Given a chronological date list and a date_country_dct as specified in
    previous docstring, and a specification for news source (a string or ''
    for all 4 news sources), returns the plot of dates as x axis and country
    mentions as y axis, for the specified news source's overall top 5 countries
    mentioned in the period of past data collection. 
    '''

    country_freq_time_df = \
    create_total_tbl(date_lst, date_country_dct)

    # No option selected in app
    if source == None:
        return px.line()

    # When we need to filter for specific news source
    if source != "":
        country_freq_time_df = \
        country_freq_time_df[country_freq_time_df["news_site"] == source]

    country_freq_time_df = pd.DataFrame(
        {'Qty_cnt' : country_freq_time_df.groupby(["news_site", "country", "date"])["count"].sum()})\
        .reset_index()

    # Obtain the top 5 countries mentioned by news source and only
    # work with this subset of the data.  
    top_5_lst = \
        list(country_freq_time_df.groupby("country")["Qty_cnt"].count()
             .sort_values(ascending = False).index[:5])

    country_freq_time_df = \
        country_freq_time_df[country_freq_time_df["country"].isin(top_5_lst)]\
        .reset_index()

    country_freq_time_df = country_freq_time_df.drop(columns = "index")
    date_country_dct = \
        pd.DataFrame(country_freq_time_df.groupby(["date"])["country"]
                     .apply(list)).to_dict()

    for dt in date_country_dct["country"].keys():
        for country in top_5_lst:
            if country not in date_country_dct["country"][dt]:
                country_freq_time_df = \
                    country_freq_time_df.append(
                        {'country' : country , 'date' : dt, "Qty_cnt" : 0},\
                        ignore_index = True)

    country_freq_time_df = country_freq_time_df.sort_values("date")
    country_freq_time_df = country_freq_time_df.reset_index()
    country_freq_time_df = country_freq_time_df.drop(columns = "index")

    country_freq_time_fig = \
        px.line(country_freq_time_df, x="date", y="Qty_cnt", color='country')

    # Format plot title. 
    if source == "":
        source_title = 'all sources'
    else:
        source_title= source
    country_freq_time_fig.update_layout(
        autosize=True,
        title="Mentions from {} of its overall top 5 countries"\
        .format(source_title),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(
            family='Monaco',
            size=16,
            color="#1aa3ff"
        ),
        xaxis_rangeslider_visible=True
    )

    return country_freq_time_fig