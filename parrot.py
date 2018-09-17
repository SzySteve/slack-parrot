import logging
import json
import random
import re
from slackbot.bot import Bot, default_reply, listen_to, respond_to

logger = logging.getLogger(__name__)

USERNAME_REGEX = r'<@([\w]{9})>'

USERS = {}

PRESS_F_COUNTER = 0

def load_corpus():
    global USERS
    with open("corpus.json", 'r') as f:
        data = f.read()
        data_json = json.loads(data)

    for user_id, corpus in data_json.items():
        USERS[user_id] = User(user_id, corpus=corpus)


def write_corpus():
    data = {}
    for user in USERS.values():
        data[user.slack_id] = user.corpus

    with open("corpus.json", 'w') as f:
        f.write(json.dumps(data))


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
        for i in range(len(message)):
            try:
                next_word = message[i + 1]
            except IndexError:
                next_word = None
            yield (message[i], next_word)

    def update_corpus(self, message):
        message = message.split()
        if len(message) == 1:
            word = message[0]
            if not word in self.corpus.keys():
                self.corpus[word] = {}
        for pair in self.make_pairs(message):
            first = pair[0]
            second = pair[1]

            if first in self.corpus.keys() and second is not None:
                word_counters = self.corpus[first]
                if second in word_counters.keys():
                    word_counters[second] += 1
                else:
                    word_counters[second] = 1
            else:
                if second:
                    self.corpus[first] = {
                        second: 1
                    }
                else:
                    self.corpus[first] = {}


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
    try:
        text = message.body['text']
        user_id = re.match(USERNAME_REGEX, text).group(1)

        load_corpus()

        if user_id in USERS.keys():
            user = USERS[user_id]
            message.send(user.generate_sentence())
        else:
            message.send('Who is that?!')
    except Exception as e:
        logger.exception('Caught error in respond')


@listen_to('.*')
def listen(message):
    global PRESS_F_COUNTER
    try:
        text = message.body['text']
        if text == 'f':
            if PRESS_F_COUNTER > 3:
                message.send('f')
                PRESS_F_COUNTER = 0
            else:
                PRESS_F_COUNTER += 1
        else:
            PRESS_F_COUNTER = 0

        user_id = message.user['id']
        load_corpus()
        if user_id in USERS.keys():
            # users we know
            user = USERS[user_id]
            user.update_corpus(text)
        else:
            # users we dont know yet
            user = User(user_id)
            user.update_corpus(text)
            USERS[user_id] = user
        write_corpus()
    except Exception as e:
        logger.exception('Caught error in listen')

def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
