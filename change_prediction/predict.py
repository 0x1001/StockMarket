class TrainerException(Exception): pass
class ParserException(Exception): pass

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



##################################################################################

INPUT = 15
HIDDEN = 30
OUTPUT = 1

INPUT_DATA_RANGE = 30

def getData():
    import xlrd

    excel_file = xlrd.open_workbook("PL9999999987.xls")
    first_sheet = excel_file.sheets()[0]

    data = []
    for cell in first_sheet.col(9):
        try:
            data_float = float(cell.value)/100.0
        except ValueError:
            pass
        else:
            data.append(data_float)

    return data

def train(data):
    from pybrain.tools.shortcuts import buildNetwork
    from pybrain.supervised.trainers import BackpropTrainer
    from pybrain.datasets import SupervisedDataSet

    data_set = SupervisedDataSet(INPUT,OUTPUT)
    for idx in range(len(data)):
        input_data = tuple([data[idx + i] for i in range(INPUT)])

        try:
            output_data = data[idx + INPUT]
        except IndexError:
            break

        data_set.addSample(input_data,output_data)

    net = buildNetwork(INPUT,HIDDEN,OUTPUT)
    trainer = BackpropTrainer(net,data_set)
    trainer.trainUntilConvergence()

    return net

def day_prediction(data):
    net = train(data)
    return net.activate(data[-INPUT:])[0]

if __name__ == "__main__":
    import datetime
    import os
    import multiprocessing

    if not os.path.isdir("log"):
        os.makedirs("log")
    log_name = datetime.datetime.now().strftime("%Y-%m-%d_%H%M.log")
    log_path = os.path.join("log",log_name)

    start_time = datetime.datetime.now()
    print start_time

    data = getData()

    pool = multiprocessing.Pool()

    predictions = []
    for idx in range(len(data)):
        input_data = [data[idx + i] for i in range(INPUT_DATA_RANGE)]

        try:
            expectation = data[idx + INPUT_DATA_RANGE]
        except IndexError:
            break

        print "Adding task: " + str(idx)
        predictions.append((pool.apply_async(day_prediction,(input_data,)),expectation,idx))

    print "Waiting..."

    for prediction_worker,expectation,idx in predictions[:]:
        prediction = prediction_worker.get()
        with open(log_path,"a") as fp:
            fp.write(str('{0:.2f}'.format(prediction*100)) + ";" + str(expectation*100) + "\n")

        print "Prediction: " + str('{0:.2f}'.format(prediction*100)) + " % Reality: " + str(expectation*100) + " % Sample: " + str(idx) + " / " + str(len(data)-INPUT_DATA_RANGE)
        predictions.remove((prediction_worker,expectation,idx))

    pool.close()
    pool.join()

    end_time = datetime.datetime.now()
    print end_time

    print "Calculation took:    " + str((end_time - start_time).total_seconds()/60) + " Min"
