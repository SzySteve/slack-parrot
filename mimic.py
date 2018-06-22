import json
import random
import re
from slackbot.bot import Bot, default_reply, listen_to, respond_to
import pdb

USERNAME_REGEX = r'<@([\w]{9})>'

USERS = {}


def load_corpus():
    global USERS
    with open("corpus.json", 'r') as f:
        data = f.read()
        data_json = json.loads(data)

    for user_id, corpus in data_json.items():
        USERS[user_id] = User(user_id, corpus=corpus)
    print(data_json)


def write_corpus():
    data = {}
    for user in USERS.values():
        data[user.slack_id] = user.corpus

    with open("corpus.json", 'w') as f:
        f.write(json.dumps(data))
    print(data)


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

    def __init__(self, id, corpus=None):
        """
        Support passing in the entire corpus so we can load this from the file
        :param id:
        :param corpus:
        """
        self.slack_id = id
        if corpus:
            self.corpus = corpus

    @staticmethod
    def make_pairs(message):
        for i in range(len(message) - 1):
            yield (message[i], message[i + 1])

    def update_corpus(self, message):
        message = message.split()
        if len(message) == 1:
            word = message[0]
            if not word in self.corpus.keys():
                self.corpus[word] = {}
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
                print(self.corpus)

    def generate_sentence(self):
        start = random.choice(list(self.corpus.keys()))
        words = [start]
        max_length = 100
        word = start
        for i in range(max_length):
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


@respond_to('@\w+')
def respond(message):
    text = message.body['text']
    user_id = re.match(USERNAME_REGEX, text).group(1)

    load_corpus()
    print(user_id)
    print("{}".format([u for u in USERS.keys()]))

    if user_id in USERS.keys():
        user = USERS[user_id]
        message.send(user.generate_sentence())
    else:
        message.send('Who is that?!')


@listen_to('.*')
def listen(message):
    user_id = message.user['id']
    load_corpus()
    if user_id in USERS.keys():
        # users we know
        user = USERS[user_id]
        user.update_corpus(message.body['text'])
    else:
        # users we dont know yet
        user = User(user_id)
        user.update_corpus(message.body['text'])
        USERS[user_id] = user
    write_corpus()


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
