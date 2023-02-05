import re
import pandas
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta
from scipy.fft import rfft, rfftfreq


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_plot_x_y(filename):
    start_date = date(2021, 5, 4)
    end_date = date(2022, 11, 27)
    it = iter(daterange(start_date, end_date))
    d = next(it)
    p = pandas.read_csv(filename)
    datedata = p['metadata']
    datecount = [[str(d)], [0]]
    for date in datedata:
        dstr = d.strftime("%Y-%m-%d")
        if re.search(dstr, date):
            datecount[1][-1] += 1
        else:
            try:
                d = next(it)
                datecount[0].append(dstr)
                datecount[1].append(1)
            except StopIteration:
                break
    return datecount[0], datecount[1]


def plot_freq(filename):
    x_major_locator = plt.MultipleLocator(61)
    plt.gca().xaxis.set_major_locator(x_major_locator)
    plt.plot(*get_plot_x_y(filename))
    plt.show()


def plot_fft(filename):
    _, y = get_plot_x_y(filename)
    yf = rfft(y)
    xf = rfftfreq(len(y), 1)
    for i in range(len(xf)):
        xf[i] = 1 / xf[i]
    plt.plot(xf, np.abs(yf))
    plt.show()


plot_fft('../BANK.csv')
