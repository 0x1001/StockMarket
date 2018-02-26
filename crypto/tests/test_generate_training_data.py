import unittest
import generate_training_data


class TestGenerateTraninigData(unittest.TestCase):
    def test_get_data(self):
        all_data = generate_training_data.get_data()

        k = 0
        for d in all_data:
            k += len(d)

        print(k)

