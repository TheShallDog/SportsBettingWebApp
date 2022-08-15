from .models import MlbPlayer
from .models import MlbAtBat
from .models import MlbGame
from .models import MlbPlayerSimulations
from .models import MlbUpcomingPlayers
from .models import MlbBovadaUpcomingBatters
from .models import MlbBovadaUpcomingPitchers
from .models import MlbBovadaPitchersPostSimData
from .models import MlbBovadaPitchersBetComparison
from django.db.models import Q
from multiprocessing import Pool
from .import multiprocess_work as mp
import datetime
import time
import math
import pickle


def get_upcoming_pitchers():
    probable_pitchers = MlbUpcomingPlayers.objects.filter(position_type='Pitcher')\
                                                  .values_list('player_id', flat=True).distinct()
    probable_pitchers = list(filter(None, probable_pitchers))  # remove None values
    print(len(probable_pitchers))
    return probable_pitchers


def get_upcoming_batters():
    probable_batters = MlbUpcomingPlayers.objects.exclude(position_type='Pitcher')\
                                                  .values_list('player_id', flat=True).distinct()
    probable_batters = list(filter(None, probable_batters))  # remove None values
    print(len(probable_batters))
    return probable_batters


def get_upcoming_bovada_pitchers():
    pitchers = MlbBovadaUpcomingPitchers.objects.values_list('player_id', flat=True).distinct()
    pitchers = list(filter(None, pitchers))  # remove None values
    return pitchers


def get_upcoming_bovada_batters():
    batters = MlbBovadaUpcomingBatters.objects.values_list('player_id', flat=True).distinct()
    batters = list(filter(None, batters))  # remove None values
    return batters


def get_time_frames(input_list):
    list_length = len(input_list)
    if list_length < 10:
        return False

    max_possible_sims = int(math.floor(list_length / 2))
    max_sims = max_possible_sims if max_possible_sims <= 120 else 120
    temp_length = 5
    time_frames = []
    while temp_length < max_sims:
        time_frames.append(temp_length)
        temp_length *= 2

    time_frames.append(max_sims)

    return time_frames


def mp_prepare_upcoming_player_data():
    probable_pitchers = get_upcoming_pitchers()
    probable_batters = []  # get_upcoming_batters() - need to optimize or test length of running sim

    start = time.time()

    processed_pitchers = process_pitchers(probable_pitchers)
    processed_batters = process_batters(probable_batters)

    all_processed_players = processed_pitchers + processed_batters
    print("all processed players simulations to run")
    print(len(all_processed_players))
    print("all processed pitchers simulations to run")
    print(len(processed_pitchers))
    print("all processed batters simulations to run")
    print(len(processed_batters))
    print("processing took " + str(round(time.time() - start)) + " seconds")
    return all_processed_players


def process_batters(batters):
    stats = ['homerun', 'stolen_base', 'hit', 'run', 'rbi', 'bases']
    stat_filters = ['none', 'home', 'away']

    batter_pre_sim_complete_di_li = []

    for batter in batters:
        player_name = MlbPlayer.objects.get(pk=batter).full_name
        print(player_name)

        # get queryset of at_bats where they have a participated at_bat in order of most recent first
        at_bats_played_qs = MlbAtBat.objects.filter(batter_id=batter) | \
                            MlbAtBat.objects.filter(scoring_player_1=batter) | \
                            MlbAtBat.objects.filter(scoring_player_2=batter) | \
                            MlbAtBat.objects.filter(scoring_player_3=batter) | \
                            MlbAtBat.objects.filter(scoring_player_4=batter) | \
                            MlbAtBat.objects.filter(base_stealer_1=batter) | \
                            MlbAtBat.objects.filter(base_stealer_2=batter) | \
                            MlbAtBat.objects.filter(base_stealer_3=batter)

        played_game_ids_li = at_bats_played_qs.values_list('game_id', flat=True).distinct()
        played_games_ordered_qs = MlbGame.objects.filter(pk__in=played_game_ids_li).order_by('-game_date')

        # turn the queryset into an ordered list
        ordered_game_ids_li = []
        for game in played_games_ordered_qs:
            ordered_game_ids_li.append(int(game.game_id))

        game_cap = 82  # TODO - try to optimize everything else to allow this to be as many as possible
        temp_di = {'player_id': batter,
                   'player_name': player_name,
                   'ordered_game_ids': ordered_game_ids_li[:game_cap],
                   'stats': stats,
                   'stat_filters': stat_filters}

        # this method will return a list of dictionaries containing the full stats for each stat and filter by game
        start = time.time()
        print("start processing batter stats")
        temp_li = process_batter_stats(temp_di)
        print("finish processing batter stats in " + str(round(time.time() - start, 2)) + " seconds")

        # this loop takes less than 0.00 seconds to complete - would still love to get rid of it
        processed_batter_stats_di_li = []
        for di in temp_li:
            processed_batter_stats_di_li.append(di)

        # this method expands on the previous to break them down by individual timeframes
        # and with their respective values
        start = time.time()
        print("start processing player timeframes")
        temp_li = process_player_timeframes(processed_batter_stats_di_li)
        for di in temp_li:
            batter_pre_sim_complete_di_li.append(di)
        print("finishing processing timeframes in " + str(round(time.time() - start, 2)) + " seconds")

    return batter_pre_sim_complete_di_li


def process_pitchers(pitchers):
    # TODO earned runs will be flawed and will need to add in the at_bat table a column for
    #  earned run against - will not be currently calculating it,
    #  also not sure what bovada considers a pitching out so i wont be calculating that either,
    #  finally look into recording walks maybe through event_type
    stats = ['strikeouts', 'hits_allowed']
    stat_filters = ['none', 'home', 'away']

    pitcher_pre_sim_complete_di_li = []

    for pitcher in pitchers:
        player_name = MlbPlayer.objects.get(pk=pitcher).full_name

        # get queryset of games where they start in order of most recent first
        started_games_qs = MlbAtBat.objects.filter(pitcher_id=pitcher).filter(inning=1).filter(lineup_position=0)
        started_games_ids_qs = started_games_qs.values_list('game_id', flat=True).distinct()
        started_games_ordered_qs = MlbGame.objects.filter(pk__in=started_games_ids_qs).order_by('-game_date')

        # turn the queryset into an ordered list
        started_game_ids_li = []
        for game in started_games_ordered_qs:
            started_game_ids_li.append(int(game.game_id))

        temp_di = {'player_id': pitcher,
                   'player_name': player_name,
                   'ordered_game_ids': started_game_ids_li,
                   'stats': stats,
                   'stat_filters': stat_filters}

        # this method will return a list of dictionaries containing the full stats for each stat and filter by game
        processed_pitcher_stats_di_li = []
        temp_li = process_pitcher_stats(temp_di)
        for di in temp_li:
            processed_pitcher_stats_di_li.append(di)

        # this method expands on the previous to break them down by individual timeframes
        # and with their respective values
        temp_li = process_player_timeframes(processed_pitcher_stats_di_li)
        for di in temp_li:
            pitcher_pre_sim_complete_di_li.append(di)

    return pitcher_pre_sim_complete_di_li


def process_batter_stats(batter_di):
    batter_id = batter_di['player_id']
    player_name = batter_di['player_name']

    # need to do anything to only query the games list once for each game

    processed_game_stats_di_li = []
    for game_id in batter_di['ordered_game_ids']:
        processed_game_stats = {'game_id': game_id}

        players_impacted_at_bats = MlbAtBat.objects.filter(game_id=game_id)\
                                                   .filter(Q(batter_id=batter_id) |
                                                           Q(scoring_player_1=batter_id) |
                                                           Q(scoring_player_2=batter_id) |
                                                           Q(scoring_player_3=batter_id) |
                                                           Q(scoring_player_4=batter_id) |
                                                           Q(base_stealer_1=batter_id) |
                                                           Q(base_stealer_2=batter_id) |
                                                           Q(base_stealer_3=batter_id))

        # query set that includes every at bat where batter was actually batting in game
        batting_at_bats = players_impacted_at_bats.filter(batter_id=batter_id)

        # query set that includes every non batting at bat where he made a play
        plays_at_bats_qs = players_impacted_at_bats.exclude(batter_id=batter_id)

        # check if this game was home or away for the batter, home bats second in each inning
        # setting a variable with this version of a call is faster than calling twice and checking
        inning_half = players_impacted_at_bats[:1].get().inning_half
        if inning_half == 'bottom':
            processed_game_stats.update({'home_or_away': 'home'})
        elif inning_half == 'top':
            processed_game_stats.update({'home_or_away': 'away'})

        homerun = batting_at_bats.filter(home_run=True).count()
        processed_game_stats.update({'homerun': homerun})

        stolen_bases = plays_at_bats_qs.filter(Q(base_stealer_1=batter_id) |
                                               Q(base_stealer_2=batter_id) |
                                               Q(base_stealer_3=batter_id)).count()
        processed_game_stats.update({'stolen_base': stolen_bases})

        """ commented out as it can be processed below with the bases calculation
        hit = batting_at_bats.filter(Q(single=True) |
                                     Q(double=True) |
                                     Q(triple=True) |
                                     Q(home_run=True)).count()
        processed_game_stats.update({'hit': hit})
        """

        run = plays_at_bats_qs.filter(Q(scoring_player_1=batter_id) |
                                      Q(scoring_player_2=batter_id) |
                                      Q(scoring_player_3=batter_id) |
                                      Q(scoring_player_4=batter_id)).count()
        processed_game_stats.update({'run': run})

        rbi = sum(batting_at_bats.values_list('rbi', flat=True))
        processed_game_stats.update({'rbi': rbi})

        # if we changed the at_bats table to have the value for each of these than it could sum like RBI and using ors
        singles = batting_at_bats.filter(single=True).count()
        doubles = batting_at_bats.filter(double=True).count()
        triples = batting_at_bats.filter(triple=True).count()
        home_runs = batting_at_bats.filter(home_run=True).count()
        bases = singles + (doubles * 2) + (triples * 3) + (home_runs * 4)
        processed_game_stats.update({'bases': bases})
        hits = singles + doubles + triples + home_runs
        processed_game_stats.update({'hit': hits})

        processed_game_stats_di_li.append(processed_game_stats)

    # this set of loops takes less than 0.00 seconds to complete - thought I needed to pull running
    # the game out of the bottom of the loop but turns out this is fine.
    processed_batter_stats = []
    for stat in batter_di['stats']:
        for stat_filter in batter_di['stat_filters']:
            ordered_games_by_filter_li = []
            ordered_cumulative_stat_by_filter_li = []
            for game_di in processed_game_stats_di_li:

                match stat_filter:
                    case 'none':
                        ordered_games_by_filter_li.append(game_di['game_id'])
                        ordered_cumulative_stat_by_filter_li.append(game_di[stat])
                    case 'home':
                        if game_di['home_or_away'] == 'home':
                            ordered_games_by_filter_li.append(game_di['game_id'])
                            ordered_cumulative_stat_by_filter_li.append(game_di[stat])
                    case 'away':
                        if game_di['home_or_away'] == 'away':
                            ordered_games_by_filter_li.append(game_di['game_id'])
                            ordered_cumulative_stat_by_filter_li.append(game_di[stat])

            time_frames_li = get_time_frames(ordered_cumulative_stat_by_filter_li)

            processed_batter_stats.append({'player_id': batter_id,
                                           'player_name': player_name,
                                           'games': ordered_games_by_filter_li,
                                           'values': ordered_cumulative_stat_by_filter_li,
                                           'stat': stat,
                                           'filters': stat_filter,
                                           'time_frames': time_frames_li})

    return processed_batter_stats


# TODO optimize like the batter stats querysets
def process_pitcher_stats(pitcher_di):
    pitcher_id = pitcher_di['player_id']
    player_name = pitcher_di['player_name']

    # need to do anything to only query the games list once for each game
    processed_game_stats_di_li = []
    for game_id in pitcher_di['ordered_game_ids']:
        processed_game_stats = {}
        processed_game_stats.update({'game_id': game_id})

        pitching_at_bats = MlbAtBat.objects.filter(game_id=game_id).filter(pitcher_id=pitcher_id)

        # check if this game was home or away for the pitcher, home pitches first in each inning
        if pitching_at_bats[0].inning_half == 'bottom':
            processed_game_stats.update({'home_or_away': 'away'})
        elif pitching_at_bats[0].inning_half == 'top':
            processed_game_stats.update({'home_or_away': 'home'})

        strikeouts = pitching_at_bats.filter(strikeout=True).count()
        processed_game_stats.update({'strikeouts': strikeouts})

        hit_qs = pitching_at_bats.filter(single=True) | \
                 pitching_at_bats.filter(double=True) | \
                 pitching_at_bats.filter(triple=True) | \
                 pitching_at_bats.filter(home_run=True)
        hits_allowed = hit_qs.count()
        processed_game_stats.update({'hits_allowed': hits_allowed})

        processed_game_stats_di_li.append(processed_game_stats)

    # TODO need to find a way to only loop through these games once.
    #  also need to cap the total games to just over the max amount
    processed_pitcher_stats = []
    for stat in pitcher_di['stats']:
        for stat_filter in pitcher_di['stat_filters']:
            ordered_games_by_filter_li = []
            ordered_cumulative_stat_by_filter_li = []
            for game_di in processed_game_stats_di_li:

                match stat_filter:
                    case 'none':
                        ordered_games_by_filter_li.append(game_di['game_id'])
                        ordered_cumulative_stat_by_filter_li.append(game_di[stat])
                    case 'home':
                        if game_di['home_or_away'] == 'home':
                            ordered_games_by_filter_li.append(game_di['game_id'])
                            ordered_cumulative_stat_by_filter_li.append(game_di[stat])
                    case 'away':
                        if game_di['home_or_away'] == 'away':
                            ordered_games_by_filter_li.append(game_di['game_id'])
                            ordered_cumulative_stat_by_filter_li.append(game_di[stat])

            time_frames_li = get_time_frames(ordered_cumulative_stat_by_filter_li)

            processed_pitcher_stats.append({'player_id': pitcher_id,
                                            'player_name': player_name,
                                            'games': ordered_games_by_filter_li,
                                            'values': ordered_cumulative_stat_by_filter_li,
                                            'stat': stat,
                                            'filters': stat_filter,
                                            'time_frames': time_frames_li})

    return processed_pitcher_stats


def process_player_timeframes(processed_player_stats_di_li):

    data = []
    for di in processed_player_stats_di_li:
        # checks if the stat and filter combo have enough time frames to run a sim
        # timeframe will be false if none available
        if not di['time_frames']:
            continue

        time_frames = di['time_frames']
        player_id = di['player_id']
        player_name = di['player_name']
        statistic = di['stat']
        stat_filters = di['filters']
        sim_values = None
        sim_avg = None
        sim_st_dev = None
        prev_avg = None
        prev_st_dev = None

        for time_interval in time_frames:
            # TODO check that this simulation doesnt currently exist in our simulated numbers table
            # all of these need to reset for every time interval
            time_frame = time_interval
            game_id = None
            actual_value = None

            x = 0
            while x <= time_interval:
                # starting at zero allows us to go ahead and create a sim set for the next future game based
                # on current data, therefore when game = None that will be our future info

                if x > 0:
                    game_id = di['games'][x - 1]
                    actual_value = di['values'][x - 1]

                # creates a list of just the previous statistics from the asked for timeframe and
                # doesn't include the current games stat
                prev_values = di['values'][x:time_interval + x]
                # will calculate mean and st dev in simulation

                data.append({'player_id': player_id,
                             'player_name': player_name,
                             'game_id': game_id,
                             'statistic': statistic,
                             'time_frame': time_frame,
                             'stat_filters': stat_filters,
                             'prev_values': prev_values,
                             'prev_avg': prev_avg,
                             'prev_st_dev': prev_st_dev,
                             'sim_values': sim_values,
                             'sim_avg': sim_avg,
                             'sim_st_dev': sim_st_dev,
                             'actual_value': actual_value})
                x += 1

    return data


def mp_update_player_simulations_table(data):
    start = time.time()
    print("starting to delete then update player simulation table")

    MlbPlayerSimulations.objects.all().delete()
    for d in data:
        row = MlbPlayerSimulations(player_id=d['player_id'],
                                   player_name=d['player_name'],
                                   game_id=d['game_id'],
                                   statistic=d['statistic'],
                                   time_frame=d['time_frame'],
                                   stat_filters=d['stat_filters'],
                                   prev_values=d['prev_values'],
                                   prev_avg=d['prev_avg'],
                                   prev_st_dev=d['prev_st_dev'],
                                   sim_values=d['sim_values'],
                                   sim_avg=d['sim_avg'],
                                   sim_st_dev=d['sim_st_dev'],
                                   actual_value=d['actual_value'],
                                   )
        row.save()

    print("finished updating player simulation table in " + str(round(time.time()-start)) + " seconds")


def analyze_pitcher_simulations():
    pitcher_ids = get_upcoming_bovada_pitchers()
    prepped_for_db_table_di_li = []

    simulation_group_list = []
    x = 1
    print(len(pitcher_ids))
    for pitcher_id in pitcher_ids[7:18]:
        player_id = pitcher_id
        player_name = MlbPlayer.objects.get(player_id=pitcher_id).full_name
        print(x)
        x += 1
        print(player_name)
        team_id = MlbPlayer.objects.get(player_id=pitcher_id).current_team.team_id

        # get each unique stat that is stored in simulated data for this pitcher
        player_query_set = MlbPlayerSimulations.objects.filter(player_id=pitcher_id)
        stat_query_set = player_query_set \
            .values_list('statistic', flat=True) \
            .distinct()

        # get each unique filter that is stored in simulated data for each stat
        for stat in stat_query_set:
            filter_query_set = player_query_set \
                .filter(statistic=stat) \
                .values_list('stat_filters', flat=True) \
                .distinct()

            # if there is not bovada data for this pitcher and stat then no need to process it
            bovada_qs = MlbBovadaUpcomingPitchers.objects.filter(player_id=pitcher_id).filter(stat=stat)
            if len(bovada_qs) == 1:
                bovada_obj = bovada_qs[0]
                over_line = bovada_obj.over_line
                over_odds = bovada_obj.over_odds
                under_line = bovada_obj.under_line
                under_odds = bovada_obj.under_odds
            else:
                continue

            # get each unique time interval that is stored in simulated data for each filter
            for stat_filter in filter_query_set:
                time_frame_query_set = player_query_set \
                    .filter(statistic=stat) \
                    .filter(stat_filters=stat_filter) \
                    .values_list('time_frame', flat=True) \
                    .distinct()
                # get all table items that are in the current time interval
                for time_interval in time_frame_query_set:
                    query_set = player_query_set \
                        .filter(statistic=stat) \
                        .filter(stat_filters=stat_filter) \
                        .filter(time_frame=time_interval) \
                        .exclude(actual_value=None)  # do not want to include the future prediction when backtesting

                    values_list = []
                    for item in query_set:
                        # have to unpickle values here to allow them to be multi-processed
                        values_list.append({'sim_value': pickle.loads(item.sim_values),
                                            'actual_value': item.actual_value})

                    simulation_group_list.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'team_id': team_id,
                                                  'stat': stat,
                                                  'stat_filter': stat_filter,
                                                  'time_interval': time_interval,
                                                  'values': values_list,
                                                  'over_line': over_line,
                                                  'over_odds': over_odds,
                                                  'under_line': under_line,
                                                  'under_odds': under_odds})

        # this can be multi-processed below
        # analyzed_group_di_li_li = []
        # for sim_group_di in simulation_group_list:
        #    analyzed_group_di_li_li.append(post_sim_analysis(sim_group_di))
        analyzed_group_di_li_li = run_post_sim_analysis(simulation_group_list)

        print("finished analyzing pitchers")
        for li in analyzed_group_di_li_li:
            for di in li:
                prepped_for_db_table_di_li.append(di)
        print("finished prepping pitcher data")

    print("Start updating table")
    update_bovada_pitcher_post_sim_data_table(prepped_for_db_table_di_li)
    print("Finished updating table")

    update_bovada_pitcher_bet_comparison_table()


def update_bovada_pitcher_bet_comparison_table():
    pitcher_ids = MlbBovadaPitchersPostSimData.objects.values_list('player_id', flat=True).distinct()

    for pitcher_id in pitcher_ids:
        pitcher_obj = MlbBovadaUpcomingPitchers.objects.filter(player_id=pitcher_id)[0]
        home_or_away = pitcher_obj.home_or_away  # need this to determine correct filter
        upcoming_game_id = pitcher_obj.game_id

        pitcher_obj_qs = MlbBovadaPitchersPostSimData.objects.filter(player_id=pitcher_id)
        statistics = pitcher_obj_qs.values_list('stat', flat=True).distinct()

        for stat in statistics:
            stat_obj_qs = pitcher_obj_qs.filter(stat=stat)
            bet_options = stat_obj_qs.values_list('bet_option', flat=True).distinct()

            for bet_option in bet_options:
                bet_obj_qs = stat_obj_qs.filter(bet_option=bet_option)

                filtered_qs = bet_obj_qs.filter(stat_filter='none') | \
                              bet_obj_qs.filter(stat_filter=home_or_away)

                best_stat_match_obj = filtered_qs.order_by('difference')[0]

                # create a list of all the best matches within each time interval that are below a confidence threshold
                # the first item will always be the best general match
                lowest_diff_by_filter_and_time_interval = [best_stat_match_obj]
                stat_filters = filtered_qs.values_list('stat_filter', flat=True).distinct()
                for stat_filter in stat_filters:
                    time_intervals = filtered_qs.filter(stat_filter=stat_filter)\
                                                .values_list('time_interval', flat=True)\
                                                .distinct()
                    for interval in time_intervals:
                        time_interval_qs = filtered_qs.filter(stat_filter=stat_filter)\
                                                      .filter(time_interval=interval)\
                                                      .order_by('difference')

                        best_match_obj = time_interval_qs[0]
                        if best_match_obj.difference > 0.05:  # TODO verify this confidence threshold
                            continue

                        lowest_diff_by_filter_and_time_interval.append(best_match_obj)

                expected_probability_li = []
                for obj in lowest_diff_by_filter_and_time_interval:
                    sim_values_li_pickled = MlbPlayerSimulations.objects.filter(player_id=obj.player_id)\
                                                                        .filter(statistic=obj.stat)\
                                                                        .filter(stat_filters=obj.stat_filter)\
                                                                        .filter(time_frame=obj.time_interval)\
                                                                        .filter(game_id=None)[:1].get().sim_values

                    sim_values_li = pickle.loads(sim_values_li_pickled)
                    expected_value = post_sim_expected_value(sim_values_li, obj)
                    expected_probability_li.append(expected_value)

                lowest_expected_prob = min(expected_probability_li)

                obj = lowest_diff_by_filter_and_time_interval[0]  # this is the best match
                bovada_implied_probability = calc_implied_probability(obj.bet_odds)
                sim_implied_probability = expected_probability_li[0]
                sim_implied_probability_rounded = round(sim_implied_probability * 100, 2)
                sim_bet_odds = calc_american_odds(sim_implied_probability)
                exp_value_per_unit = expected_value_per_unit(obj.bet_odds, sim_implied_probability)

                bet_rating = 'bad'
                if lowest_expected_prob > ((bovada_implied_probability/100) + .05):
                    bet_rating = 'primo'
                elif lowest_expected_prob > (bovada_implied_probability/100):
                    bet_rating = 'great'
                elif sim_implied_probability > (bovada_implied_probability/100):
                    bet_rating = 'good'

                row = MlbBovadaPitchersBetComparison(player_id=obj.player_id,
                                                     player_name=obj.player_name,
                                                     team_id=obj.team_id,
                                                     upcoming_game_id=upcoming_game_id,
                                                     stat=obj.stat,
                                                     bet_option=obj.bet_option,
                                                     bovada_bet_line=obj.bet_line,
                                                     bovada_bet_odds=obj.bet_odds,
                                                     bovada_implied_probability=bovada_implied_probability,
                                                     sim_bet_odds=sim_bet_odds,
                                                     sim_implied_probability=sim_implied_probability_rounded,
                                                     expected_value_per_unit=exp_value_per_unit,
                                                     bet_rating=bet_rating,
                                                     )
                row.save()
                print("-")

            # TODO run the post sim analysis for each future sim numbers for each of the generated good matches
            # also show difference numbers
            # then classify bets as bad, good, great, primo
            # bad is losing unit per bet based on best match,
            # good is + expected value per unit based on best match,
            # great is + expected value per unit even with lowest probability
            # primo is + expected value per unit even with lowest probability - difference
            # eventually track accuracy of each category


def update_bovada_pitcher_post_sim_data_table(prepped_di_li):
    MlbBovadaPitchersPostSimData.objects.all().delete()
    for d in prepped_di_li:
        row = MlbBovadaPitchersPostSimData(player_id=d['player_id'],
                                           player_name=d['player_name'],
                                           team_id=d['team_id'],
                                           stat=d['stat'],
                                           stat_filter=d['stat_filter'],
                                           time_interval=d['time_interval'],
                                           sim_option=d['sim_option'],
                                           round_option=d['round_option'],
                                           bet_option=d['bet_option'],
                                           bet_line=d['bet_line'],
                                           bet_odds=d['bet_odds'],
                                           expected_prob_avg=d['expected_prob_avg'],
                                           actual_result_avg=d['actual_result_avg'],
                                           difference=d['difference'],
                                           )
        row.save()


def run_mlb_simulation():
    start = time.time()
    print("starting to prepare simulation data")

    prepared_data = mp_prepare_upcoming_player_data()

    print("finished preparing simulation data in " + str(round(time.time() - start)) + " seconds")

    start = time.time()
    print("starting simulations")

    pool = Pool(processes=28)
    simulated_data = pool.map(mp.run_monte_carlo_sim, prepared_data)

    print("finished simulations in " + str(round(time.time() - start)) + " seconds")

    mp_update_player_simulations_table(simulated_data)


def run_post_sim_analysis(simulation_group_list):
    print("begin multiprocess")
    pool = Pool(processes=28)
    analyzed_group_di_li_li = pool.map(mp.post_sim_analysis, simulation_group_list)
    print("finish multiprocess")
    return analyzed_group_di_li_li


# if you have nested lists of lists this will bring all items to one level
def flatten_list(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten_list(list_of_lists[0]) + flatten_list(list_of_lists[1:])
    return list_of_lists[:1] + flatten_list(list_of_lists[1:])


def calc_american_odds(og_odds):
    match og_odds:
        # calculating american odds from implied probability
        case n if 0 <= n < 1:
            if og_odds == 0:
                return 0
            if og_odds > .5:
                return round(((og_odds * 100) / (1 - og_odds)) * -1)
            if og_odds < .5:
                return round((100 / og_odds) - 100)
            if og_odds == .5:
                return 'EVEN'
        # calculating american odds from decimal odds
        case n if 1 < n < 100:
            match og_odds:
                case n if n >= 2:
                    return round((og_odds - 1) * 100)
                case n if n < 2:
                    return round(-100/(og_odds - 1))


def calc_implied_probability(american_odds):
    if american_odds == 'EVEN':
        return 50
    if american_odds < 0:
        return round(((-1*american_odds)/(-american_odds+100)) * 100, 2)
    if american_odds > 0:
        return round((100/(american_odds+100)) * 100, 2)


def expected_value_per_unit(bookie_odds, model_probability):
    bookie_decimal = 1

    if bookie_odds > 0:
        bookie_decimal = (bookie_odds/100) + 1
    elif bookie_odds < 0:
        bookie_decimal = (100/abs(bookie_odds)) + 1

    edge = (model_probability * bookie_decimal) - 1

    return edge


def post_sim_expected_value(sim_values_li, obj):
    sim_option = obj.sim_option
    round_option = obj.round_option
    bet_option = obj.bet_option
    bet_line = obj.bet_line
    expected_probability = None

    s_option_values_li = []
    match sim_option:
        case 'Raw':
            # case 'Raw' keeps the numbers the same
            s_option_values_li = sim_values_li

        case 'Zeroed':
            # all negative sim numbers = 0
            s_option_values_li = zeroed(sim_values_li)

        case 'Absolute Value':
            # all negative numbers absolute valued
            s_option_values_li = abs_value(sim_values_li)

        case 'Deleted':
            # all negative numbers removed
            s_option_values_li = removed(sim_values_li)

    r_option_values_li = []
    match round_option:
        case 'Raw':
            # case 'Raw' keeps the numbers the same
            r_option_values_li = s_option_values_li

        case 'Round':
            # all numbers rounded normally
            r_option_values_li = round_list(s_option_values_li)

        case 'Round Up':
            # all numbers rounded up to the nearest int
            r_option_values_li = round_up_list(s_option_values_li)

        case 'Round Down':
            # all numbers rounded down to the nearest int
            r_option_values_li = round_down_list(s_option_values_li)

    match bet_option:
        case 'Over':
            # determine expected value for over the line and compare to actual value
            count = sum(x > bet_line for x in r_option_values_li)
            expected_probability = count / len(r_option_values_li)

        case 'Under':
            # determine expected value for under the line and compare to actual value
            count = sum(x < bet_line for x in r_option_values_li)
            expected_probability = count / len(r_option_values_li)

    return expected_probability


def below_zero(li):
    new_li = []
    for x in li:
        if x < 0:
            new_li.append(x)
    return new_li


def equal_zero(li):
    new_li = []
    for x in li:
        if x == 0:
            new_li.append(x)
    return new_li


def zeroed(li):
    new_li = []
    for x in li:
        if x < 0:
            new_li.append(0)
        else:
            new_li.append(x)
    return new_li


def abs_value(li):
    new_li = []
    for x in li:
        if x < 0:
            new_li.append(abs(x))
        else:
            new_li.append(x)
    return new_li


def removed(li):
    new_li = []
    for x in li:
        if x >= 0:
            new_li.append(x)
    return new_li


def round_list(li):
    new_li = []
    for x in li:
        new_li.append(round(x))
    return new_li


def round_up_list(li):
    new_li = []
    for x in li:
        new_li.append(math.ceil(x))
    return new_li


def round_down_list(li):
    new_li = []
    for x in li:
        new_li.append(math.floor(x))
    return new_li
