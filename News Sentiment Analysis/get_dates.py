import subprocess
import os
import glob
import pandas as pd
import datetime


def RUN():
    pulling = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    output = pulling.communicate()[0]


def get_past_data(get_country_times=True):
    '''
    directly run and return a dictionary of time to dataframe
    if True, then returns country dictionary
    if False, then returns a word dictonary
    '''
    os.chdir(r"/home/student/cs122-word-freq-project/scraped_csvs")

    countries_times = glob.glob('countries*')
    word_times = glob.glob('words*')

    countries_times_tup = list(map(lambda x: [x, None], countries_times))
    word_times_tup = list(map(lambda x: [x, None], word_times))
    # print(countries_times_tup)
    # print(word_times_tup)
    date_time_lst = []

    for psud_tup in countries_times_tup:
        psud_tup[1] = pd.read_csv(psud_tup[0], header=None)

    for psud_tup in word_times_tup:
        psud_tup[1] = pd.read_csv(psud_tup[0], header=None)

    countries_times_mod = list(
        map(lambda x: (x[0].replace('countries', '').replace(' ', '_')[:-10], x[1]), countries_times_tup))
    word_times_mod = list(map(lambda x: (x[0].replace('words', '').replace(' ', '_')[:-10], x[1]), word_times_tup))

    date_times = list(map(lambda x: x[0], countries_times_mod))
    date_times.sort(key = lambda x: datetime.datetime.strptime(x, "%Y-%m-%d_%H:%M"))
    #print(date_times)

    #print(countries_times_mod[4:])

    os.chdir(r"/home/student/cs122-word-freq-project")

    countries_times_dict = dict(countries_times_mod)
    word_times_dict = dict(word_times_mod)


    # print(countries_times_dict)
    # print(word_times_dict)
    if get_country_times:
        return date_times, countries_times_dict
    else:
        return date_times, word_times_dict


'''
    print(word_times)
    print(countries_times)

    countries_times_mod = list(map(lambda x: x.replace('countries', '').replace(' ','_')[:-4], countries_times))
    word_times_mod = list(map(lambda x: x.replace('words', '').replace(' ','_')[:-4], countries_times))

    print(countries_times_dict)
    print(word_times_dict)
'''

