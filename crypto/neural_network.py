import tensorflow as tf
import datetime
import generate_training_data


n_input = 4 * generate_training_data.RANGE
n_nodes_hl1 = 128
n_nodes_hl2 = 64
n_nodes_hl3 = 32

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

    output_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                    'biases': tf.Variable(tf.random_normal([n_classes])), }

    data_norm = tf.nn.l2_normalize(data)

    l1 = tf.add(tf.matmul(data_norm, hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.relu(l3)

    output = tf.matmul(l3, output_layer['weights']) + output_layer['biases']

    return output


def train_neural_network(x):
    prediction = neural_network_model(x)

    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y))
    optimizer = tf.train.AdamOptimizer().minimize(cost)

    hm_epochs = 15
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        for epoch in range(hm_epochs):
            epoch_loss = 0
            batch = batch_data(batch_size)
            total_data_samples = 0
            for epoch_x, epoch_y in batch:
                _, c = sess.run([optimizer, cost], feed_dict={x: epoch_x, y: epoch_y})
                epoch_loss += c
                total_data_samples += len(epoch_y)

            print('Epoch', epoch, 'completed out of', hm_epochs, 'loss:', epoch_loss, 'total data samples:', total_data_samples)

        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))

        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        test_samples, test_feedback = test_data()
        print('Accuracy:', accuracy.eval({x: test_samples, y: test_feedback}))


def batch_data(batch_size):
    with open(generate_training_data.TRAINING_DB_FILE, "r", buffering=10000) as fp:
        while True:
            y = []
            x = []
            for _ in range(batch_size):
                line = fp.readline()
                if line != "":
                    stimuli_data, expected_data = _read_data(line)
                    x.append(stimuli_data)
                    y.append(expected_data)
                else:
                    if x and y:
                        yield x, y
                    raise StopIteration

            yield x, y


def _read_data(line):
    data = [float(d) for d in line.split(";")]
    stimuli_data = data[:-n_classes]
    expected_data = data[-n_classes:]
    return stimuli_data, expected_data


def test_data():
    with open(generate_training_data.TEST_DB_FILE, "r") as fp:
        data = fp.readlines()

        x = []
        y = []
        for line in data:
            if line != "":
                stimuli_data, expected_data = _read_data(line)
                x.append(stimuli_data)
                y.append(expected_data)

        return x, y


if __name__ == "__main__":
    start = datetime.datetime.now()
    train_neural_network(x)
    print("Total time:", (datetime.datetime.now() - start).total_seconds())
