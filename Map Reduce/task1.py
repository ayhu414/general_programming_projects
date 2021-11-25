from mrjob.job import MRJob


class MRTenTimes(MRJob):
    '''
    determines individuals who have visited
    the whitehouse at least 10 times
    '''

    def mapper(self, _, line):
        '''
        Gets the total number of visits within node

        Input: line: (str) a line in the csv file
        '''

        entry = line.split(",")
        full_name = (entry[0], entry[1])
        yield full_name, 1

    def combiner(self, full_name, counts):
        '''
        Gets counts of different nodes and combines them
        together, eases the load on reducer

        Inputs: full_name: (tuple) full name 
                    of a visitor
                counts: (int) the frenquency
                    of visits per entry (1)

        Outputs: full_name: (tuple) full name 
                    of a visitor
                sum(counts): (int) the total frenquency
                    of visits
        '''

        yield full_name, sum(counts)

    def reducer(self, full_name, counts):
        '''
        Summarizes the data by summing up all instances
        of visits, and reporting names of those who have 
        over 10 visits

        Inputs: full_name: (tuple) full name 
                    of a visitor
                counts: (int) the frenquency
                    of visits per entry (1)

        Outputs: full_name: (tuple) full name 
                    of a visitor that has visited
                    over 10 times
        '''

        total = sum(counts)
        if total >= 10:
            yield full_name

if __name__ == '__main__':
    MRTenTimes.run()
