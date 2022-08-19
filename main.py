import requests
import statsapi
import datetime
import numpy as np
import random
import statistics
from scipy.stats import norm
import time
import pyopencl as cl


def create_data():
    li = []
    for x in range(20):
        li.append(random.random())
    return li


def run_monte_carlo_sim(li):
    average = statistics.mean(li)
    st_dev = statistics.stdev(li)
    simulations = 10000  # took 83 second @ 10,000
    sim_list = []
    for x in range(simulations):
        sim_list.append(norm.ppf(random.random(),
                                 loc=average,
                                 scale=st_dev))
    return sim_list


def go():
    start = time.time()
    print("start")
    lis = []
    for i in range(100):
        lis.append(create_data())

    for elem in lis:
        print(run_monte_carlo_sim(elem))
    end = time.time()
    total = int(round(end - start))
    print("ended in " + str(total) + " seconds")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(statsapi.meta('statTypes'))
