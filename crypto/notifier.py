import argparse
import datetime
import time
import exchange
import threading
import http.client as httplib
import socket
from urllib import parse
import json
import os
from paho.mqtt import publish


class Pushover(object):
    def __init__(self):
        if not os.path.isfile("pushover_keys.txt"):
            raise Exception("PushOver is not configured. "
                            "Create pushover_keys.txt with first line your user key and "
                            "second line with your application token.")

        with open("pushover_keys.txt") as fp:
            self._user = fp.readline().strip()
            self._token = fp.readline().strip()

    def send(self, contents):
        try:
            response = self._send_notification(contents)
        except (httplib.HTTPException, socket.error) as error:
            raise Exception("Cannot send notification via Pushover. Error: " + str(error))
        else:
            self._analyze_server_response(response)

    def _send_notification(self, contents):
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST",
                     "/1/messages.json",
                     parse.urlencode({"token": self._token,
                                       "user": self._user,
                                       "message": contents}),
                     {"Content-type": "application/x-www-form-urlencoded"})

        return conn.getresponse()

    def _analyze_server_response(self, response):
        resp_contents = response.read()
        server_msg = json.loads(resp_contents.decode("utf8"))
        if server_msg["status"] == 0:
            raise Exception(("Error during sending Pushover notification: " + ", ".join(server_msg["errors"])))


def orders_change_thread():
    orders = {}
    pushover = Pushover()
    while True:
        completed = ""
        pending = ""
        new = ""
        new_orders = exchange.get_open_orders()
        balance = exchange.get_balance()
        if orders != new_orders:
            for coin in orders:
                for o in orders[coin]:
                    if coin not in new_orders:
                        completed += "{0} {1} amount: {2}, total: {3}\n".format(o['type'].capitalize(), coin, o['amount'], o['total'])
                    else:
                        for new_o in new_orders[coin]:
                            if new_o != o:
                                completed += "{0} {1} amount: {2}, total: {3}\n".format(o['type'].capitalize(), coin, o['amount'], o['total'])

            for coin in new_orders:
                for o in new_orders[coin]:
                    if coin not in orders:
                        new += "{0} {1} amount: {2}, total: {3}\n".format(o['type'].capitalize(), coin, o['amount'], o['total'])
                    else:
                        for old_o in orders[coin]:
                            if old_o != o:
                                new += "{0} {1} amount: {2}, total: {3}\n".format(o['type'].capitalize(), coin, o['amount'], o['total'])

            for coin in new_orders:
                for o in new_orders[coin]:
                    pending += "{0} {1} amount: {2}, total: {3}\n".format(o['type'].capitalize(), coin, o['amount'], o['total'])

            message = ""
            if completed != "":
                message += "Completed or canceled orders:\n"
                message += completed
                message += "\n"

            if new != "":
                message += "New orders:\n"
                message += new
                message += "\n"

            if pending != "":
                message += "Pending orders:\n"
                message += pending
                message += "\n"

            if message != "":
                message += "Total balance: {0:.2f} USDT".format(sum([coin['usdtValue'] for coin in balance]))
                print("---------------------------")
                print(datetime.datetime.now())
                print(message)
                pushover.send(message)

            orders = new_orders

        time.sleep(10)


def balance_thread():
    if not os.path.isfile("mqtt_config.txt"):
        raise Exception("MQTT is not configured. "
                        "Create mqtt_config.txt with first line mqtt server IP address and "
                        "second line with user name and"
                        "third line with your password and"
                        "forth line with your topic for account balance.")

    with open("mqtt_config.txt") as fp:
        ip = fp.readline().strip()
        user = fp.readline().strip()
        password = fp.readline().strip()
        topic = fp.readline().strip()

    while True:
        balance = exchange.get_balance()
        publish.single(topic,
                       payload="{0}".format(sum([coin['usdtValue'] for coin in balance])),
                       qos=0,
                       retain=True,
                       hostname=ip,
                       port=1883,
                       client_id="",
                       keepalive=60,
                       will=None,
                       auth={'username': user, 'password': password},
                       tls=None)

        time.sleep(20)


def server_forever():
    while True:
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sends notifications via PushOver app https://pushover.net/.'
                                                 'Or via MQTT protocol http://mqtt.org/')
    parser.add_argument('-ab', dest='balance', action='store_true', help='Sends account balance to MQTT server.')
    parser.add_argument('-oc', dest='orders_change', action='store_true', help='Sends notification about exchange orders change.')

    args = parser.parse_args()

    if args.balance:
        t = threading.Thread(target=balance_thread)
        t.daemon = True
        t.start()

    if args.orders_change:
        t = threading.Thread(target=orders_change_thread)
        t.daemon = True
        t.start()

    if args.balance or args.orders_change:
        server_forever()
