# CS122: Linking restaurant records in Zagat and Fodor's data sets
#
# Allen (Yixin) Hu


import numpy as np
import pandas as pd
import jellyfish
import util

REST_COL_NAMES = ["idx_num","restaruant_name","city","address"]
COMP_COL_NAMES = ["zagat","fodors"]

def make_tups():

    '''
    Make all possible tuples of jw categories

    OUTPUT: (set) a set of all possible tuples
    '''

    l = []
    lst = ['low','medium','high']
    for item in lst:
        for item_2 in lst:
            for item_3 in lst:
                l.append((item, item_2, item_3))

    return set(l)

def import_csv(csv_file_name, col_names):
    '''
    Takes a CSV and returns a pd dataframe of said csv
    which contains 1) index, 2) restaruant name
                    3) city 4) address within city

    INPUT:  csv_file_name (String) -> name of desired csv
            col_names (list) -> list of name column names

    OUTPUT: df (Pandas Dataframe) -> dataframe of desired csv
    '''

    df = pd.read_csv(csv_file_name, names = col_names, header = None)

    return df

def generate_matches_df(df_1, df_2, known_lnk):

    '''
    Given two dataframs, create a random unmatched dataframe to train data

    INPUT:  df_1 (Pandas Dataframe) -> dataframe of restaurant
            df_2 (Pandas Dataframe) -> dataframe of restaurant
            known_lnk (Pandas Dataframe) -> dataframe of known links

    OUTPUT: final_unmatch (Pandas Dataframe) -> dataframe of
                                                matched restaurants
    '''

    final_merge = known_lnk.merge(df_1, how = "left", 
                                left_on = "zagat", right_on = "idx_num", 
                                suffixes = ("_zgt","_fdr"))
    final_merge = final_merge.merge(df_2, how = "left", 
                                left_on = "fodors", right_on = "idx_num", 
                                suffixes = ("_zgt","_fdr"))
    final_merge = final_merge.drop(
                                columns = ["zagat","fodors",
                                            "idx_num_zgt","idx_num_fdr"])

    return final_merge

def generate_unmatches_df(df_1, df_2):

    '''
    Given two dataframs, create a random unmatched dataframe to train data

    INPUT:  df_1 (Pandas Dataframe) -> dataframe of restaurant
            df_2 (Pandas Dataframe) -> dataframe of restaurant

    OUTPUT: final_unmatch (Pandas Dataframe) -> dataframe of unmatched restaurants
    '''

    zgt_random = df_1.sample(
            1000, replace = True, random_state = 1234).reset_index().drop(
            columns = ["idx_num","index"])
    fdr_random = df_2.sample(
            1000, replace = True, random_state = 5678).reset_index().drop(
            columns = ["idx_num","index"])

    final_unmatch = zgt_random.join(
            fdr_random, how = "outer", 
            lsuffix = "_zgt", rsuffix = "_fdr", sort = False)

    return final_unmatch

def generate_pct_from_df(df):
    '''
    Given a df, return a dictionary of counts of each type of match
    TUPLE ORDER: (name_category,city_categ, address_categ)

    INPUT: df (Pandas Dataframe) -> dataframe of restaurant

    OUTPUT: counts_dict (Dictionary) -> dictionary containing 
                frequencies of tuples
    '''
    counts_dict = dict.fromkeys(make_tups(), 0)

    for index, row in df.iterrows():
        loc_name_score = jellyfish.jaro_winkler(
                row['restaruant_name_zgt'], row['restaruant_name_fdr'])
        name_categ = util.get_jw_category(loc_name_score)
        loc_city_score = jellyfish.jaro_winkler(
                row['city_zgt'], row['city_fdr'])
        city_categ = util.get_jw_category(loc_city_score)
        loc_address_score = jellyfish.jaro_winkler(
                row['address_zgt'], row['address_fdr'])
        address_categ = util.get_jw_category(loc_address_score)

        counts_dict[tuple([name_categ, city_categ, address_categ])] += 1

    total_count = len(df.index)

    for key, value in counts_dict.items():
        counts_dict[key] = value / total_count

    return counts_dict

def step1_assign_zero_to_possible(categ_dict, dict_1, dict_2):
    '''
    assigns zeros in both dicts to the category possible_tuples in category dict

    INPUT:  categ_dict (Dictionary) -> a dictionary containing which
                has keys of tuple categories and tuple values
            dict_1 (Pandas Dataframe) -> a dataframe of restaurants
            dict_1 (Pandas Dataframe) -> a dataframe of restaurants

    OUTPUT: <INPLACE MODIFICATION> updates the "possible_tuples" key
                in the categ_dict dictionary
    '''
    for tup, val in dict_1.items():
        if (val == 0 and dict_2[tup] == 0):
            categ_dict["possible_tuples"].append(tup)

def step2_sorting_ratios(categ_dict, matches_dict, unmatches_dict):

    '''
    Find the tuples to put into unmatches

    INPUT:  categ_dict (Dictionary) -> a dictionary containing which
                has keys of tuple categories and tuple values
            matches_dict (Dictionary) -> dictionary containing 
                tuples which map to relative frequency
            unmatches_dict (Dictionary) -> dictionary containing 
                tuples which map to relative frequency

    OUTPUT: ret_lst (List) -> list of sorted tuples
    '''

    ret_lst = []

    # step one, let all unmatch 0s be in the front of our sorted list

    for tup, val in unmatches_dict.items():
        if (val == 0 and tup not in categ_dict["possible_tuples"]):
            ret_lst.append(tup)

    ratios = {} 

    # step two, sort the ratios

    for tup, val in unmatches_dict.items():
        if (tup not in ret_lst and tup not in categ_dict["possible_tuples"]):
            ratios[tup] = matches_dict[tup] / val

    sort = sorted(ratios.items(), key = lambda x: -x[1])

    for key_val in sort:
        ret_lst.append(key_val[0])

    return ret_lst

def step3_finding_best(categ_dict, unmatches_dict, rnk_lst, mu):

    '''
    Find the tuples to put into unmatches

    INPUT:  categ_dict (Dictionary) -> a dictionary containing which
                has keys of tuple categories and tuple values
            unmatches_dict (Dictionary) -> dictionary containing 
                tuples which map to relative frequency
            rnk_lst (List) -> list of sorted tuples
            mu (Int) -> the cutoff value for finding
                match tuples

    OUTPUT: categ_dict (Dictionary) -> updated category dictionary
            idx (Int) -> index of the tuple which stopped
    '''

    agg = 0
    idx = 0

    for i, item in enumerate(rnk_lst):
        agg += unmatches_dict[item]
        if agg <= mu:
            categ_dict["match_tuples"].append(item)
            idx = i
        else:
            break

    return categ_dict, idx

def step4_finding_worst(categ_dict, matches_dict, 
                            rnk_lst, lambda_, lwr_bound):

    '''
    Find the tuples to put into unmatches

    INPUT:  categ_dict (Dictionary) -> a dictionary containing which
                has keys of tuple categories and tuple values
            matches_dict (Dictionary) -> dictionary containing 
                tuples which map to relative frequency
            rnk_lst (List) -> list of sorted tuples
            lambda_ (Int) -> the cutoff value for finding
                unmatch tuples
            lwr_bound (Int) -> index of the best matches 
                to prevent cross-overs

    OUTPUT: categ_dict (Dictionary) -> updated category dictionary
            idx (Int) -> index of the tuple which stopped

    '''

    agg = 0
    idx = 0

    for i, item in enumerate(rnk_lst[:lwr_bound:-1]):
        agg += matches_dict[item]
        if agg <= lambda_:
            categ_dict["unmatch_tuples"].append(item)
            idx = i
        else:
            break

    return categ_dict, idx

def step5_assign_remains(categ_dict, rnk_lst, idx_best, idx_worst):

    '''
    Assign all categorized tuples into possible tuples

    INPUT:  categ_dict (Dictionary) -> a dictionary containing which
                has keys of tuple categories and tuple values
            rnk_lst (List) -> list of sorted tuples
            idx_best (Int) -> index of the furthest matches
            idx_worst (Int) -> index of the furthest unmatches

    OUTPUT: <INPLACE MODIFICATION> Append uncategorized tuples to 
                the "possible_tuples" key of categ_dict dictionary
    '''

    if idx_best < idx_worst:
        categ_dict["possible_tuples"] + rnk_lst[idx_best + 1:idx_worst]


def determine_matches(df_1, df_2, categ_dict, block_on_city = False):

    '''
    Take in two dataframes and generate three dataframes. 
    Specifically, it will return a matches, possible, and unmaches dataframe.
    
    INPUT:  df_1 (Pandas Dataframe) -> a raw dataframe of restaurants
            df_2 (Pandas Dataframe) -> a raw dataframe on restaurants
            categ_dict (Dictionary) -> a dictionary containing which
                has keys of tuple categories and tuple values
            block_on_city (Boolean) -> whether or not to limit 
                selections to same city
            
    '''
    storage = set()

    zgt_match = []
    fdr_match = []
    zgt_possible = []
    fdr_possible = []
    zgt_unmatch = []
    fdr_unmatch = []

    for idx1, row1 in df_1.iterrows():
        for idx2, row2 in df_2.iterrows():
            if (not block_on_city) or (
                        block_on_city and row1["city"] == row2["city"]):
                loc_name_score = jellyfish.jaro_winkler(
                        row1['restaruant_name'], row2['restaruant_name'])
                name_categ = util.get_jw_category(loc_name_score)
                loc_city_score = jellyfish.jaro_winkler(
                        row1['city'], row2['city'])
                city_categ = util.get_jw_category(loc_city_score)
                loc_address_score = jellyfish.jaro_winkler(
                        row1['address'], row2['address'])
                address_categ = util.get_jw_category(loc_address_score)

                #^generate all possible jw categories for a given row

                categ_tup = (name_categ, city_categ, address_categ)
                idx_tup = (idx1, idx2)
                storage.add((categ_tup,idx_tup))

                #^store a tuple of (category, tuple of the given rows' indices)  

            else:
                break

    for item in storage:
        if item[0] in categ_dict["match_tuples"]:
            zgt_match.append(item[1][0])
            fdr_match.append(item[1][1])

        if item[0] in categ_dict["possible_tuples"]:
            zgt_possible.append(item[1][0])
            fdr_possible.append(item[1][1])

        if item[0] in categ_dict["unmatch_tuples"]:
            zgt_unmatch.append(item[1][0])
            fdr_unmatch.append(item[1][1])

        #^unpack index tuples to respective lists in order to extract rows from dfs
    
    matched_zgt_df = df_1.iloc[zgt_match].reset_index().drop(
                                                columns = ["idx_num","index"])
    matched_fdr_df = df_2.iloc[fdr_match].reset_index().drop(
                                                columns = ["idx_num","index"])
    possible_zgt_df = df_1.iloc[zgt_possible].reset_index().drop(
                                                columns = ["idx_num","index"])
    possible_fdr_df = df_2.iloc[fdr_possible].reset_index().drop(
                                                columns = ["idx_num","index"])
    unmatched_zgt_df = df_1.iloc[zgt_unmatch].reset_index().drop(
                                                columns = ["idx_num","index"])
    unmatched_fdr_df = df_2.iloc[fdr_unmatch].reset_index().drop(
                                                columns = ["idx_num","index"])

    matched_df = matched_zgt_df.join(matched_fdr_df, 
            how = "left", lsuffix = "_zgt", rsuffix = "_fdr", sort = False)
    possible_df = possible_zgt_df.join(possible_fdr_df, 
            how = "left", lsuffix = "_zgt", rsuffix = "_fdr", sort = False)
    unmatched_df = unmatched_zgt_df.join(unmatched_fdr_df, 
            how = "left", lsuffix = "_zgt", rsuffix = "_fdr", sort = False)

    return matched_df, possible_df, unmatched_df

def find_matches(mu, lambda_, block_on_city=False):
    '''
    given a mu and lambda, return dataframs of match, possible
    and unmatched dataframes

    INPUT:  mu (Int) -> the cutoff value for finding
                match tuples
            lambda_ (Int) -> the cutoff value for finding
                unmatch tuples
            block_on_city (Boolean) -> determine whether
                or not to block on city
    '''
    counts_dict = {}

    zagat = import_csv("zagat.csv",REST_COL_NAMES)
    fodors = import_csv("fodors.csv",REST_COL_NAMES)
    matches = import_csv("known_links.csv",COMP_COL_NAMES)

    #^get all dfs ready

    matched_df = generate_matches_df(zagat, fodors, matches)
    unmatched_df = generate_unmatches_df(zagat,fodors)

    #^get all matches, and unmatches dfs

    unmatched_pct_dict = generate_pct_from_df(unmatched_df)
    matched_pct_dict = generate_pct_from_df(matched_df)

    #^get all relative frequencies

    categ_dict = {"match_tuples": [], 
                    "possible_tuples": [], 
                    "unmatch_tuples": []}

    step1_assign_zero_to_possible(categ_dict, 
            matched_pct_dict, unmatched_pct_dict)
    ranked_lst = step2_sorting_ratios(
            categ_dict, matched_pct_dict, unmatched_pct_dict)
    categ_dict, idx_match = step3_finding_best(
            categ_dict, unmatched_pct_dict, ranked_lst, mu)
    categ_dict, idx_unmatch = step4_finding_worst(
            categ_dict, matched_pct_dict, ranked_lst, lambda_, idx_match)
    step5_assign_remains(categ_dict, ranked_lst, idx_match, idx_unmatch)

    #^determine the tuples which will go into categories

    matched_df, possible_df, unmatched_df = determine_matches(
            zagat, fodors, categ_dict, block_on_city)

    return matched_df, possible_df, unmatched_df
    
if __name__ == '__main__':
    matches, possibles, unmatches = \
        find_matches(0.005, 0.005, block_on_city=False)

    print("Found {} matches, {} possible matches, and {} "
          "unmatches with no blocking.".format(matches.shape[0],
                                               possibles.shape[0],
                                               unmatches.shape[0]))
