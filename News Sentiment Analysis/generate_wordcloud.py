from wordcloud import WordCloud, STOPWORDS # wordcloud generating app
import matplotlib.pyplot as plt
import WebScrapingNewsV6 as web_scraper
import CONSTANTS as const
import plotly.tools as tls

# Purpose of this code:
# Generate word clouds for the words scraped from news headlines.

def generate_wordcloud(word_df, news_source):
    '''
    Given a dataframe of words to news sources and a specification
    of which news_source to examine in that dataframe (string or '' for 
    all 4 sources), returns a wordcloud object representing those words.
    '''
    # We do not want to modify the word_df itself since it may be used by
    # other python scripts. 
    processing_df = word_df.copy()
    processing_df.columns = ['word', 'news_source']

    # Return placeholder wordcloud if no source is selected in app. 
    if news_source is None:
        return WordCloud().generate('placeholder')
    if news_source == '':
        word_df_filtered_by_source = processing_df
    else:
        word_df_filtered_by_source = \
        processing_df[processing_df['news_source'] == news_source]
    word_list = list(word_df_filtered_by_source['word'])

    # The wordcloud package takes in a single string to generate
    # a wordcloud.
    concat_text = ' '.join(word_list)
    wordcloud = \
    WordCloud(max_font_size=50, max_words=300, width=700,\
        height=500, background_color='white').generate(concat_text)

    return wordcloud


def export_wordcloud_to_png(word_df, news_source, current_words):
    '''
    Given a words_df and news_source as described in previous function,
    and a boolean parameter specifying whether we are doing a live scrape
    (current_words=True) or past scrape, exports the created wordcloud to 
    a png format.

    The reason we have to export the wordcloud to png is because the wordcloud
    is matplotlib, which does not integrate well with the Dash application that
    is part of the plotly universe. We have to add the wordcloud into
    Dash as a png image. Whenever we update a wordcloud, this function
    will get called and the png file will be updated. We then insert the 
    wordcloud as the png into the Dash app. 
    '''
    wordcloud = generate_wordcloud(word_df, news_source)
    if current_words:
        wordcloud.to_file("live_scraped_wordcloud.png")
    else:
        wordcloud.to_file("past_scraped_wordcloud.png")
