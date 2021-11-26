import pandas as pd
import get_dates

def generate_training_string():

    '''
    Turning the output from the get_past_data function from get_dates to
    four strings associated with the four different news sources respectively

    Return:
    str_NBC, str_RT, str_SCMP, str_BBC: a tuple of four strings associated
        with the four different news sources respectively
    '''

    initial_tuple = get_dates.get_past_data(False)
    total_dict = initial_tuple[1]

    list_of_dict = []
    for key, value in total_dict.items():
        list_of_dict.append(value)
    df = pd.concat(list_of_dict)
    df.columns = ["word", "source"]

    separator = ' '
    df_NBC = df.loc[df["source"] == "NBC"]
    str_NBC = separator.join(df_NBC["word"].tolist())
    df_RT = df.loc[df["source"] == "RT"]
    str_RT = separator.join(df_RT["word"].tolist())
    df_SCMP = df.loc[df["source"] == "SCMP"]
    str_SCMP = separator.join(df_SCMP["word"].tolist())
    df_BBC = df.loc[df["source"] == "BBC"]
    str_BBC = separator.join(df_BBC["word"].tolist())

    return str_NBC, str_RT, str_SCMP, str_BBC

