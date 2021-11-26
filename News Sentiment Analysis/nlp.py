import nltk
from nltk.corpus import movie_reviews
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
import random
import bs4
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import get_dates as gd
import pandas as pd
import praw as pr
import math
import numpy as np
import datetime
import pickle
import plotly.graph_objects as go

def get_sentiment(save_csv=False, train_and_save=False, news_source='', live_scraping="EMPTY"):
    '''
    Function to train a naive bayes model and analyze the overall sentiment of the headlines.
    Specifically, if the user wishes to train and save a model, the function will access the
    reddit API and retrive headlines from major news subreddits, whcih will
    constitute our training data.
    Later, the training data will be classified using
    NLTK's vader SIA as a first classification of the reddit news articles, which we call
    the classifying set.
    Then the features of the classifying set will be used to both train and analyze our
    naive bayes classifier.
    This classifier will then be stored as a pickle with its corresponding features, which
    can be later extracted to determine the sentiments of news headlines without retraining
    

    Inputs:
        save_csv(bool): whether or not to save reddit headline data (used if API fails)
        train_and_save(bool): whether or not to train a naive bayes model and save
            the model along with its corresponding set of features
        news_source(str): the name of the news source to analyze sentiments, '' returns
            the sentiment analysis for all four sources in the past
        live_scraping(pandas DataFrame): if the user ever wishes to analyze a live-scraped 
            dataframe. if "EMPTY", then conduct analysis on all past data, if not "EMPTY",
            and a dataframe was imported, the it directly analyzes the dataframe (this 
            effectively makes the news_source parameter insignificant)
        
    Output:
        ret_df(pandas DataFrame): a dataframe containing columns date and sentiment which
            shows the sentiment estimation of a speciic news source on a specific day. If 
            live scraping, the sentiment estimation of that specific news source that instant.
    '''

    if train_and_save:

        sia = SIA()
        results = []

        headlines = reddit(train_and_save)
        #gets the headlines from reddit to construct categorical data
        #matching words to a positive or negative sentiment

        for line in headlines:
            pol_score = sia.polarity_scores(line)
            pol_score['headline'] = line
            results.append(pol_score)

        cols = ['headline', 'compound', 'pos', 'neg', 'neu']
        df = pd.DataFrame.from_records(results)[cols]

        df['categ'] = 0
        df.loc[df['compound'] > 0.2, 'categ'] = 1
        df.loc[df['compound'] < -0.2, 'categ'] = -1
        #creates the dataframe which categorizes the headlines 
        #into positive or negative 

        if save_csv:
            csv_name = "training_data{}.csv".format(str(datetime.datetime.now())[:-10].replace(" ", "_"))
            df.to_csv(r'/home/student/cs122-word-freq-project/training_data/' + str(csv_name), index=False)
            #INCASE API FAILS, this saves reddit data just in case API fails

        all_lst = df.iloc[:, 0].tolist()
        clean_all = []
        for headline in all_lst:
            clean_all += processing_tokens(headline)
            #lemmatizing and tokenizing headlines for analysis

        random.shuffle(clean_all)
        #randomize our data to minimize the impact of data organization on
        #our final results

        all_frq = nltk.FreqDist(clean_all)
        word_features = list(all_frq)[:1500]

        pos_lst = list(df[df['categ'] == 1].headline)
        neg_lst = list(df[df['categ'] == -1].headline)

        pos_lst = list(map(lambda x: (processing_tokens(x), 'pos'), pos_lst))
        neg_lst = list(map(lambda x: (processing_tokens(x), 'neg'), neg_lst))
        documents = pos_lst + neg_lst
        random.shuffle(documents)
        #randomize our data to minimize the impact of data organization on
        #our final results

        featuresets = [(doc_features(d, word_features), c) for (d, c) in documents]

        train_set, test_set = featuresets[100:], featuresets[:100]
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        #create the classifier model using naive bayes distribution
        
        saved_classifer = open("classifier.pickle", "wb")
        pickle.dump(classifier, saved_classifer)
        saved_classifer.close()

        saved_features = open("features.pickle", "wb")
        pickle.dump(word_features, saved_features)
        saved_features.close()
        #save the model and its feature correspondence for future use

    else:

        classifier_f = open("classifier.pickle", 'rb')
        classifier = pickle.load(classifier_f)
        classifier_f.close()

        features_f = open("features.pickle", 'rb')
        word_features = pickle.load(features_f)
        features_f.close()
        #retreive the saved model and its feature correspondence 

    ordering, data = gd.get_past_data(False)

    if live_scraping is "EMPTY":
        classification_lst = []
        for date, df in data.items():
            daily_info = classifying_headlines(date, df, classifier, word_features, news_source)
            classification_lst.append((date, daily_info))
            classification = dict(classification_lst)
            #create the classification for live_scraped data

    else:
        date = str(datetime.datetime.now())[:-10].replace(" ", "_")
        classification = classifying_headlines(date, live_scraping, classifier, word_features, news_source)
        #create classification for all past data

    ret_df = to_df(ordering, classification)

    return ret_df


def generate_sentiment_plotly_table(news_source=''):
    '''
    Given a particular news source, get the plotly table correspondence

    Input: news_source(str): a news source in question.
    Output: table(plotly table): directly generates a plotly table in web app
    '''
    if news_source is None:
        table = go.Figure()
        return table

    sentiment_df = get_sentiment(save_csv = False, train_and_save=False,news_source=news_source)
    table = go.Figure(data=[go.Table(
        header=dict(values=list(sentiment_df.columns),
                    fill_color="#1aa3ff",
                    font=dict(color='white'),
                    align='center'),
        cells=dict(values=[sentiment_df['date'], sentiment_df['sentiment']],
                   fill_color='lavender',
                   font_size=18,
                   height=30,
                   align='center'))
    ])

    if news_source is None:
        news_source_name = "None"
    elif news_source == '':
        news_source_name = 'all 4 sources'
    else:
        news_source_name = news_source


    table.update_layout(
        autosize=True,
        title="Sentiment of {}".format(news_source_name),
        font=dict(
            family='Monaco',
            size=16,
            color="#1aa3ff"
        )
    )

    return table


def to_df(ordering, data):
    '''
    given a correct ordering of dates as well as a dictionary of sentiments
    return a pandas dataframe with the corresponding to the inputs

    Inputs: ordering(lst): a list of dates in the correct order
            data(dict): a dictionary containing date to sentiment data
    Outputs: df(pandas DataFrame) a pandas dataframe containing all date 
            and sentiments 
    '''
    sentiment_order = []
    for date in ordering:
        sentiment_order.append(data[date])
    df = pd.DataFrame(list(zip(ordering, sentiment_order)), columns=["date", "sentiment"])

    return df



def df_manipu(df, news_source):
    '''
    given a designated news_source, prune the dataframe
    to match the desired news source.

    Input:  df(pandas DataFrame): a pandas dataframe with
            words and news_source 
            news_source(str): a string which denotes the
            desired news_source
    '''
    df.columns = ['word', 'news_source']
    if news_source != "All sources":
        df = df[df['news_source'] == news_source]

    return df


def classifying_headlines(date, word_df, classifier, word_features, news_source):
    '''
    classify the current dataframe of words to news source

    Input:  date(str): string which encodes the date which we are analyzing
            word_df(pandas DataFrame): a pandas dataframe with
            words and news_source 
            word_features: 
    '''
    word_df = df_manipu(word_df, news_source)

    current_tokens = word_df.iloc[:, 0].tolist()
    processing_tokens(current_tokens, False)

    curr_features = doc_features(current_tokens, word_features)

    classification = classifier.classify(curr_features)

    return classification


def reddit(train_and_save):
    '''
    using reddit's PRAW API, access subreddits to find the most 
    featured words within designated sub-reddits. This will constitute
    what words will be included in the sentiment analysis of our own 
    news headline data

    Input: train_and_save(bool): a boolean determining whether or not
            to train and save data. If not, then the this function will not
            access sub-reddits, saving time when running the program.

    Output: headlines(list): a list of strings which correspond the the
            title of the most viral posts on the particular sub-reddits
    '''
    reddit = pr.Reddit(client_id='mjKYOVGPTg1tUQ',
                       client_secret='ZQYXjepTZ71UNGWnxAZMy-Cj364',
                       user_agent='akatyusha')

    headlines = set()

    if train_and_save:
        for submit in reddit.get_subreddit('worldnews').get_hot(limit=None):
            headlines.add(submit.title)
        for submit in reddit.get_subreddit('news').get_hot(limit=None):
            headlines.add(submit.title)
        for submit in reddit.get_subreddit('unitedkingdom').get_hot(limit=None):
            headlines.add(submit.title)
        for submit in reddit.get_subreddit('usanews').get_hot(limit=None):
            headlines.add(submit.title)
        for submit in reddit.get_subreddit('China').get_hot(limit=None):
            headlines.add(submit.title)

    return headlines


def find_lemmatize_corresp(wn_tag):
    '''
    given a word POS tag, find its wordnet correspondence

    Input: wn_tag(str): a POS tag of a word

    Output: wordnet.???(str): a word net tag corresponding
            to the POS tag ("" if it cannot find it)
    '''
    if wn_tag.startswith('J'):
        return wordnet.ADJ
    elif wn_tag.startswith('V'):
        return wordnet.VERB
    elif wn_tag.startswith('N'):
        return wordnet.NOUN
    elif wn_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ""


def processing_tokens(headline, tokenize_needed=True):
    '''
    lemmatize tokens to ensure that words of the same
    vein do not split the overall count of said word

    Inputs: headline(str): a string corresponding to a headline,
            or pre-tokenized headline
            tokenize_needed(bool): determine whether or not 
            to tokenize the headline

    Output: lemma_tokens(list): a list of lemmatized tokens
    '''
    lemma = nltk.stem.wordnet.WordNetLemmatizer()
    stop_words = stopwords.words('english')

    if tokenize_needed:
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(headline)
    else:
        tokens = headline

    word_and_pos = nltk.pos_tag(tokens)
    word_and_pos = list(map(lambda x: (x[0], find_lemmatize_corresp(x[1])), word_and_pos))
    lemma_tokens = []

    for word, pos in word_and_pos:
        if pos is not "" and not word in stop_words:
            lemma_tokens.append(lemma.lemmatize(word, pos=pos).lower())
        elif not word in stop_words:
            lemma_tokens.append(lemma.lemmatize(word).lower())

    return lemma_tokens


def doc_features(doc, word_features):
    '''
    returns a dictionary mapping words in features whether or not the word
    appears in the given document

    Input:  doc(lst): a list containing all words appeared within a 
            set of headlines
            word_features(lst): a list containing all featured words
            recieved from reddit
    '''
    document_words = set(doc)

    features = {}

    for word in word_features:
        features['contains({})'.format(word)] = (word in document_words)

    return features


