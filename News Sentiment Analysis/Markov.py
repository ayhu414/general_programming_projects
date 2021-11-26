import math
import Hash_Table
import create_Markov_training

HASH_CELLS = 57

# Purpose of code:
# Use PA5's Markov model to predict which news source a user's input string
# sounds most like. 

class Markov:

    def __init__(self,k,s):

        '''
        Construct a new k-order Markov model using the statistics of string "s"

        Inputs:
            k (int): a value which represents the order of the Markov model
            s (str): a string of text
        '''

        self.k = k
        self.s = s
        self.Hash_Table = self.get_combo_table(self.k, self.s)


    def get_combo_table(self,k,s):

        '''
        Convert the combo_list generated from the generate_combo function
        into a hash table with the key being each k + 1 sequence and the
        value being the frequency of each k + 1 sequence in the combo_list

        Inputs:
            k (int): a value which represents the order of the Markov model
            s (str): a string of text

        Return:
            combo_table (hash table): a hash table with the key being each
            possible k + 1 sequence and the value being the frequency of each
            k + 1 sequence in the combo_list
        '''

        combo_table = Hash_Table.Hash_Table(HASH_CELLS, 0)
        
        combo_list = self.generate_combo(k, s)
        

        freq_dict = {}
        for combo in combo_list:
            if combo in freq_dict:
                freq_dict[combo] += 1
            else:
                freq_dict[combo] = 1

        for name, freq in freq_dict.items():
            combo_table.update(name, freq)

        return combo_table


    def generate_combo(self, k, s):

        '''
        Generate a list of all possible combinations of the k + 1 sequence
        given the order of the Markov model k and the text string s

        Inputs:
            k (int): a value which represents the order of the Markov model
            s (str): a string of text

        Returns:
            combo_list (list): a list of all possible combinations of the 
            k + 1 sequence
        '''

        combo_list = []

        for i in range(len(s)):
            new_list = []
            if i + k < len(s):
                combo_list.append(s[i:i + k + 1])

            else:
                front = s[i - 1:]
                back_index = k + i + 1 - len(s)
                back = s[:back_index]
                combo_list.append(front + back)

        return combo_list


    def log_probability(self,s):

        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.

        Inputs:
            s (str): a string of text

        Return:
            sum_log (float): the log probability of string "s"
        '''

        distinct_list = list(set(self.s))
        s_value = len(distinct_list)

        combo_list = self.generate_combo(self.k, s)
        h_table = self.Hash_Table
        list_of_item = [item for item in h_table.Hash_Table if item != 0]

        sum_log = 0

        for element in combo_list:
            
            m = h_table.lookup(element)
            n = 0
            for item in list_of_item:
                if item != None:
                    if item[0][:-1] == element[:-1]:
                        n += item[1]
            raw_score = (m + 1) / (n + s_value)

            log_score = math.log(raw_score)
            sum_log += log_score

        return sum_log


def identify_speaker(random_string, order=2):

    '''
    Given a user input string, uses Markov models of 
    the training strings collected from past data, 
    each of the specified order, to return a string
    predicting which news source that input string 
    is most similar to.

    Inputs:
        random_string: text from an unidentified source
        order: the order of the character-based Markov model

    Return:
        A string predicting which news source that input 
        string is most similar to.
    '''

    if random_string is None:
        return ''

    string_NBC, string_RT, string_SCMP, string_BBC = \
        create_Markov_training.generate_training_string()

    model1 = Markov(order, string_NBC)
    model2 = Markov(order, string_RT)
    model3 = Markov(order, string_SCMP)
    model4 = Markov(order, string_BBC)

    prob1 = model1.log_probability(random_string)
    prob2 = model2.log_probability(random_string)
    prob3 = model3.log_probability(random_string)
    prob4 = model4.log_probability(random_string)

    prob_list = [prob1, prob2, prob3, prob4]
    max_prob = max(prob_list)

    if max_prob == prob1:
        conclusion = "Your source sounds most like NBC"
    if max_prob == prob2:
        conclusion ="Your source sounds most like RT"
    if max_prob == prob3:
        conclusion = "Your source sounds most like SCMP"
    if max_prob == prob4:
        conclusion = "Your source sounds most like BBC"

    return conclusion


