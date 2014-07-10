import unittest

class test_parser(unittest.TestCase):
    def setUp(self):
        import predict
        self.p = predict.Parser("test_file.xls")

    def test_getColumn(self):
        column = self.p.getColumn(3)
        self.assertIsInstance(column,list)
        self.assertEqual(column[0],u"Nazwa")

class test_Trainer(unittest.TestCase):
    def setUp(self):
        import predict

        class Net(): pass

        self.t = predict.Trainer(Net())

    def test_train(self):
        self.t.train([()],[()])

if __name__ == "__main__":
    unittest.main()
