from mrjob.job import MRJob
from mrjob.step import MRStep
import heapq

class MRTopTen(MRJob):
    '''
    determines the top ten
    most visited host in the Whitehouse
    '''


    def mapper(self, _, line):
        '''
        gets the name of the visitee
        for each entry(visit)

        Input: line: (str) a line in the csv file
        '''

        entry = line.split(",")
        full_name = (entry[19], entry[20])
        yield full_name, 1

    def combiner(self, full_name, counts):
        '''
        combines preliminary results 
        from the nodes

        Inputs: full_name: (tuple) full name 
                    of a Whitehouse host
                counts: (int) the frenquency
                    of visits per entry (1)

        Outputs: full_name: (tuple) full name 
                    of a Whitehouse host
                sum(counts): (int) the total frenquency
                    of visits for a host in a node
        '''

        yield full_name, sum(counts)

    def reducer_init(self):
        '''
        initialize the heapified list
        to keep track of our top 10
        most visted hosts
        '''

        self.lst = [(0,None)]*10
        heapq.heapify(self.lst)

    def reducer(self, full_name, counts):
        '''
        check each host's visited frequency
        and updates top 10 list (lst) with
        the most recent name

        Inputs: full_name: (tuple) full name 
                    of a Whitehouse host
                counts: (int) the frenquency
                    of total visits

        '''
        total = sum(counts)
        min_count = self.lst[0][0]
        if total > min_count:
            heapq.heapreplace(self.lst, (total,full_name))

    def reducer_final(self):
        '''
        reports the final top 10 list
        after all data has been passed through

        Outputs: ele[1]: (str) the name
                    of a Whitehouse host
        '''
        for ele in self.lst:
            yield ele[1]

if __name__ == '__main__':
    MRTopTen.run()

