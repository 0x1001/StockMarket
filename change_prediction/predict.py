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

    print "Training Data set length: " + str(len(data_set))

    net = buildNetwork(INPUT,HIDDEN,OUTPUT)
    trainer = BackpropTrainer(net,data_set)
    trainer.trainUntilConvergence()

    return net

def day_prediction(data,real_data):
    net = train(data)

    log = "Next day prediction: " + str(net.activate(data[-10:])[0]*100) + "% Real data: " + str(real_data*100) + "%"
    print log

    with open("log.txt","a") as fp:
        fp.write(log + "\n")

if __name__ == "__main__":
    import datetime

    start_time = datetime.datetime.now()
    print start_time

    data = getData()

    for idx in range(len(data)):
        input_data = [data[idx + i] for i in range(30)]

        try:
            expected_data = data[idx + 30]
        except IndexError:
            break

        print "Progress: " + str(idx) + " / " + str(len(data)-30)
        day_prediction(input_data,expected_data)

    end_time = datetime.datetime.now()
    print end_time

    print "Calculation took:    " + str((end_time - start_time).total_seconds()/60) + " Min"
