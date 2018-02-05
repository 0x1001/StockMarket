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
