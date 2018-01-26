import os
import poloniex
import time
import datetime
import argparse
import matplotlib.pyplot as plt


def find_tree_line_strike(data):
    """
        More to read here: https://www.investopedia.com/articles/active-trading/092315/5-most-powerful-candlestick-patterns.asp
    """
    found = None
    for i in range(len(data) - 4):
        first = data[i]
        second = data[i + 1]
        third = data[i + 2]
        forth = data[i + 3]

        if not first["close"] < first["open"]:
            continue

        if not second["close"] < second["open"]:
            continue

        if not third["close"] < third["open"]:
            continue

        if not forth["close"] > forth["open"]:
            continue

        if not (first["close"] > second["close"] > third["close"] > forth["open"]):
            continue

        if not first["high"] < forth["high"]:
            continue

        if not third["low"] > forth["low"]:
            continue

        found = datetime.datetime.utcfromtimestamp(int(first["date"]))

    return found


def find_two_black_gapping(data):
    """
        More to read here: https://www.investopedia.com/articles/active-trading/092315/5-most-powerful-candlestick-patterns.asp
    """
    found = None
    for i in range(len(data) - 4):
        first = data[i]
        second = data[i + 1]
        third = data[i + 2]
        forth = data[i + 3]

        if not first["close"] > first["open"]:
            continue

        if not second["close"] < second["open"]:
            continue

        if not third["close"] < third["open"]:
            continue

        if not forth["close"] < forth["open"]:
            continue

        if not second["low"] > third["high"]:
            continue

        if not third["low"] > forth["low"]:
            continue

        found = datetime.datetime.utcfromtimestamp(int(first["date"]))

    return found


def find_three_black_crows(data):
    """
        More to read here: https://www.investopedia.com/articles/active-trading/092315/5-most-powerful-candlestick-patterns.asp
    """
    found = None
    for i in range(len(data) - 4):
        first = data[i]
        second = data[i + 1]
        third = data[i + 2]
        forth = data[i + 3]

        if not first["close"] > first["open"]:
            continue

        if not second["close"] < second["open"]:
            continue

        if not third["close"] < third["open"]:
            continue

        if not forth["close"] < forth["open"]:
            continue

        if not first["high"] < second["high"]:
            continue

        if not (second["low"] > third["low"] > forth["low"]):
            continue

        found = datetime.datetime.utcfromtimestamp(int(first["date"]))

    return found


def find_evening_star(data):
    """
        More to read here: https://www.investopedia.com/articles/active-trading/092315/5-most-powerful-candlestick-patterns.asp
    """
    found = None
    for i in range(len(data) - 4):
        first = data[i]
        second = data[i + 1]
        third = data[i + 2]

        if not first["close"] > first["open"]:
            continue

        if not second["close"] < second["open"]:
            continue

        if not third["close"] < third["open"]:
            continue

        if not first["close"] < second["close"]:
            continue

        if not second["close"] > third["open"]:
            continue

        if not (first["close"] - first["open"]) * 0.1 > second["open"] - second["close"]:
            continue

        if not (third["close"] - third["open"]) * 0.1 > second["open"] - second["close"]:
            continue

        found = datetime.datetime.utcfromtimestamp(int(first["date"]))

    return found


def find_abandoned_baby(data):
    """
        More to read here: https://www.investopedia.com/articles/active-trading/092315/5-most-powerful-candlestick-patterns.asp
    """
    found = None
    for i in range(len(data) - 4):
        first = data[i]
        second = data[i + 1]
        third = data[i + 2]

        if not first["close"] < first["open"]:
            continue

        if not second["close"] == second["open"]:
            continue

        if not third["close"] > third["open"]:
            continue

        if not first["low"] > second["high"]:
            continue

        if not third["low"] > second["high"]:
            continue

        found = datetime.datetime.utcfromtimestamp(int(first["date"]))

    return found


def what_to_sell():
    polo = poloniex.Poloniex()

    found = {}
    for currency_pair in polo.returnTicker():
        data = polo.returnChartData(currency_pair, period=300, start=(time.time() - polo.HOUR * 2))
        data = convert_to_float(data)

        found[currency_pair] = find_three_black_crows(data)

        if not found[currency_pair]:
            found[currency_pair] = find_two_black_gapping(data)

        if not found[currency_pair]:
            found[currency_pair] = find_evening_star(data)

    return found


def what_to_buy():
    polo = poloniex.Poloniex()

    found = {}
    for currency_pair in polo.returnTicker():
        data = polo.returnChartData(currency_pair, period=300, start=(time.time() - polo.HOUR * 2))
        data = convert_to_float(data)

        found[currency_pair] = find_tree_line_strike(data)

        if not found[currency_pair]:
            found[currency_pair] = find_abandoned_baby(data)
    
    return found


def get_balance():
    api_key, secret = get_key()

    polo = poloniex.Poloniex(api_key, secret)
    data = polo.returnCompleteBalances()
    data = convert_to_float_balance(data)

    coins_with_balance = {}
    for coin in data:
        if data[coin]["btcValue"] != 0.0:
            coins_with_balance[coin] = data[coin]

    btc_price = float(polo.returnTicker()["USDT_BTC"]['last'])

    coins_sorted = []
    for coin in coins_with_balance:
        new_coin = coins_with_balance[coin]
        new_coin['name'] = coin
        new_coin['usdtValue'] = btc_price * coins_with_balance[coin]['btcValue']
        coins_sorted.append(new_coin)

    coins_sorted.sort(key=lambda k: k['btcValue'], reverse=True)
    return coins_sorted


def get_open_orders():
    api_key, secret = get_key()

    polo = poloniex.Poloniex(api_key, secret)
    data = polo.returnOpenOrders()
    data = filter_open_orders(data)

    return data


def filter_open_orders(data):
    return {k: v for k,v in data.items() if v}


def display_open_orders(data):
    print("Open buy orders for:")
    for coin in data:
        for buy in data[coin]:
            if buy["type"] == "buy":
                print(coin)

    print("Open sell orders for:")
    for coin in data:
        for sell in data[coin]:
            if sell["type"] == "sell":
                print(coin)


def display_balance(coins):
    print("Total balance: {0:.2f} USDT".format(sum([coin['usdtValue'] for coin in coins])))
    for coin in coins:
        print("{0: <10} Amount: {1: <20} BTC: {2: <20} USDT: {3}".format(coin['name'],
                                                          coin['available'] + coin["onOrders"],
                                                          coin['btcValue'],
                                                          coin['usdtValue']))


def plot_balance(coins):
    labels = ["{0: <10} {1:.2f} USDT".format(coin["name"], coin["usdtValue"]) for coin in coins]
    sizes = [coin['usdtValue'] for coin in coins]
    explode = [0.1] + [0] * (len(coins) - 1)

    fig1, ax1 = plt.subplots()
    patches, texts = ax1.pie(sizes, explode=explode, shadow=True, startangle=90)
    ax1.axis('equal')

    plt.legend(patches, labels, loc='center left', fontsize=8)
    plt.title('Total balance: {0:.2f} USDT'.format(sum(sizes)))
    plt.tight_layout()
    plt.show()


def convert_to_float(data):
    new_data = []
    for d in data:
        new_d = {}
        for k in d:
            new_d[k] = float(d[k])
        new_data.append(new_d)
    return new_data


def convert_to_float_balance(data):
    new_data = {}
    for d in data:
        new_d = {}
        for k in data[d]:
            new_d[k] = float(data[d][k])
        new_data[d] = new_d
    return new_data


def display_predictions(found, prefix):
    if any(found.values()):
        print(prefix)
        for currency_pair in found:
            if found[currency_pair]:
                print(currency_pair, " on ", found[currency_pair].strftime('UTC: %Y-%m-%d %H:%M:%S'))


def get_key():
    if not os.path.isfile("poloniex_keys.txt"):
        raise Exception("File poloniex_keys.txt does not exists. "
                        "It should contain in first line your api key and in second line your secret key."
                        "You can generate Poloniex keys in API Keys menu once you log in.")

    with open("poloniex_keys.txt") as fp:
        api_key = fp.readline().strip()
        secret = fp.readline().strip()

    return api_key, secret


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Poloniex command line tool. '
                                                 'Uses Poloniex API: https://github.com/s4w3d0ff/python-poloniex/releases. '
                                                 'Version python-poloniex v0.4.7.'
                                                 'pip install https://github.com/s4w3d0ff/python-poloniex/archive/v0.4.7.zip')
    parser.add_argument('-s', dest='sell', action='store_true', help='Tells what to sell according to candelstick analysis.')
    parser.add_argument('-b', dest='buy', action='store_true', help='Tells what to buy according to candelstick analysis')
    parser.add_argument('-ab', dest='balance', action='store_true', help='Tells account balance.')
    parser.add_argument('-abg', dest='balance_with_graph', action='store_true', help='Tells account balance on the pie chart.')
    parser.add_argument('-oo', dest='open_orders', action='store_true', help='Tells open orders.')

    args = parser.parse_args()

    if args.sell:
        display_predictions(what_to_sell(), "Good to sell:")

    if args.buy:
        display_predictions(what_to_buy(), "Good to buy:")

    if args.balance:
        display_balance(get_balance())

    if args.balance_with_graph:
        plot_balance(get_balance())

    if args.open_orders:
        display_open_orders(get_open_orders())

