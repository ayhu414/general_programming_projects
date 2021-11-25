### CS122, Winter 2020: Course search engine: search
###
### Allen (Yixin) Hu, Nicholas Thom

from math import radians, cos, sin, asin, sqrt
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')

INPT_TO_OTPT = {"terms":["dept","course_num","title"],"dept":["dept",
                            "course_num","title"],
                    "day":["dept","course_num","section_num","day",
                            "time_start","time_end"],
                    "time_start":["dept","course_num","section_num","day",
                            "time_start","time_end"],
                    "time_end":["dept","course_num","section_num","day",
                            "time_start","time_end"],
                    "walking_time":["dept","course_num","section_num","day",
                            "time_start","time_end","building","walking_time"],
                    "building":["dept","course_num","section_num","day",
                            "time_start","time_end","building","walking_time"],
                    "enroll_lower":["dept","course_num","section_num","day",
                            "time_start","time_end","enrollment"],
                    "enroll_upper":["dept","course_num","section_num","day",
                            "time_start","time_end","enrollment"]}

TABLES_TO_PK = {("catalog_index","courses"):"course_id",
                ("courses","sections"):"course_id",
                ('sections',"meeting_patterns"):"meeting_pattern_id",
                ('sections',"gps"):"building_code"}

ITEMS_TO_TABLE = {"terms":"catalog_index","dept":"courses",
                "course_num":"courses","section_num":"sections",
                "day":"meeting_patterns","time_start":"meeting_patterns",
                "time_end":"meeting_patterns",
                "building":"gps","walking_time":"gps",
                "enroll_lower":"sections","enroll_upper":"sections",
                "enrollment":"sections","title":"courses", "word":"catalog_index"}

CORRECT_ORDER_RETURN = ["dept", "course_num", "section_num", "day", "time_start",
                "time_end", "building", "walking_time", "enrollment", "title"]

CORRECT_ORDER_QUERY = ["terms","dept","day","time_start",
                        "time_end","walking_time","building",
                        "enroll_lower","enroll_upper"]

CORRECT_ORDER_TABLE = ["catalog_index", "courses", 
                        "sections", "meeting_patterns", "gps"]

def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day a list with variable number of elements
           -> ["'MWF'", "'TR'", etc.]
      - time_start an integer in the range 0-2359
      - time_end an integer in the range 0-2359
      - walking_time an integer
      - enroll_lower an integer
      - enroll_upper an integer
      - building a string
      - terms a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''

    if args_from_ui == {}:
        return ([],[])
    
    otpt_lst, table_lst = find_req_otpt_and_table(args_from_ui)
    db = sqlite3.connect(DATABASE_FILENAME)
    db.create_function("compute_time_between", 4, compute_time_between)
    c = db.cursor()

    select_clause = create_select_clause(otpt_lst)
    from_join_clause = create_join_clause(table_lst)
    where_clause = create_where_clause(otpt_lst, args_from_ui, table_lst)

    query = select_clause + from_join_clause + where_clause
    params = construct_params(otpt_lst, args_from_ui)

    r = c.execute(query, params)
    lst_entries = r.fetchall()
    lst_headers = get_header(c)
    db.close()

    if lst_entries == []:
        return ([], [])
    else:
        return (lst_headers, lst_entries)

########### auxiliary functions #################
########### do not change this code #############

                    
def find_req_otpt_and_table(user_inpt):

    '''
    Find the required outputs given the keys of user inputs

    INPUT: user_inpt: (dict) A dictionary object holding the user's
            desired inputs

    OUTPUT: otpt_lst: (list) The required info that needs to be returned
            table_lst: (list) The tables needed to conduct the query
    '''

    raw_otpt_lst = []
    raw_table_lst = []


    if 'terms' in user_inpt.keys():
        raw_table_lst.append("catalog_index")

    for key in user_inpt.keys():
        raw_otpt_lst += (INPT_TO_OTPT[key])
    otpt_set = set(raw_otpt_lst)
    otpt_lst = correct_order_given_list(CORRECT_ORDER_RETURN, otpt_set)

    for otpt in otpt_lst:
        raw_table_lst.append(ITEMS_TO_TABLE[otpt])
    table_set = set(raw_table_lst)
    table_lst = correct_order_given_list(CORRECT_ORDER_TABLE, table_set)

    return otpt_lst, table_lst

def correct_order_given_list(reference, ref_set):
    '''
    Given a particular set, order that set according to the 
        desired ordering

    INPUT:  reference: (list) A list holding the items in question
            in the correct order
            ref_set: (set) An unordered set containing all pertinent
            items to sort into the desired order

    OUTPUT: correct_lst: (list) A list holding the elements in the 
            set in the desired order
    '''

    correct_lst = []

    for item in reference:
        if item in ref_set:
            correct_lst.append(item)

    return correct_lst

def retreive_pk(table_1, table_2):
    '''
    [HELPER FUNCTION]
    Given two tables, get their primary keys

    INPUT: table_1, table_2: (str) Names of tables 

    OUTPUT: val: (str) the desired primary key between
            the two tables

    NOTICE: it returns ERROR if the paring does not exist
    '''
    table_pair = (table_1,table_2)
    for key, val in TABLES_TO_PK.items():
        if table_pair == key:
            return val
    return "ERROR"

def create_join_clause(lst_tables):

    '''
    Creates FROM-JOIN clause given a list of tables

    INPUT: lst_tables: (lst) a list of tables needed for
            conducting queries

    OUTPUT: final_str: (str) a string in the format of a 
            sql FROM clause
    '''


    temp_lst = []
    on = ""
    local_tables = list(lst_tables)



    if len(local_tables) > 1:
        on = " ON "      

    for i in range(1, len(local_tables)):
        if local_tables[i] != "gps":
            table_1 = local_tables[i-1]
            table_2 = local_tables[i]
            pk = retreive_pk(table_1,table_2)
            local_str = table_1 + "." + pk + " = " + table_2 + "." + pk
            temp_lst.append(local_str)

    if "gps" in lst_tables:
        local_tables += ['gps AS dest']
        temp_lst += ['sections.building_code = final']

    tables_str = " JOIN ".join(local_tables)
    on_str = " AND ".join(temp_lst)

    final_str = tables_str + on + on_str

    return "FROM " + final_str + " "

def create_select_clause(lst_otpt):
    '''
    Creates select clause given a list of desired outputs

    INPUT:  lst_otpt: (list) a list containing all the necessary
            outputs given a user input


    OUTPUT: final_str: (str) a string in the form of a sql
            SELECT clause
    '''

    temp_lst = []
    for item in lst_otpt:
        if item != "walking_time" and item != "building":
            local_str = ITEMS_TO_TABLE[item] + "." + item
        elif item == "walking_time":
            local_str = ("compute_time_between(gps.lon, "
                            "gps.lat, dest.lon, dest.lat) AS walking_time")
        elif item == "building":
            local_str = "dest.building_code AS final"
        temp_lst.append(local_str)

    final_str = ", ".join(temp_lst)

    return 'SELECT ' + final_str + " "

def create_where_clause(lst_otpt, user_inpt, lst_tables):
    '''
    Given a user's inputs, construct the where clauses for
        recieving the user's filters 

    INPUT:  lst_otpt: (list) a list containing all the necessary
            outputs given a user input
            lst_tables: (lst) a list of tables needed for
            conducting queries
            user_inpt: (dict) the dictionary containing the user's desired
            inputs

    OUTPUT: final_str: (str) a string in the form of a sql WHERE clause

    '''
    
    temp_lst = []
    str_group_by = ""

    for item in CORRECT_ORDER_QUERY:
        if item in user_inpt.keys():
            if item == "dept":
                local_str = "(" + ITEMS_TO_TABLE[item] + "." + item + " = ?)"
            if item == "enroll_lower":
                local_str = ("(" + ITEMS_TO_TABLE[item] + 
                                "." + "enrollment" + " >= ?)")
            if item == "enroll_upper":
                local_str = ("(" + ITEMS_TO_TABLE[item] + 
                                "." + "enrollment" + " <= ?)")
            if item == "time_start":
                local_str = "(" + ITEMS_TO_TABLE[item] + "." + item + " >= ?)"
            if item == "time_end":
                local_str = "(" + ITEMS_TO_TABLE[item] + "." + item + " <= ?)"
            if item == "walking_time":
                local_str = ("walking_time <= ? ")
            if item == "building":
                local_str = ("gps.building_code = ? ")
            if item == "day":
                count = len(user_inpt["day"])
                local_str = "(" + create_multiple_entry(count, item) + ")"
            if item == "terms":
                count = len(user_inpt[item].split())
                local_str = "(" + create_multiple_entry(count, item) + ")"
                str_group_by = create_group_by("sections" in lst_tables, count)
            temp_lst.append(local_str)

    final_str = " AND ".join(temp_lst)
    
    return "WHERE " + final_str + str_group_by + ";"

def create_group_by(do_sections, count):
    '''
    [HELPER FUNCTION]
    Create a group by function if we need to count the number of occurences 
    of a particular course

    INPUT: do_sections: (bool) if true, generates a statement with sections
            count: (int) the count of terms inputed by the user

    OUTPUT: (str) the sql group by statement
    '''

    if do_sections:
        return " GROUP BY sections.section_id HAVING COUNT(*) = " + str(count)
    else:
        return " GROUP BY courses.course_id HAVING COUNT(*) = " + str(count)

def create_multiple_entry(count, item):
    '''
    [HELPER FUNCTION]
    Create a portion of the WHERE clause when multiple entries are required

    INPUT:  count: (int) the count of terms inputed by the user
            item: (str) the desired variable 
                that will be needed to conduct queries

    OUTPUT: local_str: (str) The string prepared to recieve user queries
    '''

    temp_lst = []

    if item == "terms":
        item = "word"

    for i in range(count):
        temp_str = ITEMS_TO_TABLE[item] + "." + item + " = ?"
        temp_lst.append(temp_str)
    
    local_str = " OR ".join(temp_lst)

    return local_str

def construct_params(lst_otpt, user_inpt):
    '''
    Given the user's inputs, construct parameters to conduct queries

    INPUT: lst_otpt: (list) The list containing desired outputs
            user_inpt: (dict) the dictionary containing user's
            entries for the query

    OUTPUT: temp_tup: (tuple) the tuple containing all user's inputs
            in order to conduct queries
    '''

    temp_tup = tuple()

    for item in CORRECT_ORDER_QUERY:
        if item in user_inpt.keys():
            if item == "dept":
               temp_tup += (user_inpt["dept"],)
            if item == "day":
                for pattern in user_inpt["day"]:
                    temp_tup += (pattern,)
            if item == "time_start":
                temp_tup += (user_inpt[item],)
            if item == "time_end":
                temp_tup += (user_inpt[item],)
            if item == "building":
                temp_tup += (user_inpt[item],)
            if item == "walking_time" :
                temp_tup += (user_inpt[item],)
            if item == "enroll_lower":
                temp_tup += (user_inpt[item],)
            if item == "enroll_upper":
                temp_tup += (user_inpt[item],)
            if item == "terms":
                terms_lst = user_inpt[item].split()
                for term in terms_lst:
                    temp_tup += (term,)

    return temp_tup

def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i, _ in enumerate(s):
        if s[i] == ".":
            s = s[i + 1:]
            break

    return s


########### some sample inputs #################

EXAMPLE_0 = {"time_start": 930,
             "time_end": 1500,
             "day": ["MWF"]}

EXAMPLE_1 = {"dept": "CMSC",
             "day": ["MWF", "TR"],
             "time_start": 1030,
             "time_end": 1500,
             "enroll_lower": 20,
             "terms": "computer science"}
