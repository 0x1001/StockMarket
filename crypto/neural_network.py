import pickle
import tensorflow as tf

import helper
import training_data


n_input = 4 * training_data.RANGE
n_nodes_hl1 = 500
n_nodes_hl2 = 500
n_nodes_hl3 = 500
n_nodes_hl4 = 500

n_classes = 3  # One hot for "buy", "sell", "hold"
batch_size = 100

x = tf.placeholder('float', [None, n_input])
y = tf.placeholder('float')


def neural_network_model(data):
    hidden_1_layer = {'weights': tf.Variable(tf.random_normal([n_input, n_nodes_hl1])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl1]))}

    hidden_2_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl2]))}

    hidden_3_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl3]))}

    hidden_4_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl3, n_nodes_hl4])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl4]))}

    output_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl4, n_classes])),
                    'biases': tf.Variable(tf.random_normal([n_classes])), }

    data_norm = tf.nn.l2_normalize(data)

    l1 = tf.add(tf.matmul(data_norm, hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.relu(l3)

    l4 = tf.add(tf.matmul(l3, hidden_4_layer['weights']), hidden_4_layer['biases'])
    l4 = tf.nn.relu(l4)

    output = tf.matmul(l4, output_layer['weights']) + output_layer['biases']

    return output


def train_neural_network(x):
    prediction = neural_network_model(x)

    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y))
    optimizer = tf.train.AdamOptimizer().minimize(cost)

    hm_epochs = 8
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        for epoch in range(hm_epochs):
            epoch_loss = 0
            batch = next_data(batch_size)
            total_data_samples = 0
            for epoch_x, epoch_y in batch:
                _, c = sess.run([optimizer, cost], feed_dict={x: epoch_x, y: epoch_y})
                epoch_loss += c
                total_data_samples += len(epoch_y)

            print('Epoch', epoch, 'completed out of', hm_epochs, 'loss:', epoch_loss, 'total data samples:', total_data_samples)

        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))

        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        test_data, test_feedback = _test_data()
        print('Accuracy:', accuracy.eval({x: test_data, y: test_feedback}))


def next_data(batch_size):
    with open(training_data.TRAINING_DB_FILE, "rb") as fp:
        all_data = pickle.load(fp)[0]

    for data in all_data:
        data_idx = 0
        data = data[:-1000]

        x = []
        y = []
        while True:
            if len(y) == batch_size:
                yield x, y
                y = []
                x = []

            if data_idx == len(data) - (training_data.RANGE + training_data.RANGE_AFTER):
                break

            single_data = []
            single_data_raw = data[data_idx: data_idx + training_data.RANGE]
            for j in range(len(single_data_raw)):
                single_data.append(float(single_data_raw[j]["open"]))
                single_data.append(float(single_data_raw[j]["close"]))
                single_data.append(float(single_data_raw[j]["low"]))
                single_data.append(float(single_data_raw[j]["high"]))

            x.append(single_data)
            y.append(correct_output(data, data_idx))

            data_idx += 1

    raise StopIteration


def correct_output(data, idx):
    open = float(data[idx + training_data.RANGE]["open"])
    close = float(data[idx + (training_data.RANGE + training_data.RANGE_AFTER) - 1]["close"])

    change = helper.calculate_difference_in_percent(open, close)

    if change > 1.5:  # if price changed more then 1.5% in data afterwards then it was good moment to buy
        return one_hot_encoding("buy")
    elif change < -1.5:  # if price change less then -1.5% in data afterwards then it was good moment to sell
        return one_hot_encoding("sell")
    else:  # if price didn't change much then do nothing
        return one_hot_encoding("hold")


def _test_data():
    with open(training_data.TRAINING_DB_FILE, "rb") as fp:
        all_data = pickle.load(fp)[0]

    x = []
    y = []
    for data in all_data:
        data = data[-1000:]

        for i in range(len(data) - (training_data.RANGE + training_data.RANGE_AFTER)):
            single_data = []
            single_data_raw = data[i: i + training_data.RANGE]
            for j in range(len(single_data_raw)):
                single_data.append(float(single_data_raw[j]["open"]))
                single_data.append(float(single_data_raw[j]["close"]))
                single_data.append(float(single_data_raw[j]["low"]))
                single_data.append(float(single_data_raw[j]["high"]))

            x.append(single_data)
            y.append(correct_output(data, i))

    return x, y


def one_hot_encoding(data):
    if data == "buy":
        return [1, 0, 0]
    elif data == "sell":
        return [0, 1, 0]
    elif data == "hold":
        return [0, 0, 1]


if __name__ == "__main__":
    train_neural_network(x)