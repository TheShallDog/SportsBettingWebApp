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


def morning_run(request):
    update_mlb_data.update_completed_games(recent=True, current=False, previous=False, previous_seasons=5)
    update_mlb_data.update_upcoming_games_and_players()
    bovada.refresh_bov_mlb_upcoming_player_tables()

    simulation.run_mlb_simulation()
    simulation.analyze_pitcher_simulations()
    simulation.update_bovada_pitcher_bet_comparison()

    return HttpResponse("SUCCESS")


def update_page(request):
    # update_mlb_data.update_completed_games(recent=True, current=False, previous=False, previous_seasons=5)
    # update_mlb_data.update_upcoming_games_and_players()
    # bovada.refresh_bov_mlb_upcoming_player_tables()
    # simulation.mp_prepare_upcoming_player_data()
    # simulation.analyze_pitcher_simulations()
    simulation.update_bovada_pitcher_bet_comparison()

    return render(request, 'mlb/update_page.html')


def reset_test_tables(request):
    update_mlb_data.reset_test_tables()
    return render(request, 'mlb/reset_test_tables.html')


def my_view(request):
    #  TODO Re-look into using the GPU to process this data.

    start = time.time()
    # this is a list of dictionaries for each element to simulate
    prepared_data = simulation.mp_prepare_upcoming_player_data()
    prepared_data_time_end = time.time()
    print("items to process " + str(len(prepared_data)))
    print("starting multiprocessing section")

    # last tested, 22 cores seemed to be optimal
    cores = multiprocessing.cpu_count()
    if cores > 30:
        pool = Pool(processes=28)  # my PC current using switched to 30 and shaved 1.5 mins on 14k processed
    elif cores < 3:
        pool = Pool(processes=1)
    else:
        pool = Pool(processes=int(round(cores/2)))

    # the code to split into the different processes
    # TODO use a for loop to batch the splitting of processes and provide progress updates update roughly 5 - 10 seconds
    simulated_data = pool.map(mp.run_monte_carlo_sim, prepared_data)
    print(len(simulated_data))
    total = int(round(time.time() - start))

    print("ending multiprocessing section " + str(total) + " seconds")
    print("preparing data took " + str(round(prepared_data_time_end-start)) + " seconds")

    # update the table with new information
    simulation.mp_update_player_simulations_table(simulated_data)

    end = time.time()
    total = int(round(end - start))
    print("ended in " + str(total) + " seconds")
    return HttpResponse("SUCCESS")
