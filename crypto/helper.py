import exchange
from tkinter import *
import PIL.Image
import PIL.ImageTk

TEMP_FILE_BEFORE = "_before_temp.png"
TEMP_FILE_AFTER = "_after_temp.png"


def calculate_difference_in_percent(first, second):
    return calculate_difference(first, second) * 100


def calculate_difference(first, second):
    if first != 0:
        return float((second - first)/first)
    else:
        return float((second - first))


def visualise(first, second, title):
    ymin = min([float(d["low"]) for d in first + second])
    ymax = max(([float(d["high"]) for d in first + second]))

    exchange.plot_chart_data(first, title, TEMP_FILE_BEFORE, ymin, ymax)
    exchange.plot_chart_data(second, title, TEMP_FILE_AFTER, ymin, ymax)

    root = Tk()

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

    root.geometry('%dx%d+%d+%d' % (1400, 570, 400, 300))
    root.mainloop()