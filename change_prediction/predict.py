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
    from pybrain.tools.shortcuts import buildNetwork
    from pybrain.supervised.trainers import BackpropTrainer
    from pybrain.datasets import SupervisedDataSet

    INPUT = 10
    HIDDEN = 40
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

    net = buildNetwork(INPUT,HIDDEN,OUTPUT)
    trainer = BackpropTrainer(net,data_set)
    trainer.trainUntilConvergence()

    return net

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

        predictions.append((pool.apply_async(day_prediction,(input_data,)),expectation))


    progress = 0
    for prediction_worker,expectation in predictions:
        prediction = prediction_worker.get()
        with open(log_path,"a") as fp:
            fp.write(str(prediction*100) + ";" + str(expectation*100) + "\n")

        progress += 1
        print "Prediction: " + str(prediction*100) + " % Reality: " + str(expectation*100) + " % Sample: " + str(progress) + " / " + str(len(data)-30)

    pool.close()
    pool.join()

    end_time = datetime.datetime.now()
    print end_time

    print "Calculation took:    " + str((end_time - start_time).total_seconds()/60) + " Min"
