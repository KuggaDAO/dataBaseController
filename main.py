# -- coding: utf-8 --
import networkx as nx
import networkx.algorithms.community as nx_comm
import matplotlib.pyplot as plt
import numpy as np
import cProfile, pstats

import pandas as pd
from ruamel import yaml

from Analyze import *
from datetime import datetime

# load attributes
with open('./attributes.yaml', 'r') as f:
    configs = yaml.load(f, yaml.Loader)
apikey = "eDKGyoUbdjxgcNvUV-gvwTrLPkaBnleQ"
addresses = configs['contracts']['MEDIUM']


#NetworkAnalyzer.get_num_from_dict(addresses, apikey, 10)
#networkAnalyzer.apply_all_and_output(addresses, DataFetcher.give_transaction_variety, 'var_med.csv')
#print(NetworkAnalyzer.give_clustering("./transaction_data/PLU10000.csv"))

y, x = NetworkAnalyzer.comm_num_time_scatter()
plt.scatter(x, y)
plt.gca().invert_xaxis()
plt.show()
"""
# the part that plots community numbers.
y, x = NetworkAnalyzer.comm_num_series()
fig, ax = plt.subplots()
# ax.scatter(x, y)

# the part that plots all time data
times = []
xx = []
for i in range(1, 1066):
    df = pd.read_csv("./transaction_data/1000/{}.csv".format(i))
    if len(df) == 1000:
        exec("s = " + df['metadata'][999])
        time = datetime.strptime(s['blockTimestamp'], r"%Y-%m-%dT%H:%M:%S.%fZ")  # fit in time data
        times.append(time)
        xx.append(i)
ax2 = ax.twinx()
# ax2.scatter(xx, times, color="red")

times_x = []
for i in x:
    times_x.append(times[i])
ax.scatter(times_x, y)
plt.show()
"""


"""
# the part that plots degree frequencies
fig, ax = plt.subplots()
n, bins_limits, patches = ax.hist(y, bins=100)
ax.plot(bins_limits[:100], n)
plt.show()
"""

"""
# the part that calculate degree frequencies
avg = sum(y)/len(y)
up_bound = avg
low_bound = avg
while True:
    up_bound += 0.1
    low_bound -= 0.1
    counter = 0
    for i in y:
        if up_bound > i > low_bound:
            counter += 1
    print("in {0} and {1} ratio: {2}".format(up_bound, low_bound, counter/len(y)))
    if up_bound > 30:
        break
"""

"""
# the part that gets all transaction data
f = open("adr.txt", "r")
adrs = f.read().split()
DataFetcher.get_num_from_list(adrs, apikey, 5, reverse=True)
"""
