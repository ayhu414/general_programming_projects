# CS122 W'20: Markov models and hash tables
# Allen (Yixin) Hu


TOO_FULL = 0.5
GROWTH_RATIO = 2


class Hash_Table:

    def __init__(self,cells,defval):
        '''
        Construct a new hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted

        Input:  cells(int): number of cells the hash table will start with
                defval(int): a default value which
                             the user will choose to use as to
                             not raise key errors in the hash table
        '''

        self.hash_table = [defval] * cells
        self.defval = defval
        self.cnt = 0

    def gen_hash(self, input_key):
        '''
        Computes a hash value for a given input using a hashing alogrithm

        Input: input_key(str): the key which user wishes to hash

        Output: hash_val(int): a hash value specific to the input_key
        '''
        hash_val = 0
        for letter in input_key:
            hash_val = ((hash_val * 37) + ord(letter)) % len(self.hash_table)

        return hash_val 

    def linear_probing(self, input_key):
        '''
        If the specific cell is filled, linear probe the table to find
        the next empty cell and return the hash value which allows 
        the user to act upon that cell. Also used in looking up a 
        specific cell using a key value

        Input: input_key(str): the key which user wishes to retreive

        Output: final_hash(int): the valid hash value which allows
                                 the user to act upon the cell
        '''
        final_hash = self.gen_hash(input_key)
        begin = final_hash

        while (self.hash_table[final_hash] != self.defval 
                    and self.hash_table[final_hash][0] != input_key):
            final_hash += 1
            if final_hash > len(self.hash_table) - 1:
                final_hash = 0
            if final_hash == begin:
                self.rehashing()

        return final_hash

    def rehashing(self):
        '''
        If the table exceeds the TOO_FULL value, constructs a larger hash
        table by the GROWTH_RATIO term, and migrate previous data into
        the new hash table

        Input: N/A [Inplace Modification of Hash Table]
        Output: N/A [Inplace Modification of Hash Table]

        '''

        migrated_table = [self.defval] * (len(self.hash_table) * GROWTH_RATIO)
        curr_items = []
        for item in self.hash_table:
            if item != self.defval:
                curr_items.append(item)

        self.hash_table = migrated_table

        for key, val in curr_items:
            self.update(key, val)


    def lookup(self, key):
        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.

        Input: key(str): a string containing the desired key (i.e. first
                         entry of the tuple)

        Output: If key is found:
                    self.hash_table[idx][1](value): the value stored in the
                    (key, val) tuple within the hash table. 
                If key does not exist:
                    self.defval(int): the default value of the hash table
        '''

        idx = self.linear_probing(key)
        if self.hash_table[idx] != self.defval:
            return self.hash_table[idx][1]
        else:
            return self.defval


    def update(self,key,val):
        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table, insert it 
        coupled with value "val" in a (key, val) tuple

        Input:  key(immutable): an immutable type to serve as the key
                               for the tuple for lookup purposes
                val(*): any value the user wish to store within the
                        second entry of the tuple.
        '''
        begin_idx = self.linear_probing(key)

        if self.hash_table[begin_idx] == self.defval:
            self.cnt += 1
            curr_ratio = (1 - self.cnt) / len(self.hash_table)
            if curr_ratio > TOO_FULL:
                self.cnt = 0
                self.rehashing()
                
        self.hash_table[begin_idx] = (key, val)

    def __repr__(self):
        return str(self.hash_table)
