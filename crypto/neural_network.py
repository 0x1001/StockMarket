import pickle
import tensorflow as tf
import training_data


n_input = 4 * training_data.RANGE
n_nodes_hl1 = 500
n_nodes_hl2 = 500
n_nodes_hl3 = 500

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

    l1 = tf.add(tf.matmul(data, hidden_1_layer['weights']), hidden_1_layer['biases'])
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

    hm_epochs = 10
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
        #print('Accuracy:', accuracy.eval({x: mnist.test.images, y: mnist.test.labels}))


def next_data(batch_size):
    _DATA_IDX = 0

    with open(training_data.TRAINING_DB_FILE, "rb") as fp:
        data = pickle.load(fp)[0]

    x = []
    y = []
    while True:
        if len(y) == batch_size:
            yield x, y
            y = []
            x = []

        if _DATA_IDX == len(data[1]):
            raise StopIteration()

        single_data = []
        single_data_raw = data[0][_DATA_IDX: _DATA_IDX + training_data.RANGE]
        for j in range(len(single_data_raw)):
            single_data.append(float(single_data_raw[j]["open"]))
            single_data.append(float(single_data_raw[j]["close"]))
            single_data.append(float(single_data_raw[j]["low"]))
            single_data.append(float(single_data_raw[j]["high"]))

        if is_balanced(batch_size, y, data[1][_DATA_IDX]):
            x.append(single_data)
            y.append(one_hot_encoding(data[1][_DATA_IDX]))

        _DATA_IDX += 1


def is_balanced(batch_size, y, current):
    #return len([d for d in y if d == one_hot_encoding(current)]) < batch_size/3
    return True


def one_hot_encoding(data):
    if data == "buy":
        return [1, 0, 0]
    elif data == "sell":
        return [0, 1, 0]
    elif data == "hold":
        return [0, 0, 1]


if __name__ == "__main__":
    train_neural_network(x)