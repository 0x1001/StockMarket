import exchange
import random
from tkinter import *
import PIL.Image
import PIL.ImageTk


TEMP_FILE_BEFORE = "_before_temp.png"
TEMP_FILE_AFTER = "_after_temp.png"


class TrainingData:
    data = {}
    feedback = ""  # "buy", "sell", "hold"
    currency_pair = ""  # "USDT_BTC"


def ask():
    RANGE = 10
    currency_pair = "USDT_BTC"

    data = exchange.get_chart_data(currency_pair)
    while True:
        start = random.randint(0, len(data) - 2 * RANGE - 1)
        slice = data[start : start + RANGE]
        slice_after = data[start + RANGE : start + 2 * RANGE]

        ymin = min([float(d["low"]) for d in slice + slice_after])
        ymax = max(([float(d["high"]) for d in slice + slice_after]))

        exchange.plot_chart_data(slice, currency_pair, TEMP_FILE_BEFORE, ymin, ymax)
        exchange.plot_chart_data(slice_after, currency_pair, TEMP_FILE_AFTER, ymin, ymax)

        answer = _gui_question()
        if answer:
            pass
        else:
            break


def _gui_question():
    root = Tk()

    class _answer:
        def __init__(self, root):
            self.ansswer = None
            self.root = root

        def buy_callback(self):
            self.ansswer = "buy"
            self.root.destroy()

        def sell_callback(self):
            self.ansswer = "sell"
            self.root.destroy()

        def hold_collback(self):
            self.ansswer = "hold"
            self.root.destroy()

    answer = _answer(root)

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

    return answer.ansswer
