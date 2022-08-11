from django.shortcuts import render
from django.http import HttpResponse

import multiprocessing
from multiprocessing import Pool
from django import db
import time
import pandas as pd
import django
import statistics
from .import multiprocess_work
from .import update_mlb_data
from .import simulation
from .import multiprocess_work as mp
from .import bovada
import pickle


from .models import Course

# Create your views here.


def index(request):
    things = Course.objects
    return render(request, 'mlb/index.html', {'things': things})


def update_page(request):
    # update_mlb_data.update_completed_games()
    # update_mlb_data.update_upcoming_games()
    # simulation.mp_prepare_upcoming_player_data()
    # simulation.analyze_predictions_table()
    # simulation.analyze_pitcher_simulations(506433)
    start = time.time()
    simulation.process_batters([572041])
    end = time.time()
    total = int(round(end - start))
    print("ended in " + str(total) + " seconds")
    # bovada.refresh_bov_mlb_upcoming_games()
    return render(request, 'mlb/update_page.html')


def reset_test_tables(request):
    update_mlb_data.reset_test_tables()
    return render(request, 'mlb/reset_test_tables.html')


def my_view(request):

    start = time.time()
    # this is a list of dictionaries for each element to simulate
    prepared_data = simulation.mp_prepare_upcoming_player_data()
    print("items to process " + str(len(prepared_data)))
    print("starting multiprocessing section")

    # create a unique identifier for each item like a primary key
    pk_prepared_data = []
    x = 0
    for di in prepared_data:
        pk_prepared_data.append({x: di})
        x += 1

    # pull out each prev_value and maintain unique identifier
    pk_prev_values = []
    for di in pk_prepared_data:
        key = list(di.keys())[0]
        values = di[key]['prev_values']
        pk_prev_values.append({key: values})

    # last tested, 22 cores seemed to be optimal
    cores = multiprocessing.cpu_count()
    if cores > 26:
        pool = Pool(processes=22)
    elif cores < 3:
        pool = Pool(processes=1)
    else:
        pool = Pool(processes=int(round(cores/2)))

    # the code to split into the different processes
    # TODO use a for loop to batch the splitting of processes and provide progress updates update roughly 5 - 10 seconds
    sim_values = pool.map(mp.run_monte_carlo_sim, pk_prev_values)
    print(len(sim_values))
    total = int(round(time.time() - start))
    print("ending multiprocessing section " + str(total) + " seconds")

    # time to insert new sim values into the prepared data.
    # remove list aspect of sim_values
    sim_values_di = {}
    for v in sim_values:
        pk = list(v.keys())[0]
        sim_di = v[pk]
        sim_values_di.update({pk: sim_di})

    # insert new items into previous dictionary
    for pk_di in pk_prev_values:
        pk = list(pk_di.keys())[0]
        sim_di = sim_values_di[pk]
        pk_prepared_data[pk][pk].update({'prev_values': sim_di['prev_values']})
        pk_prepared_data[pk][pk].update({'prev_avg': sim_di['prev_avg']})
        pk_prepared_data[pk][pk].update({'prev_st_dev': sim_di['prev_st_dev']})
        pk_prepared_data[pk][pk].update({'sim_values': sim_di['sim_values']})
        pk_prepared_data[pk][pk].update({'sim_avg': sim_di['sim_avg']})
        pk_prepared_data[pk][pk].update({'sim_st_dev': sim_di['sim_st_dev']})

    # remove pk aspect of data but keep as list
    finalized_data = []
    for data in pk_prepared_data:
        pk = list(data.keys())[0]
        finalized_data.append(data[pk])

    # update the table with new information
    simulation.mp_update_player_simulations_table(finalized_data)

    end = time.time()
    total = int(round(end - start))
    print("ended in " + str(total) + " seconds")
    return HttpResponse("SUCCESS")


"""  This is a working version that i am going to try to improve works with the pitchers
def my_view(request):

    start = time.time()
    # this is a list of dictionaries for each element to simulate
    prepared_data = simulation.mp_prepare_upcoming_player_data()
    print("items to process " + str(len(prepared_data)))
    print("starting multiprocessing section")

    # create a unique identifier for each item like a primary key
    pk_prepared_data = []
    x = 0
    for di in prepared_data:
        pk_prepared_data.append({x: di})
        x += 1

    # pull out each prev_value and maintain unique identifier
    pk_prev_values = []
    for di in pk_prepared_data:
        key = list(di.keys())[0]
        values = di[key]['prev_values']
        pk_prev_values.append({key: values})

    # last tested, 22 cores seemed to be optimal
    cores = multiprocessing.cpu_count()
    if cores > 26:
        pool = Pool(processes=22)
    elif cores < 3:
        pool = Pool(processes=1)
    else:
        pool = Pool(processes=int(round(cores/2)))

    # the code to split into the different processes
    # TODO use a for loop to batch the splitting of processes and provide progress updates update roughly 5 - 10 seconds
    sim_values = pool.map(mp.run_monte_carlo_sim, pk_prev_values)
    print(len(sim_values))
    total = int(round(time.time() - start))
    print("ending multiprocessing section " + str(total) + " seconds")

    # time to insert new sim values into the prepared data.
    # remove list aspect of sim_values
    sim_values_di = {}
    for v in sim_values:
        pk = list(v.keys())[0]
        sim_di = v[pk]
        sim_values_di.update({pk: sim_di})

    # insert new items into previous dictionary
    for pk_di in pk_prev_values:
        pk = list(pk_di.keys())[0]
        sim_di = sim_values_di[pk]
        pk_prepared_data[pk][pk].update({'prev_values': sim_di['prev_values']})
        pk_prepared_data[pk][pk].update({'prev_avg': sim_di['prev_avg']})
        pk_prepared_data[pk][pk].update({'prev_st_dev': sim_di['prev_st_dev']})
        pk_prepared_data[pk][pk].update({'sim_values': sim_di['sim_values']})
        pk_prepared_data[pk][pk].update({'sim_avg': sim_di['sim_avg']})
        pk_prepared_data[pk][pk].update({'sim_st_dev': sim_di['sim_st_dev']})

    # remove pk aspect of data but keep as list
    finalized_data = []
    for data in pk_prepared_data:
        pk = list(data.keys())[0]
        finalized_data.append(data[pk])

    # update the table with new information
    simulation.mp_update_player_simulations_table(finalized_data)

    end = time.time()
    total = int(round(end - start))
    print("ended in " + str(total) + " seconds")
    return HttpResponse("SUCCESS")
"""
