import random

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
        message = message.split()
        for pair in self.make_pairs(message):
            first = pair[0]
            second = pair[1]

            if first in self.corpus.keys():
                word_counters = self.corpus[first]
                if second in word_counters.keys():
                    word_counters[second] += 1
                else:
                    word_counters[second] = 1
            else:
                self.corpus[first] = {
                    second: 1
                }

    def generate_sentence(self):
        start = random.choice(list(self.corpus.keys()))
        words = [start]
        # length = random.randint(0, 10)
        length = 10
        word = start
        for i in range(length):
            # rename w
            w = self.corpus.get(word, None)
            if w is not None:
                next = self.choose_next_word(self.corpus[word])
                if next:
                    word = next
                    words.append(next)
                else:
                    break
            else:
                break

        return ' '.join(words)

    def choose_next_word(self, word_dict):
        words = []
        weights = []
        for word, weight in word_dict.items():
            words.append(word)
            weights.append(weight)
        if len(words):
            return random.choices(words, weights=weights, k=1)[0]
        else:
            # not sure this is a case...
            return False
