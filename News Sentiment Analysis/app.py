# For the dash dapp
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# From past work
import CONSTANTS as const
import WebScrapingNewsV6 as web_scraper
import init_figures as init_figs
import app_features
import generate_map as gmp
import generate_countries_plot as gcp
import generate_wordcloud as gwc
import Markov as mk
import nlp

# For wordcloud image processing
import base64

# Purpose of code:
# This is the final dash app, accumulating everything we have done.
# The final dash app, more directly, loads initial figures from 
# init_figures, and gets figures, interactive components like sliders
# from app_features.

# Brief explanation of Dash: 
# It is unneccessary to explain each component of Dash, so this code is 
# lightly commented, but Dash is basically a web app designer that we 
# explored as an alternative to Django. It borrows elements from HTML
# and is part of the plotly data visualization universe.

# The app has two main components: A layout specifying what appears
# on the page, and a reactive component. 
# We can make things reactive (e.g. changing a news source selected
# updates the figure) via app callbacks later in this code. 

# Because the Dash app has many brackets, etc. and nested lines can
# easily extend over 80 characters, we ignore the formatting styles of
# PAs. 
print('YOU MUST CTRL-C IF YOU WANT TO QUIT THE APP.')
print('If you dont, program will quit but server slot is still taken and you cannot re-initialize app.')
print('If you did not CTRL-C to quit, restart the terminal.')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# This app is organized into 4 tabs (dcc.Tab())
# 1) A live scraper that scrapes data live and visualizes it in a country
# mentions map and word cloud.
# 2) A collection of country maps for past scraped data that we saved.
# 3) A collection of wordclouds for past scraped data.
# 4) More advanced and cool features like a Markov model that guesses
# which news source the user's input is most similar to, and a sentiment
# table that tells us whether the tone of the news is positive or negative.

app.layout = html.Div([
    app_features.main_title_div,
    dcc.Tabs([
        dcc.Tab(label='Live scraper', children=[
            html.Div(className='row',children=[
                html.Div(className='six columns',children=[
                    app_features.generate_map_interactive_features(
                        source_selector_id='live_map_source_selector',
                        toggle_switch_id='live_map_settings'),
                    html.Br(),
                    app_features.create_initial_map_box(map_box_id='live_countries_map')
                        ]),
                html.Div(className='six columns', children=[
                    html.Label('Select news source for wordcloud', style={"fontSize":16}),
                    app_features.create_source_selector(source_selector_id='live_wordcloud_source_selector'),
                    html.Br(),
                    app_features.initialize_wordcloud_box(get_live_wordcloud=True,
                                                              wordcloud_img_id='live_wordcloud')
                    ])
                ])
        ]),
        dcc.Tab(label='Past countries scraped', children=[
            html.Div(className='row', children=[
                html.Div(className='six columns', children=[
                    app_features.generate_map_interactive_features(
                        source_selector_id = 'past_map_source_selector',
                        toggle_switch_id='past_map_settings'),
                    app_features.create_initial_map_box(map_box_id=
                                                        'past_countries_map')]),
                html.Div(className='six columns', children=
                    app_features.generate_countries_plot_interactive_features
                    (source_selector_id='past_line_plot_news_source_selector') +
                    [app_features.create_initial_country_plot_box(plot_id='countries_time_plot_box')])
            ])
        ]),
        dcc.Tab(label='Past words scraped', children=[
            html.Label('Select news source for wordcloud', style={"fontSize":16}),
            app_features.create_source_selector(source_selector_id='past_wordcloud_source_selector'),
            html.Br(),
            app_features.create_time_slider(slider_id='past_wordcloud_slider', show_value_with_dcc=True),
            html.Br(),
            app_features.initialize_wordcloud_box(get_live_wordcloud=True,
                                                  wordcloud_img_id='past_wordcloud')
        ]),
        dcc.Tab(label='Advanced tools', children = [
            html.Label('Type in something and I will guess '
                       'which source it comes from using a 2nd-order Markov', style={"fontSize":16}),
            app_features.initialize_word_guesser(guesser_id='word_guesser'),
            app_features.initialize_text_prediction(prediction_id='text_prediction'),
            html.Br(),
            html.Label('Using natural language processing, I tell you whether a news source feels positive or negative on that day', style={"fontSize":16}),
            app_features.create_source_selector(source_selector_id='sentiment_source'),
            html.Label("Use scrollbar right of table to navigate",style={"fontSize":16}),
            app_features.initialize_sentiment_table_box(table_id='sentiment_table')
        ]),
    ])
])

# We can make things reactive (e.g. changing a news source selected
# updates the figure) via app callbacks.
# We have to identify each callback we want and then write a function that
# processes the callback. The callback must contain Outputs and Inputs of 
# interactive Dash components (e.g. an input past date slider and an 
# output past map). For each output and input, we must specify the id of the
# feature and the attribute we want to modify.

# Note: Apparently, callback functions must be written in same file as 
# the Dash app, so there is no way around putting all the callbacks
# in another file. 

@app.callback(Output('live_countries_map', 'figure'),
    [Input('live_map_source_selector', 'value'),
     Input('live_map_settings', 'value')])

def update_live_map(news_source, map_display):
    '''
    Given a news_source value from the source selector
    and a preference for map display as globe or flat,
    updates the live map. 
    '''

    new_live_countries_df, new_live_time_stamp \
        = web_scraper.convert_to_pandas(const.list_of_links, return_country_df=True)

    new_live_map = gmp.create_plotly_map(new_live_countries_df, new_live_time_stamp,
                                         news_source=news_source, globe_style=map_display)
    return new_live_map


@app.callback(Output('past_countries_map', 'figure'),
    [Input('past_map_source_selector', 'value'),
     Input('past_map_settings', 'value'),
     Input('past_map_slider','value')])

def update_past_map(news_source, map_display, past_time_stamp_index):
    '''
    Same idea as update_live_map, but now also takes in an index specifying
    the date in the list of sorted past dates that we want to generate the
    map for. Updates the past map. 
    '''

    past_time_stamp = init_figs.sorted_times[past_time_stamp_index]
    updated_past_countries_df = init_figs.times_to_countries_dfs[past_time_stamp]
    updated_past_map = \
        gmp.create_plotly_map(updated_past_countries_df, past_time_stamp,
            news_source=news_source, globe_style=map_display)

    return updated_past_map


@app.callback(Output('countries_time_plot_box', 'figure'),
    [Input('past_line_plot_news_source_selector', 'value')])

def update_countries_plot(news_source):
    '''
    Given a news source to select, updates the plot of dates to past 
    country mentions to show the plot for that news source. 
    '''

    updated_countries_plot = \
        gcp.make_country_freq_time_graph(init_figs.sorted_times, 
            init_figs.times_to_countries_dfs, source=news_source)
    
    return updated_countries_plot


@app.callback(Output('live_wordcloud', 'src'),
    [Input('live_wordcloud_source_selector', 'value')])

def update_live_wordcloud(news_source):
    '''
    Given a news source, scrapes for that news source's headline
    words then updates a wordcloud of those words to visualize
    the live scraped data. 
    '''

    live_scraped_words_df, live_time_stamp \
        = web_scraper.convert_to_pandas(const.list_of_links, return_country_df=False)
    gwc.export_wordcloud_to_png(live_scraped_words_df, news_source, current_words=True)
    wordcloud_png = './live_scraped_wordcloud.png'
    wordcloud_base64 = base64.b64encode(open(wordcloud_png, 'rb').read()).decode('ascii')
    src = 'data:image/png;base64,{}'.format(wordcloud_base64)

    # The src is a technical base64 component allowing us to update the wordcloud image.
    return src


@app.callback(Output('past_wordcloud', 'src'),
    [Input('past_wordcloud_source_selector', 'value'),
     Input('past_wordcloud_slider','value')])

def update_past_wordcloud(news_source, past_time_stamp_index):
    '''
    Same as update_live_wordcloud, but now also takes in an index
    specifying which date in the list of sorted past dates we want
    to visualize the wordcloud for. 
    '''

    past_time_stamp = init_figs.sorted_times[past_time_stamp_index]
    updated_past_words_df = init_figs.times_to_words_dfs[past_time_stamp]
    gwc.export_wordcloud_to_png(updated_past_words_df, news_source, current_words=False)
    wordcloud_png = './past_scraped_wordcloud.png'
    wordcloud_base64 = base64.b64encode(open(wordcloud_png, 'rb').read()).decode('ascii')
    src = 'data:image/png;base64,{}'.format(wordcloud_base64)

    return src


@app.callback(Output('text_prediction', 'children'),
    [Input('word_guesser', 'value')])

def update_guesser_input(word_input):
    '''
    Given a user string input in the text input component,
    uses a 2-order Markov model to guess which news source
    the user input is most similar to. Then, updates the 
    output div with the guess as a string. 
    '''

    markov_conclusion = mk.identify_speaker(word_input, order=2)

    return markov_conclusion


@app.callback(Output('sentiment_table', 'figure'),
    [Input('sentiment_source', 'value')])

def update_sentiment_table(news_source):
    '''
    Given a news source, updates the sentiment table of dates to
    news sentiment (does the news feel positive or negative) to
    reflect that news source.  
    '''

    updated_table = nlp.generate_sentiment_plotly_table(news_source=news_source)

    return updated_table


if __name__ == '__main__':
    app.run_server(debug=True)
