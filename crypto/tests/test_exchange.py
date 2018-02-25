import unittest
import exchange


class TestExchange(unittest.TestCase):
    def test_get_chart_data(self):
        for k, v in exchange.get_chart_data("USDT_BTC")[0].items():
            print("{0} - {1}".format(k, v))

    def test_plot_chart_data(self):
        data = exchange.get_chart_data("USDT_BTC")
        exchange.plot_chart_data(data[-10:], "USDT_BTC")

    def test_get_all_coin_pairs(self):
        print(exchange.get_all_coin_pairs())