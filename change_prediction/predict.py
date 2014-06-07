def getData():
    import xlrd

    excel_file = xlrd.open_workbook("PLKGHM000017.xls")
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
    from pybrain.structure import RecurrentNetwork
    from pybrain.supervised.trainers import BackpropTrainer
    from pybrain.datasets import SupervisedDataSet
    from pybrain.structure import LinearLayer, SigmoidLayer
    from pybrain.structure import FullConnection

    INPUT = 10
    HIDDEN = 1
    OUTPUT = 1

    data_set = SupervisedDataSet(INPUT,OUTPUT)
    for idx in range(len(data)):
        input_data = (data[idx],
                      data[idx + 1],
                      data[idx + 2],
                      data[idx + 3],
                      data[idx + 4],
                      data[idx + 5],
                      data[idx + 6],
                      data[idx + 7],
                      data[idx + 8],
                      data[idx + 9],
                     )

        try:
            output_data = (data[idx + 10])
        except IndexError:
            break

        data_set.addSample(input_data,output_data)

    n = RecurrentNetwork()
    n.addInputModule(LinearLayer(INPUT, name='in'))
    n.addModule(SigmoidLayer(HIDDEN, name='hidden'))
    n.addOutputModule(LinearLayer(OUTPUT, name='out'))
    n.addConnection(FullConnection(n['in'], n['hidden'], name='c1'))
    n.addConnection(FullConnection(n['hidden'], n['out'], name='c2'))
    n.addRecurrentConnection(FullConnection(n['hidden'], n['hidden'], name='c3'))
    n.sortModules()

    trainer = BackpropTrainer(n,data_set)
    trainer.trainUntilConvergence()

    return n

def day_prediction(data):
    net = train(data)
    return net.activate(data[-10:])[0]

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
        input_data = [data[idx + i] for i in range(30)]

        try:
            expectation = data[idx + 30]
        except IndexError:
            break

        print "Adding task: " + str(idx)
        predictions.append((pool.apply_async(day_prediction,(input_data,)),expectation,idx))

    print "Waiting..."

    for prediction_worker,expectation,idx in predictions[:]:
        prediction = prediction_worker.get()
        with open(log_path,"a") as fp:
            fp.write(str('{0:.2f}'.format(prediction*100)) + ";" + str(expectation*100) + "\n")

        print "Prediction: " + str('{0:.2f}'.format(prediction*100)) + " % Reality: " + str(expectation*100) + " % Sample: " + str(idx) + " / " + str(len(data)-30)
        predictions.remove((prediction_worker,expectation,idx))

    pool.close()
    pool.join()

    end_time = datetime.datetime.now()
    print end_time

    print "Calculation took:    " + str((end_time - start_time).total_seconds()/60) + " Min"
