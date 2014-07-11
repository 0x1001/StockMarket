import unittest
import predict

class CustomData(predict.DataFactory):
    def construct(self):
        return [(1,0),(0,1),(0,0),(1,1)],[(1,),(1,),(0,),(0,)]

class test_Parser(unittest.TestCase):
    def setUp(self):
        self.p = predict.Parser("test_file.xls")

    def test_getColumn(self):
        column = self.p.getColumn(3)
        self.assertIsInstance(column,list)
        self.assertEqual(column[0],u"Nazwa")

class test_Logger(unittest.TestCase):
    def setUp(self):
        self.l = predict.Logger()

    def test_log(self):
        self.l.log("text")

    def tearDown(self):
        import os
        try:
            os.unlink(self.l.path)
        except OSError:
            pass

class test_Trainer(unittest.TestCase):
    def setUp(self):
        self.t = predict.Trainer(predict.NetFactory().construct(CustomData()))

    def test_train(self):
        self.t.train([(1,0),(0,1)],[(1,),(0,)])

    def test_check_input_data(self):
        with self.assertRaises(predict.TrainerException):
            self.t._check_input_data([()],[(),()])

        with self.assertRaises(predict.TrainerException):
            self.t._check_input_data([],[])

    def test_build_dataset(self):
        self.t._build_dataset([(),()],[(),()])

class test_NetFactory(unittest.TestCase):
    def setUp(self):
        self.n = predict.NetFactory()
        self.data_factory = CustomData()

    def test_construct(self):
        self.assertIsNotNone(self.n.construct(self.data_factory))

    def test_build_net(self):
        net = self.n._build_net([(),()],[(),()])

class test_DataFactory(unittest.TestCase):
    def setUp(self):
        self.d = predict.DataFactory()

    def test_construct(self):
        with self.assertRaises(predict.DataFactoryException):
            self.d.construct()

if __name__ == "__main__":
    unittest.main()
