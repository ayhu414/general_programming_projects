TOO_FULL = 0.5
GROWTH_RATIO = 2


class Hash_Table:

    def __init__(self,cells,defval):

        '''
        Construct a new hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted

        Inputs:
            cells (int): the number of cells that the hash table has

            defval (int): the default value that will be returned upon 
            a lookup to a key that has not previously been inserted

            Hash_Table (hash table): initialize a new hash table with a fixed
            number of cells equal to the parameter "cells" (each entry is 
            initialized to be None)
        '''

        self.cells = cells
        self.defval = defval
        self.Hash_Table = [None] * cells


    def create_table(self, key):

        '''
        Create the standard string hashing function discussed
        in class (the one that repeatedly multiplies by 37, etc.)

        Inputs:
            key (string): the string of the text that we will use

        Returns:
            hash_value (int): the hash value of the corresponding key
        '''

        hash_value = 0
        for letter in key:
            hash_value = (hash_value * 37 + ord(letter)) % len(self.Hash_Table)

        return hash_value


    def lookup(self,key):

        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.

        Inputs:
            key (string): the string of the text that we will use

        Returns:
            1) If it has previously been inserted:
            self.Hash_Table[index][1] (int): the value associated with the 
            specified key in the hash table

            2) If it has not previously been inserted:
            self.defval (int): the default value that will be returned 
            upon a lookup to a key that has not previously been inserted
        '''

        index = self.create_table(key)

        if self.Hash_Table[index] == None:
            return self.defval
        else:
            if self.Hash_Table[index][0] == key:
                return self.Hash_Table[index][1]
            while self.Hash_Table[index][0] != key:
                if index < len(self.Hash_Table) - 1:
                    index += 1
                else:
                    index = 0
                if self.Hash_Table[index] == None:
                    return self.defval
                elif self.Hash_Table[index][0] == key:
                    return self.Hash_Table[index][1]


    def update(self,key,val):

        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table,  insert it with
        value "val".

        Inputs:
            key (string): the string of the text that we will use
            val (int): the value associated with the specified key
        '''

        key_list = [item[0] for item in self.Hash_Table if item != None]

        if key not in key_list:
            self.Hash_Table = self.hashing(key, val, self.Hash_Table)
            if len(key_list) >= TOO_FULL * len(self.Hash_Table):
                item_list = [item for item in self.Hash_Table if item != None]
                new_table = [None] * len(self.Hash_Table) * GROWTH_RATIO
                for item in item_list:
                    self.Hash_Table = self.hashing(item[0], item[1], new_table)

        else:
            for item in self.Hash_Table:
                if item != None:
                    if item[0] == key:
                        self.Hash_Table[self.Hash_Table.index(item)] = (key, val)


    def hashing(self, key, val, table):

        '''
        Complete the linear probing implementation

        Inputs:
            key (string): the string of the text that we will use
            val (int): the value associated with the specified key
            table (hash table): a hash table
        '''

        index = self.create_table(key)
        while table[index] != None:
            if index < len(table) - 1:
                index += 1
            else:
                index = 0
        table[index] = (key, val)

        return table