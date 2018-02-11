import unittest
import neural_network


class TestNeuralNetwork(unittest.TestCase):
    def test_test_data(self):
        test_data, feedback = neural_network._test_data()

        if len(test_data) != len(feedback):
            self.fail("Test data size is different then feedback size.")

        inner_size = {len(d) for d in test_data}

        if len(inner_size) != 1:
            self.fail("Test data are of different sizes. Found these: {0}".format(inner_size))
