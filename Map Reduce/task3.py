from mrjob.job import MRJob
from mrjob.step import MRStep
import re

class MRBothYears(MRJob):
    '''
    determines those individuals 
    who have visited the whitehouse
    at least once in both 2009 and 2010
    '''

    def mapper(self, _, line):
        '''
        gets the date of every visit as well as
        the name of the visitor

        Input: line: (str) a line in the csv file
        '''
        entry = line.split(",")
        full_name = (entry[0], entry[1])
        date = re.search(r"\d{4}",str(entry[11]))

        #check if there are missing values in entry
        if date == None:
            yr = ""
        else:
            yr = date.group()

        yield full_name, yr

    def reducer(self, name, yr):
        '''
        summarizes those individuals who have
        visited the white house in both of the years
        2009 and 2010

        Inputs: name: (tuple) full name 
                    of an individual
                yr: (str) the year 
                    which the individual has 
                    visited

        Outputs: name: (tuple) full name 
                    of an individual who
                    satisfies the criteria
        '''
        #notice that all entries only contain
        #years 2009 and 2010, therefore opt 
        #to not iterate over lists to
        #decrease use of iteration
        res = list(set(yr))

        #we notice that all entries only contain
        #years 2009 and 2010, therefore opt 
        #to not iterate over lists to
        #decrease use of iteration
        if len(res) == 2:
            yield name

if __name__ == '__main__':
    MRBothYears.run()