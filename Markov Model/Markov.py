# CS122 W'20: Markov models and hash tables
# Allen (Yixin) Hu

import sys
import math
import Hash_Table

HASH_CELLS = 57

class Markov:

    def __init__(self,k,s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"

        Input:  k(int): integer denoting the kth-order of the Markov model
                s(str): string containing speech of a known candidate,
                        used for 'training' our model for comparions later
        '''

        self.mkv_hash = Hash_Table.Hash_Table(HASH_CELLS, 0)
        self.training_str = s
        self.order = k

    def get_counts(self):
        '''
        Having initialized the Markov object, construct the k and k+1 tokens 
        and place them into our hash table with 'token: frequency' pairings

        Input: N/A [Inplace Modification of Hash Table]
        Output: N/A [Inplace Modification of Hash Table]
        '''

        length_str = len(self.training_str)

        for i in range(length_str):
            front_cut = i - self.order
            if front_cut < 0:
                first_half = self.training_str[length_str + front_cut:]
                last_half_full = self.training_str[:i + 1]
                last_half_partial = self.training_str[:i]

                final_key_full = first_half + last_half_full
                final_key_partial = first_half + last_half_partial

            else:
                final_key_full = self.training_str[front_cut:i+1]
                final_key_partial = self.training_str[front_cut:i]

            val_full = self.mkv_hash.lookup(final_key_full)
            self.mkv_hash.update(final_key_full, val_full + 1)

            val_k = self.mkv_hash.lookup(final_key_partial)
            self.mkv_hash.update(final_key_partial, val_k + 1)

    def log_probability(self,s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.

        Input: s(str):  string containing a speech from an unknown source,
                        used to calculate similarities with current model

        Output: agg_log_prob(float):  float value containing all the aggregate
                                      log probabilities as overall probability
                                      of a match.
        '''

        length_test = len(s)
        S_val = len(set(self.training_str))
        agg_log_prob = 0

        for i in range(length_test):
            front_cut = i - self.order
            if front_cut < 0:
                first_half = s[length_test + front_cut:]
                last_half = s[:i + 1]
                final_key = first_half + last_half
            else:
                final_key = s[front_cut:i+1]

            N_val = self.mkv_hash.lookup(final_key[:self.order])
            M_val = self.mkv_hash.lookup(final_key)

            prob_val = math.log(((M_val + 1) / (N_val + S_val)))

            agg_log_prob += prob_val

        return agg_log_prob

def identify_speaker(speech1, speech2, speech3, order):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the speakers
    uttering that text under a "order" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.

    Input:  Speech1(str), Speech2(str): contains speeches known from two 
                                        individuals which sets up the model
            Speech3(str): contains a speech from unknown source which
                          the function will attempt to attribute the speaker
            order(int): indicates the kth-order Markov model

    Output: (speaker_likelihood_1, speaker_likelihood_2, "*")(tuple):
                a tuple containing the likelihood of each speaker
                and the final decision of the algorithm. "*" will
                be replaced by "A"/"B"/"A or B" to indicate 
                the final decision
    '''

    speaker_model_1 = Markov(order,speech1)
    speaker_model_2 = Markov(order,speech2)

    speaker_model_1.get_counts()
    speaker_model_2.get_counts()

    length_unknown = len(speech3)

    speaker_likelihood_1 = (speaker_model_1.log_probability(speech3) 
                                / length_unknown)
    speaker_likelihood_2 = (speaker_model_2.log_probability(speech3) 
                                / length_unknown)

    if speaker_likelihood_1 > speaker_likelihood_2:
        return (speaker_likelihood_1, speaker_likelihood_2, "A")
    if speaker_likelihood_1 < speaker_likelihood_2:
        return (speaker_likelihood_1, speaker_likelihood_2, "B")
    else:
        return (speaker_likelihood_1, speaker_likelihood_2, "A or B")


def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''
    (likelihood1, likelihood2, conclusion) = res_tuple
    
    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


if __name__=="__main__":
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)
    
    with open(sys.argv[1], "rU") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "rU") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "rU") as file3:
        speech3 = file3.read()

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)

