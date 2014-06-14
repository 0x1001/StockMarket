INPUT = 10
HIDDEN = 40
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
            output_data = (-1) if data[idx + INPUT] <= 0 else (1) # Instead of actual value just a positive or negative
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
