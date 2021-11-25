# CS122: Course Search Engine Part 1
#
# Allen Hu, Nicholas Thom
#

import re
import util
import bs4
import queue
import json
import sys
import csv

INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet'])

def url_unpack(url):
    '''
    Process the url into a bs4 soup_object and retrieves
    the request URL in order to generate absolute URLs.
    Notice that we account for the possibility of encountering
    a non-viable request object, which is thrown by the exception.

    Inputs:
        url: (String) a string indicating the url

    Outputs:
        soup: (Soup Object) the vanilla soup object ready to parse through
        rec_url: (String) an unabridged URL of the requested link
    '''
    requested = util.get_request(url)
    try:
        html = util.read_request(requested)
        soup = bs4.BeautifulSoup(html, "html5lib")
        rec_url = util.get_request_url(requested)
        return soup, rec_url
    except:
        print("Error in url_unpack")
        return None

def finding_all_words(tag, get_code = False):

    '''
    This function finds relevant information from a given course
    description. Specifically, the function takes in a div tag 
    of a course object and retrieves the course description,
    and if the user inclines, the course code as well.

    Inputs: tag: (bs4 Tag Object) this is a specific div tag
                object of a given course.
            get_code: (Boolean) this tells whether or not
                the function should retreive the course code

    Outputs: refined_list: (List) this is a list of all the
                relevant words within a course's description
            [OPTIONAL] course_code: (String) the
                course code of this given course
    '''

    title_tag = tag.find("p", class_="courseblocktitle")
    desc_tag = tag.find("p", class_="courseblockdesc")
    if title_tag == None:
        title_tag == ""
    if desc_tag == None:
        desc_tag == ""
    full_text = title_tag.text + desc_tag.text
    if get_code:
        course_code_obj = re.search(r"\b^[A-Z]{4}\s[0-9]{5}\b", full_text)
        course_code = course_code_obj.group().replace(u"\xa0", " ")
    #The if statement above retrieves the course code 
    lower_full_text = full_text.lower()
    text_to_list = re.findall(r"\b[a-z][a-z0-9]*\b",lower_full_text)
    refined_list = [word for word in text_to_list if word not in INDEX_IGNORE]
    if get_code:
        return refined_list, course_code
    else:
        return refined_list

def parsing_soup_div(soup, map_name):
    '''
    Retreives an index as a dictionary of course_id to list of 
    relevant words in said course. Notice that if the course
    is in a sequence, then the words within the overarching 
    description will be given to each of the subsequent courses

    Inputs:
        soup: (bs4 Soup Object) the soup object generated from
                our URL from our url_analysis function
        map_name: (String) the name of our mapping from
                of course codes to proper course id

    Outputs:
        index: (Dictionary) gives mapping between the course_id 
                to list of relevant words 
    '''

    with open(map_name) as f:
        data = json.load(f)

    try:
        cbm_tags = soup.find_all("div", class_="courseblock main")

        index = {}

        for tag in cbm_tags:
            seq = util.find_sequence(tag)
            if seq == []:
                ref_lst, course_code = finding_all_words(tag, True)
                course_id = data[course_code]
                if course_id not in index.keys():
                    index[course_id] = ref_lst
            #The code above handles the case where there is a sequence            
            else:
                upper_lst = finding_all_words(tag, False)
                for subcourse in seq:
                    lower_lst, course_code = finding_all_words(subcourse, True)
                    lower_lst += upper_lst
                    course_id = data[course_code]
                    if course_id not in index.keys():
                        index[course_id] = lower_lst
            #The code above handles the case where there is a stand-alone            

        return index

    except:
        print("Error in parsing_soup_div")
        return None

def find_links(soup, abs_url, link_history):
    '''
    Finds all links within a webpage and adds them to a list of links
    after they have been 'cleaned up' by removing fragments 
    and converting relative to absolute links. Notice that it adds 
    links if and only if it has not already been documented

    Inputs: soup: (bs4 Soup Object) the soup object generated from
                    our request object
            abs_url: (String) the url of the current webpage, used
                    to form the absolute URL equivalents of relevant URLs
            link_history: (Set) a set of links that have been documented
                    so that no link is visted twice

    Outputs: lst_of_links: (List of strings) a list of ready-to-go links
                    which will be placed into the queue
            link_history: (Set) the updated version of the links that
                    have already been documented
    ''' 

    try:
        a_tags = soup.find_all("a")
        lst_of_links = []

        for tag in a_tags:
            if tag.has_attr('href'):            
                raw_link = util.remove_fragment(tag['href'])
                ref_link = util.convert_if_relative_url(abs_url, raw_link)
                if util.is_url_ok_to_follow(ref_link, 
                    limiting_domain = "classes.cs.uchicago.edu") and (
                    ref_link not in link_history):
                        lst_of_links.append(ref_link)
                        link_history.add(ref_link)     
        return lst_of_links, link_history
    except:
        print("Error in generating link class")

def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generate a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping of
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index
    '''
    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"
    cnt = 0
    full_index = {}
    links_q = queue.Queue()
    links_q.put(starting_url)
    history = set([starting_url])
    while cnt < num_pages_to_crawl and not links_q.empty():
        curr_soup, req_lk = url_unpack(links_q.get())
        new_index = parsing_soup_div(curr_soup, course_map_filename)
        new_links, history = find_links(curr_soup, req_lk, history)
        if new_links != None:
            for link in new_links:
                links_q.put(link)
                history.add(link)
        full_index.update(new_index)
        cnt += 1
    #The code above goes through each link in the queue,
    # and stops if either the counts are maxed out
    # or that the queue has been exhausted

    inverted_index = {}
    for course_id, lst_words in full_index.items():
        for word in lst_words:
            if word not in inverted_index.keys():
                inverted_index[word] = []
            if course_id not in inverted_index[word]:
                inverted_index[word].append(course_id)
    #The code above reconfigures our index to a
    # word to course id mapping ready to be 
    # exported to a csv

    csv_file = open(index_filename, 'w')
    csv_writer = csv.writer(csv_file, delimiter = '|')
    for word, course_lst in sorted(inverted_index.items()):
        for course_id in course_lst:
            csv_writer.writerow([course_id, word])
    #The code above places each entry of our inverted index
    # into our csv file in question

    csv_file.close()    

if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_pages_to_crawl, course_map_filename, index_filename)
