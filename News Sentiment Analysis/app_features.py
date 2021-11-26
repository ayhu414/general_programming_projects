import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
import CONSTANTS as const
import init_figures as init_figs
import base64
import nlp

# Purpose of code:
# Generate key features of Dash app, including interactive sliders, dropdowns, etc.
# and figure boxes for maps, wordclouds, tables. 
# The idea is that all of this could be directly written into the Dash app, 
# but that would make the app very unreadable.

# A bit of background:
# Dash has various objects for different things like radio buttons, dropdowns, graph
# boxes etc. Each of these has different attributes, but most Dash objects have an
# id attribute we could set to identify that specific Dash object. 

# Dash app's main title
main_title_div = \
    html.Div(style={'color': '#1aa3ff', "font-family": "Monaco"},
             children=
             [html.H1('News Headline Analyzer', style={'textAlign': 'center'}),
              html.H4('New sources: BBC, NBC, SCMP, RT', style={'textAlign': 'center'}),
              html.H4('By Calvin, Allen, Nick, Charles', style={'textAlign': 'center'})]
             )

def create_source_selector(source_selector_id):
  '''
  Given a source_selector_id for the dropdown object,
  returns the dropdown object. 
  '''

  source_selector = dcc.Dropdown(id=source_selector_id,
    options=const.news_options, value='',
    style={'width': '50%'}, multi=False)

  return source_selector


def create_time_slider(slider_id, show_value_with_dcc=False):
  '''
  Given a slider_id for the time slider object,
  returns the time_slider object, whether that is in the
  more minimalistic daq slider or the dcc slider with full 
  labels.  
  '''
  if not show_value_with_dcc:
        time_slider = daq.Slider(
          id=slider_id,
          min=0, max=len(init_figs.sorted_times) - 1,
          value=0, step=1,
          size=600)
  else:
        time_slider = dcc.Slider(
          id=slider_id,
          min=0, max=len(init_figs.sorted_times) - 1,
          marks={index : time_stamp for index, time_stamp in enumerate(init_figs.sorted_times)},
          value=0, step=1)

  return time_slider


def create_initial_country_plot_box(plot_id):
  '''
  Given a plot_id for the country mentions frequency plot
  over dates, returns a dcc.Graph() object allowing us 
  to put the plot plot in Dash. 
  '''

  plot_box = dcc.Graph(id=plot_id,
    figure=init_figs.countries_time_plot,
    style = {'height':'800px', 'width':'800px'})
  
  return plot_box


def generate_countries_plot_interactive_features(source_selector_id):
  '''
  Given an id for a source_selector, returns a full list of objects
  used to interact with the country mentions frequencies plot.
  '''

  countries_plot_features = \
    [html.Label("Select news sources using drag down, "
                "dates using slider below graph, and "
                "countries using legend in graph",
                style={'fontSize': 16}),
    create_source_selector(source_selector_id),
    html.Br()]

  return countries_plot_features


def generate_map_interactive_features(source_selector_id, toggle_switch_id):
  '''
  Given ids for a source_selector and toggle_switch (flat/globe map),
  returns a div of all the objects used to interact with the country mentions
  map.
  '''

  # These are the interactive features needed by both live scraped and past
  # maps. 
  interactive_features =  \
    [html.Label('Select news source for map', style={"fontSize":16}),
      create_source_selector(source_selector_id),
    html.Label('Flat / globe map', style={"fontSize":16}),
    daq.ToggleSwitch(id=toggle_switch_id, value=True,
                    style={'width': '9%', "fontSize":20})]

  # If we are generating interactive features for past maps, we also need
  #  a time slider to navigate the different past dates.
  if source_selector_id.startswith('past') and toggle_switch_id.startswith('past'):
    interactive_features += \
      [html.Br(),
      html.Label('Select date', style={"fontSize": 16}),
      create_time_slider(slider_id='past_map_slider')]

  map_interactive_features = \
      html.Div(children=interactive_features)

  return map_interactive_features


def create_initial_map_box(map_box_id):
  '''
  Given a map box id, returns the initial map for either 
  live or past data in a dcc.Loading() object (loading
  animation). 
  '''

  if map_box_id.startswith('live'):
      initial_map = init_figs.live_countries_map
  else:
    initial_map = init_figs.earliest_countries_map

  map_box = \
    dcc.Loading(children=[dcc.Graph(id=map_box_id,figure=initial_map)],
     type='cube')
  return map_box


def initialize_wordcloud_box(get_live_wordcloud, wordcloud_img_id):
  '''
  Given a parameter of whether we are live scraping a wordcloud or
  creating a wordcloud on past data, and an id for the html.Img() 
  component to store the wordcloud in, returns the image box
  for the Wordcloud that we could integrate into the Dash app. 
  '''
  if get_live_wordcloud:
      wordcloud_png_path= './live_scraped_wordcloud.png'
  else:
      wordcloud_png_path= './past_scraped_wordcloud.png'

  # Base64 encoding needed for proper conversion of wordcloud as image. 
  wordcloud_base64 = base64.b64encode(open(wordcloud_png_path, 'rb').read()).decode('ascii')
  wordcloud_image_box = dcc.Loading(children=[
    html.Img(id=wordcloud_img_id,
      src='data:image/png;base64,{}'.format(wordcloud_base64))],
    type='cube')


  return wordcloud_image_box


def initialize_word_guesser(guesser_id):
  '''
  Given an ID for a text input slot in the Dash app, returns
  a text input object we use as user's input string to
  predict which news soruce that input sounds most like.
  '''
  word_guesser = \
  dcc.Input(id=guesser_id, type="text",
    placeholder="Type something and I'll tell you which source it sounds like most",
    debounce=True, style={'width':'70%'})

  return word_guesser


def initialize_text_prediction(prediction_id):
  '''
  Given an ID for the news source prediction to the the input text 
  in previous function, returns an html.Div() for the news
  source prediction. This Div is empty at first, but will
  be updated later reactively by user input in the Dash app. 
  '''
  prediction = \
  html.Div(id=prediction_id,
    style={'fontFamily': 'Monaco',
    'fontSize': 25,
    'color': "#1aa3ff"})
  
  return prediction


def initialize_sentiment_table_box(table_id):
  '''
  Given a table_id, initializes the natural language processing
  table that maps, for a given news source (initialized as all),
  the past dates at which we collected the news source and
  whether if that news source was overall positive or negative
  news at that date. 
  '''
  
  initial_table = nlp.generate_sentiment_plotly_table(news_source='')
  table_box = dcc.Loading(children=
    [dcc.Graph(id=table_id, figure=initial_table)], type='cube')
  
  return table_box