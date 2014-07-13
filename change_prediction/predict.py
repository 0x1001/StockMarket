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
    def __init__(self,change_rate_data,data_range):
        self._data_range = data_range
        self._change_rate_data = change_rate_data

    def construct(self):
        self._change_rate_data = self._convert_data_to_float(self._change_rate_data)
        return self._group_data()

    def _convert_data_to_float(self,data):
        return map(lambda value: float(value)/100.0,data)

    def _group_data(self):
        input_data = []
        expected_data = []
        for idx in range(len(self._change_rate_data)):
            try:
                expected_data.append(tuple([self._change_rate_data[idx + self._data_range]]))
            except IndexError:
                break

            input_data.append(tuple(self._change_rate_data[idx:idx + self._data_range]))

        return input_data,expected_data

class VolumeDataFactory(DataFactory):
    """ Factory class for volume data """
    def __init__(self,volume_data,data_range):
        self._data_range = data_range
        self._volume_data = volume_data

    def construct(self):
        self._volume_data = self._inverse_data(self._volume_data)
        return self._group_data()

    def _inverse_data(self,data):
        return map(lambda value: 1/float(value),data)

    def _group_data(self):
        input_data = []
        expected_data = []
        for idx in range(len(self._volume_data)):
            try:
                expected_data.append(tuple([self._volume_data[idx + self._data_range]]))
            except IndexError:
                break

            input_data.append(tuple(self._volume_data[idx:idx + self._data_range]))

        return input_data,expected_data

class CombinedDataFactory(DataFactory):
    """ Factory class for combined change rate and volume data """
    def __init__(self,change_rate_data,volume_data):
        self._change_rate_data = change_rate_data
        self._volume_data = volume_data

    def construct(self):
        self._volume_data = self._inverse_data(self._volume_data)
        self._change_rate_data = self._convert_data_to_float(self._change_rate_data)
        return self._group_data()

    def _inverse_data(self,data):
        return map(lambda value: 1/float(value),data)

    def _convert_data_to_float(self,data):
        return map(lambda value: float(value)/100.0,data)

    def _group_data(self):
        input_data = []
        expected_data = []
        for idx in range(len(self._change_rate_data)):
            try:
                if self._change_rate_data[idx + 1] >= 0:
                    expected_data.append(tuple([1]))
                else:
                    expected_data.append(tuple([-1]))
            except IndexError:
                break

            input_data.append((self._change_rate_data[idx],self._volume_data[idx]))

        return input_data,expected_data

def predict(change_rate_data,volume_data,data_range):
    change_rate_net = NetFactory().construct(ChangeRateDataFactory(change_rate_data,data_range))
    volume_net = NetFactory().construct(VolumeDataFactory(volume_data,data_range))
    combined_net = NetFactory().construct(CombinedDataFactory(change_rate_data,volume_data))

    change_rate_prediction = change_rate_net.activate(change_rate_data[-data_range:])
    volume_prediction = volume_net.activate(volume_data[-data_range:])

    combined_prediction = combined_net.activate((change_rate_prediction,volume_prediction))

    return combined_prediction[0]

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
        change_rate_sample = change_rate_data[idx:idx+MAX_DATA_RANGE]
        volume_sample = volume_data[idx:idx+MAX_DATA_RANGE]

        try:
            if change_rate_data[idx + MAX_DATA_RANGE] >= 0:
                expectation = 1
            else:
                expectation = -1
        except IndexError:
            break

        logger.log("Adding task: " + str(idx),False,True)
        predictions.append((pool.apply_async(predict,(change_rate_sample,volume_sample,DATA_RANGE)),expectation,idx))

    logger.log("Waiting...",False,True)

    for prediction_worker,expectation,idx in predictions:
        prediction = prediction_worker.get()
        logger.log(str(prediction) + ";" + str(expectation),True,False)
        logger.log("Prediction: " + str(prediction) + " % Reality: " + str(expectation) + " % Sample: " + str(idx) + " / " + str(len(change_rate_data) - MAX_DATA_RANGE),False,True)

    pool.close()
    pool.join()
