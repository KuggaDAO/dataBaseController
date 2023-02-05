# test file, do not run #

import re
import pandas
import matplotlib.pyplot as plt
import numpy as np
import emd
from datetime import date, timedelta
from scipy.fft import rfft, rfftfreq


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


start_date = date(2021, 5, 4)
end_date = date(2022, 11, 27)
it = iter(daterange(start_date, end_date))
d = next(it)
p = pandas.read_csv('BANK.csv')
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


imf = emd.sift.sift(np.array(datecount[1]), max_imfs=8)
print(imf.shape)
emd.plotting.plot_imfs(imf)
plt.show()
