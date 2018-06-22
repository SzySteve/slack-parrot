users = {}


class User:

    slack_id = ''
    corpus = {}
    """
    corpus is a dict like so:
    word1: {
        rare_word: 1
        common_word: 9
    }   
    """

    def __init__(self, id, message):
        self.slack_id = id
        self.update_corpus(message)

    @staticmethod
    def make_pairs(message):
        for i in range(len(message) - 1):
            yield (message[i], message[i + 1])

    def update_corpus(self, message):
        for pair in self.make_pairs(message):
            first = pair[0]
            second = pair[1]

            if first in self.corpus.keys():
                word_counters = self.corpus[first]
                if second in word_counters.keys:
                    word_counters[second] += 1
                else:
                    word_counters[second] = 1
            else:
                self.corpus[first] = {
                    second: 0
                }
