import argparse
import exchange
import random
from tkinter import *
import PIL.Image
import PIL.ImageTk
import pickle
import os
import helper


TEMP_FILE_BEFORE = "_before_temp.png"
TEMP_FILE_AFTER = "_after_temp.png"
TRAINING_DB_FILE = "training_data_db.pkl"
RANGE = 10
RANGE_AFTER = 10


class TrainingData:
    def __init__(self):
        self.data = []
        self.feedback = ""  # "buy", "sell", "hold"
        self.currency_pair = ""  # "USDT_BTC"


def ask():
    currency_pair = "USDT_BTC"

    data = exchange.get_chart_data(currency_pair)
    while True:
        start = random.randint(0, len(data) - (RANGE + RANGE_AFTER) - 1)
        slice = data[start : start + RANGE]
        slice_after = data[start + RANGE : start + (RANGE + RANGE_AFTER)]

        ymin = min([float(d["low"]) for d in slice + slice_after])
        ymax = max(([float(d["high"]) for d in slice + slice_after]))

        exchange.plot_chart_data(slice, currency_pair, TEMP_FILE_BEFORE, ymin, ymax)
        exchange.plot_chart_data(slice_after, currency_pair, TEMP_FILE_AFTER, ymin, ymax)

        answer = _gui_question()
        if answer:
            td = TrainingData()
            td.data = slice
            td.feedback = answer
            td.currency_pair = currency_pair
            _save(td)
        else:
            break


def _gui_question():
    root = Tk()

    class _Answer:
        def __init__(self, root):
            self.answer = None
            self.root = root

        def buy_callback(self):
            self.answer = "buy"
            self.root.destroy()

        def sell_callback(self):
            self.answer = "sell"
            self.root.destroy()

        def hold_collback(self):
            self.answer = "hold"
            self.root.destroy()

    answer = _Answer(root)

    w = Label(root, text="Choose between: Buy, Sell, Hold")
    w.pack()

    image_frame = Frame(root)

    photo_before = PIL.ImageTk.PhotoImage(PIL.Image.open(TEMP_FILE_BEFORE))
    chart_before = Label(image_frame, image=photo_before)
    chart_before.image = photo_before
    chart_before.pack(fill=BOTH, side=LEFT)
    photo_after = PIL.ImageTk.PhotoImage(PIL.Image.open(TEMP_FILE_AFTER))
    chart_after = Label(image_frame, image=photo_after)
    chart_after.image = photo_after
    chart_after.pack(fill=BOTH, side=LEFT)
    image_frame.pack()

    button_frame = Frame(root)
    buy = Button(button_frame, text="buy", fg="green", command=answer.buy_callback)
    sell = Button(button_frame, text="sell", fg="red", command=answer.sell_callback)
    hold = Button(button_frame, text="hold", fg="black", command=answer.hold_collback)
    buy.pack(side=LEFT)
    sell.pack(side=LEFT)
    hold.pack(side=LEFT)
    button_frame.pack()

    root.geometry('%dx%d+%d+%d' % (1400, 570, 400, 300))
    root.mainloop()

    return answer.answer


def generate_automatic():
    currency_pairs = ["USDT_BTC", "USDT_ETH", "USDT_LTC", "USDT_ZEC", "USDT_ETC", "USDT_REP", "USDT_XMR", "USDT_STR", "USDT_DASH", "USDT_XRP"]

    all_data = []
    for currency_pair in currency_pairs:
        data = exchange.get_chart_data(currency_pair)
        all_data.append(data)
        print("Progress {2}: {0} / {1}".format(currency_pairs.index(currency_pair), len(currency_pairs), currency_pair))

    _save(all_data)


def _save(data):
    if not os.path.isfile(TRAINING_DB_FILE):
        all_data = []
    else:
        with open(TRAINING_DB_FILE, "rb") as fp:
            all_data = pickle.load(fp)

    all_data.append(data)

    with open(TRAINING_DB_FILE, "wb") as fp:
        pickle.dump(all_data, fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Training data generator.')
    parser.add_argument('-r', dest='remove', action='store_true', help='Remove existing training database.')
    parser.add_argument('-g', dest='generate', action='store_true', help='Generate training data.')
    parser.add_argument('-ag', dest='generate_automatic', action='store_true', help='Generates data automatically')

    args = parser.parse_args()

    if args.remove:
        if os.path.isfile(TRAINING_DB_FILE):
            os.unlink(TRAINING_DB_FILE)

    if args.generate:
        ask()

    if args.generate_automatic:
        generate_automatic()
