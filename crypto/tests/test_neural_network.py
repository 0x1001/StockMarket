import unittest
import neural_network


class TestNeuralNetwork(unittest.TestCase):
    def test_batch_data(self):
        for data, expected in neural_network.batch_data(100):
            print(len(data), len(expected))

    def test_test_data(self):
        data_x, data_y = neural_network.test_data()
