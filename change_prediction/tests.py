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
        #self.t.train([(),()],[(),()])
        pass
        # TODO

    def test_check_input_data(self):
        import predict

        with self.assertRaises(predict.TrainerException):
            self.t._check_input_data([()],[(),()])

        with self.assertRaises(predict.TrainerException):
            self.t._check_input_data([],[])

    def test_build_dataset(self):
        self.t._build_dataset([(),()],[(),()])

class test_NetFactory(unittest.TestCase):
    def test_setUp(self):
        import predict
        self.n = predict.NetFactory()

if __name__ == "__main__":
    unittest.main()
