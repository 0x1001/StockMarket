import argparse
import exchange
import random
import helper

TRAINING_DB_FILE = "training_data_db.csv"
TEST_DB_FILE = "test_data_db.csv"
RANGE = 10
RANGE_AFTER = 10

TRAIN_DATA_SIZE = 3000000
TEST_DATA_SIZE = round(TRAIN_DATA_SIZE * 0.05)

CURRENCY_PAIRS = ["USDT_BTC", "USDT_ETH", "USDT_LTC", "USDT_ZEC", "USDT_ETC", "USDT_REP", "USDT_XMR", "USDT_STR", "USDT_DASH", "USDT_XRP", "USDT_BCH", "USDT_NXT"]


def get_data():
    print("Getting data from exchange.")
    all_data = []
    for currency_pair in CURRENCY_PAIRS:
        data = exchange.get_chart_data(currency_pair)
        all_data.append(data)
        print("Progress {2}: {0} / {1}".format(CURRENCY_PAIRS.index(currency_pair), len(CURRENCY_PAIRS), currency_pair))

    return all_data


def generate_automatic(data, file_name, number_of_samples):
    print("Generating data for training.")
    last_progress = -1
    with open(file_name, "w", buffering=10000) as fp:
        for p in range(number_of_samples):
            coin_data = random.choice(data)
            start = random.randint(0, len(coin_data) - RANGE - RANGE_AFTER)

            stimulus = []
            for i in range(start, start + RANGE):
                stimulus.append(float(coin_data[i]["open"]))
                stimulus.append(float(coin_data[i]["close"]))
                stimulus.append(float(coin_data[i]["low"]))
                stimulus.append(float(coin_data[i]["high"]))

            expected = expected_output(coin_data, start)
            fp.write(";".join([str(d) for d in stimulus + expected]) + "\n")

            progress = round(p/number_of_samples*100)
            if last_progress != progress:
                last_progress = progress
                print("Progress on {0}: {1}%".format(file_name, progress))


def expected_output(data, idx):
    open = float(data[idx + RANGE]["open"])
    close = float(data[idx + (RANGE + RANGE_AFTER) - 1]["close"])

    change = helper.calculate_difference_in_percent(open, close)

    if change > 1.5:  # if price changed more then 1.5% in data afterwards then it was good moment to buy
        return one_hot_encoding("buy")
    elif change < -1.5:  # if price change less then -1.5% in data afterwards then it was good moment to sell
        return one_hot_encoding("sell")
    else:  # if price didn't change much then do nothing
        return one_hot_encoding("hold")


def one_hot_encoding(data):
    if data == "buy":
        return [1, 0, 0]
    elif data == "sell":
        return [0, 1, 0]
    elif data == "hold":
        return [0, 0, 1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Training data generator.')
    parser.add_argument('-g', dest='generate', action='store_true', help='Generates data automatically')

    args = parser.parse_args()

    if args.generate:
        data = get_data()
        generate_automatic(data, TRAINING_DB_FILE, TRAIN_DATA_SIZE)
        generate_automatic(data, TEST_DB_FILE, TEST_DATA_SIZE)
