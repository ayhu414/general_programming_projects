import pandas as pd
import plotly.express as px
import CONSTANTS as const

# Purpose of code: To create a function that 
# generates a plotly map of countries mentioned
# to frequencies of mentions for given news source

def initialize_alpha_codes(alpha_csv):
    '''
    Given a csv of 2 and 3 letter country codes, returns a 
    pandas dataframe version of those country codes. 

    Motivation: The GeoText packaged used to identify country
    mentions runs on 2 letter country codes, but the plotly map
    uses 3 letter codes to determine countries' positions on maps.
    '''
    alpha_codes = pd.read_csv(alpha_csv)\
        .rename(columns={'English short name lower case':"country_name",
                         'Alpha-2 code':'alpha_2','Alpha-3 code':'alpha_3'})
    alpha_2_and_3 = alpha_codes[['country_name','alpha_2','alpha_3']]
    
    return alpha_2_and_3


def process_country_freq(scraped_countries_df, news_source=''):
    '''
    Given a raw scraped_countries dataframe and a 
    desired news source string (specified in CONSTANTS file)
    which may be all 4 sources (news_source=''), returns a dataframe
    of country name, country alpha 3 code, and frequency of mentions
    of country.
    '''
    alpha_2_and_3 = initialize_alpha_codes(const.ALPHA_CSV)
    processing_df = scraped_countries_df.copy()
    processing_df.columns = \
        ['alpha_2', 'country_freq','news_source']
    if news_source == '':
        # Want all 4 sources, so need for filtering.
        country_freq_source_raw = processing_df
    else:
        country_freq_source_raw = \
            processing_df[processing_df['news_source'] == news_source]

    country_freq_source_alpha_3 = \
        country_freq_source_raw.merge(
            alpha_2_and_3, on='alpha_2', how = 'inner')\
            .drop(columns=['alpha_2'])

    # Count country frequencies using pandas manipulations, eventually
    # returning a final polished dataframe. 
    country_to_freq_df = \
        country_freq_source_alpha_3.groupby('alpha_3').sum().reset_index()
    country_to_freq_df = \
        country_to_freq_df.merge(alpha_2_and_3, how='left', on='alpha_3')
    country_to_freq_df = \
        country_to_freq_df[['country_name', 'alpha_3', 'country_freq']]

    return country_to_freq_df


def create_plotly_map(scraped_countries_df, time_stamp, \
    news_source='', globe_style=True):
    '''
    Given a scraped_countries_df generated by the web scraper, a 
    time stamp at which the data was collected, a string specifying news
    source, and a preference for map layout (globe or flat), returns
    a plotly map object of the country frequencies.
    '''
    country_to_freq = process_country_freq(scraped_countries_df, news_source)
    country_map = px.choropleth(country_to_freq, locations="alpha_3",
                                color="country_freq",
                                hover_name="country_name",
                                color_continuous_scale='YlGnBu',
                                labels={'country_freq':'Number of mentions',
                                        "alpha_3": 'Country code'})
    if news_source == '':
        news_source_name = 'all sources'
    else:
        news_source_name = news_source
    if globe_style:
        country_map.update_geos(projection_type="orthographic")
    country_map.update_layout(
        autosize=True,
        title="Mentions from {}, {}".format(news_source_name, time_stamp),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor= 'rgba(0, 0, 0, 0)',
        font=dict(
            family='Monaco',
            size=16,
            color="#1aa3ff"
        )
    )

    return country_map