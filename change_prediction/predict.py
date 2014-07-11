class TrainerException(Exception): pass
class ParserException(Exception): pass
class DataFactoryException(Exception): pass

class Logger(object):
    """ Logs data to a file """
    def __init__(self):
        import os
        import datetime

        if not os.path.isdir("log"):
            os.makedirs("log")

        log_name = datetime.datetime.now().strftime("%Y-%m-%d_%H%M.log")
        self.path = os.path.join("log",log_name)

    def log(self,text,file_print=True,console_print=False):
        """ Saves text to a file and prints it in console """
        if file_print:
            with open(self.path,"a") as fp:
                fp.write(text + "\n")

        if console_print:
            print text

class Parser(object):
    """ Parses xls file """

    def __init__(self,file_path):
        self._file_path = file_path

    def getColumn(self,idx,sheet=0):
        """ Returns list of items in column """
        import xlrd

        excel_file = xlrd.open_workbook(self._file_path)
        first_sheet = excel_file.sheets()[sheet]

        return map(lambda cell: cell.value,first_sheet.col(idx))

class Trainer(object):
    """ Neural Network Trainer """

    def __init__(self,net):
        self._net = net

    def train(self,input_data,expected_data):
        """ Trains Network """
        from pybrain.supervised.trainers import BackpropTrainer

        self._check_input_data(input_data,expected_data)

        training_data = self._build_dataset(input_data,expected_data)
        BackpropTrainer(self._net,training_data).trainUntilConvergence()

    def _build_dataset(self,input_data,expected_data):
        from pybrain.datasets import SupervisedDataSet

        data_set = SupervisedDataSet(len(input_data[0]),len(expected_data[0]))
        for idx,data in enumerate(input_data):
            data_set.addSample(input_data[idx],expected_data[idx])

        return data_set

    def _check_input_data(self,input_data,expected_data):
        if len(input_data) != len(expected_data) or len(input_data) == 0:
            raise TrainerException("Wrong data size!")

class NetFactory(object):
    """ Neural Network Factory """

    def construct(self,data_factory):
        """ Constructs neural network """
        input_data,expected_data = data_factory.construct()

        net = self._build_net(input_data,expected_data)
        self._train_net(net,input_data,expected_data)

        return net

    def _build_net(self,input_data,expected_data):
        from pybrain.tools.shortcuts import buildNetwork

        input_size = len(input_data[0])
        output_size = len(expected_data[0])
        hidden_size = 2 * (input_size + output_size)

        return buildNetwork(input_size,hidden_size,output_size)

    def _train_net(self,net,input_data,expected_data):
        Trainer(net).train(input_data,expected_data)

class DataFactory(object):
    """ Abstract class for traning data factory """

    def construct(self):
        """ Constructs traning data """
        raise DataFactoryException("Override this function!")

################################################################################
################################################################################
################################################################################
################################################################################

class ChangeRateDataFactory(DataFactory):
    """ Factory class for change rate data """

    def construct(self,data,data_range):
        data = self._convert_data_to_float(data)
        return self._group_data(data,data_range)

    def _convert_data_to_float(self,data):
        return map(lambda value: float(value)/100.0,data)

    def _group_data(self,data,data_range):
        input_data = []
        excepted_data = []
        for idx in range(len(data)):
            input_data.append(tuple([data[idx + i] for i in range(data_range)]))
            try:
                excepted_data.append(tuple(data[idx + data_range]))
            except IndexError:
                break

        return input_data,excepted_data

def predict(change_rate_data,volume_data):
    return 0.0,0.0


if __name__ == "__main__":
    import multiprocessing

    DATA_RANGE = 15
    MAX_DATA_RANGE = 30

    logger = Logger()

    change_rate_data = Parser("PLKGHM000017.xls").getColumn(9)
    volume_data = Parser("PLKGHM000017.xls").getColumn(10)

    change_rate_data.pop(0)
    volume_data.pop(0)

    pool = multiprocessing.Pool()

    predictions = []
    for idx in range(len(change_rate_data)):
        change_rate_sample = [change_rate_data[idx + i] for i in range(MAX_DATA_RANGE)]
        volume_sample = [volume_data[idx + i] for i in range(MAX_DATA_RANGE)]

        try:
            change_rate_expectation = change_rate_data[idx + MAX_DATA_RANGE]
            volume_data_expectation = volume_data[idx + MAX_DATA_RANGE]
        except IndexError:
            break

        logger.log("Adding task: " + str(idx),False,True)
        predictions.append((pool.apply_async(predict,(change_rate_sample,volume_sample)),change_rate_expectation,volume_data_expectation,idx))

    logger.log("Waiting...",False,True)

    for prediction_worker,change_rate_expectation,volume_data_expectation,idx in predictions:
        change_rate_prediction,volume_data_prediction = prediction_worker.get()
        logger.log(str('{0:.2f}'.format(change_rate_prediction*100)) + ";" + str(change_rate_expectation*100),True,False)
        logger.log("Prediction: " + str('{0:.2f}'.format(change_rate_prediction*100)) + " % Reality: " + str(change_rate_expectation*100) + " % Sample: " + str(idx) + " / " + str(len(change_rate_data) - MAX_DATA_RANGE),False,True)

    pool.close()
    pool.join()
