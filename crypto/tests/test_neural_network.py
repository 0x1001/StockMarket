import unittest
import neural_network


class TestNeuralNetwork(unittest.TestCase):
    def test_test_data(self):

        for data, expected in neural_network.batch_data(100):
            print(len(data), len(expected))
