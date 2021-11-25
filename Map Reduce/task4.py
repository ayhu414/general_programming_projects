from mrjob.job import MRJob
from mrjob.step import MRStep

class MRVisitorVisitee(MRJob):
    '''
    Determines individuals who have

    both been visitors and visitees
    '''

    def mapper(self, _, line):
        '''
        for every entry of data,
        get the visitor and visitee

        Input: line: (str) a line in the csv file
        '''
        entry = line.split(",")
        visitor = (entry[0],entry[1])
        visitee = (entry[19],entry[20])

        yield visitor, "visitor"
        yield visitee, "visitee"

    def reducer(self, name, position):
        '''
        for each individual, check
        if they have been a visitor
        as well as a visitee

        Inputs: name: (tuple) full name 
                    of an individual
                position: (str) the positions 
                    which the individual has 
                    been visitor or visitee

        Outputs: name: (tuple) full name 
                    of an individual
        '''

        res = list(set(position))
        #there are only two positions
        if len(res) == 2:
            yield name

if __name__ == "__main__":
    MRVisitorVisitee.run()
