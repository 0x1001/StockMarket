if __name__ == "__main__":
    file = "feedforward/2014-06-07_0100.log"

    with open(file) as fp:
        contents = fp.readlines()

    match = 0
    index = 0
    for line in contents:
        line = line.split(";")
        if len(line) < 2: break

        prediction = float(line[0])
        expectation = float(line[1])

        threshold = 0

        if prediction < threshold and expectation < threshold:
            match += 1
        elif prediction > threshold and expectation > threshold:
            match += 1
        else:
            pass

        index += 1

    print str(match) + " / " + str(index)