import random
import statistics
import numpy as np
import time
from scipy.stats import norm
import pickle


def run_monte_carlo_sim(di):
    simulations = 10000

    key = list(di.keys())[0]
    values = di[key]
    # moving this math out here means I don't have to do it 10k times for each loop below reduce time by a third
    pickled_prev_values = pickle.dumps(values)
    prev_avg = statistics.mean(values)
    prev_st_dev = statistics.stdev(values)

    # most stats will have values, but some could all be zero  or all the same number created a st_dev of 0
    # and the sim fails.
    if prev_avg == 0 or prev_st_dev == 0:
        p_values = pickle.dumps(values)
        new_di = {key: {'sim_values': pickled_prev_values,
                        'sim_avg': prev_avg,
                        'sim_st_dev': prev_st_dev,
                        'prev_values': pickled_prev_values,
                        'prev_avg': prev_avg,
                        'prev_st_dev': prev_st_dev}}
    else:
        sim_list = []
        for x in range(simulations):
            sim_list.append(norm.ppf(random.random(),
                                     loc=prev_avg,
                                     scale=prev_st_dev))
        new_di = {key: {'sim_values': pickle.dumps(sim_list),
                        'sim_avg': statistics.mean(sim_list),
                        'sim_st_dev': statistics.stdev(sim_list),
                        'prev_values': pickled_prev_values,
                        'prev_avg': prev_avg,
                        'prev_st_dev': prev_st_dev}}
    return new_di
