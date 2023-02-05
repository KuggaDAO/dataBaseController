import pandas as pd
import networkx as nx
import networkx.algorithms.community as nx_comm
import matplotlib.pyplot as plt
import numpy as np
import cProfile
import pstats
from cdlib import algorithms


def give_profiler(f, G):
    profiler = cProfile.Profile()
    profiler.enable()
    result = f(G)
    profiler.disable()
    stats = pstats.Stats(profiler)
    return stats


def read_data():
    df = pd.read_csv("BANK.csv")
    df["weight"] = [a for a in df["value"]]
    G = nx.from_pandas_edgelist(df, source="from", target="to", edge_attr="weight")
    return G


def cal_gn(G, limit=float('inf')):
    comm = []
    counter = 0
    for nodes in nx.algorithms.community.centrality.girvan_newman(G):
        comm.append(list(nodes))
        counter += 1
        if counter >= limit:
            break
    return comm


def generate_graph(node_num):
    G = nx.barabasi_albert_graph(n=node_num, m=2, initial_graph=None)
    return G


def plot_log(x, y):
    plt.plot(x, y)
    plt.grid()
    plt.yscale('log')
    plt.xscale('log')


def test():
    y = []
    x = []
    for i in range(2, 10):
        G = generate_graph(2**i)
        s = give_profiler(cal_gn, G)
        #nx_comm.louvain_communities, algorithms.walktrap, cal_gn
        x.append(2**i)
        print(s.total_tt)
        y.append(s.total_tt)
    plot_log(x, y)
    plt.xlabel('node number')
    plt.ylabel('time(seconds)')
    plt.title('girvan_newman time consumption on SF network')
    plt.show()



test()
