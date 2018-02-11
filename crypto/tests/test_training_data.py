import unittest
import training_data
import pickle


class TestTraining(unittest.TestCase):
    def test_ask(self):
        training_data.ask()

    def test_check_training_data(self):
        with open(training_data.TRAINING_DB_FILE, "rb") as fp:
            db = pickle.load(fp)

        for d in db:
            print(d.feedback)

    def test_generate_automatic(self):
        training_data.generate_automatic()

    def test_data(self):
        with open(training_data.TRAINING_DB_FILE, "rb") as fp:
            data = pickle.load(fp)[0]

        data, feedback = data

        buy = sell = hold = 0
        for f in feedback:
            if f == "buy":
                buy += 1
            elif f == "sell":
                sell += 1
            elif f == "hold":
                hold += 1

        print("Buy: {0}, Sell: {1}, Hold: {2}".format(buy, sell, hold))

