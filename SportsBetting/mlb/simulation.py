from .models import MlbPlayer
from .models import MlbAtBat
from .models import MlbGame
from .models import MlbPlayerSimulations
from .models import MlbUpcomingPlayers
from .models import MlbBovadaUpcomingBatters
from .models import MlbBovadaUpcomingPitchers
from .models import MlbBovadaPitchersPostSimData
from .models import MlbBovadaPitchersBetComparison
import datetime
import time
import math
import pickle


def get_upcoming_pitchers():
    probable_pitchers = MlbUpcomingPlayers.objects.filter(position_type='Pitcher')\
                                                  .values_list('player_id', flat=True).distinct()
    probable_pitchers = list(filter(None, probable_pitchers))  # remove None values
    return probable_pitchers


def get_upcoming_batters():
    probable_batters = MlbUpcomingPlayers.objects.exclude(position_type='Pitcher')\
                                                  .values_list('player_id', flat=True).distinct()
    probable_batters = list(filter(None, probable_batters))  # remove None values
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
    start = time.time()
    probable_pitchers = get_upcoming_pitchers()
    probable_batters = []  # get_upcoming_batters()

    processed_pitchers = process_pitchers(probable_pitchers)
    processed_batters = process_batters(probable_batters)

    all_processed_players = processed_pitchers + processed_batters
    print("all processed players")
    print(len(all_processed_players))
    print("all processed pitchers")
    print(len(processed_pitchers))
    print("all processed batters")
    print(len(processed_batters))
    total = int(round(time.time() - start))
    print("processes took " + str(total) + " seconds")
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

        played_game_ids_qs = at_bats_played_qs.values_list('game_id', flat=True).distinct()
        played_games_ordered_qs = MlbGame.objects.filter(pk__in=played_game_ids_qs).order_by('-game_date')

        # turn the queryset into an ordered list
        ordered_game_ids_li = []
        for game in played_games_ordered_qs:
            ordered_game_ids_li.append(int(game.game_id))

        temp_di = {'player_id': batter,
                   'player_name': player_name,
                   'ordered_game_ids': ordered_game_ids_li,
                   'stats': stats,
                   'stat_filters': stat_filters}

        # this method will return a list of dictionaries containing the full stats for each stat and filter by game
        print("start processing batter stats")
        processed_batter_stats_di_li = []
        temp_li = process_batter_stats(temp_di)
        for di in temp_li:
            processed_batter_stats_di_li.append(di)
        print("finish processing batter stats")

        # this method expands on the previous to break them down by individual timeframes
        # and with their respective values
        print("start processing player_timeframes")
        temp_li = process_player_timeframes(processed_batter_stats_di_li)
        for di in temp_li:
            batter_pre_sim_complete_di_li.append(di)
        print("finishing processing player_timeframes")

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
        print(player_name)

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
        print("start processing pitcher stats")
        processed_pitcher_stats_di_li = []
        temp_li = process_pitcher_stats(temp_di)
        for di in temp_li:
            processed_pitcher_stats_di_li.append(di)
        print("finish processing pitcher stats")

        # this method expands on the previous to break them down by individual timeframes
        # and with their respective values
        print("start processing player_timeframes")
        temp_li = process_player_timeframes(processed_pitcher_stats_di_li)
        for di in temp_li:
            pitcher_pre_sim_complete_di_li.append(di)
        print("finished processing player_timeframes")

    return pitcher_pre_sim_complete_di_li


def process_batter_stats(batter_di):
    batter_id = batter_di['player_id']

    # need to do anything to only query the games list once for each game
    processed_game_stats_di_li = []
    for game_id in batter_di['ordered_game_ids']:
        processed_game_stats = {}
        processed_game_stats.update({'game_id': game_id})

        at_bats_in_game = MlbAtBat.objects.filter(game_id=game_id)

        # query set that includes every at bat, that was impacted by the batter in this game
        players_impacted_at_bats = at_bats_in_game.filter(batter_id=batter_id) | \
                                   at_bats_in_game.filter(scoring_player_1=batter_id) | \
                                   at_bats_in_game.filter(scoring_player_2=batter_id) | \
                                   at_bats_in_game.filter(scoring_player_3=batter_id) | \
                                   at_bats_in_game.filter(scoring_player_4=batter_id) | \
                                   at_bats_in_game.filter(base_stealer_1=batter_id) | \
                                   at_bats_in_game.filter(base_stealer_2=batter_id) | \
                                   at_bats_in_game.filter(base_stealer_3=batter_id)

        # query set that includes every at bat where batter was actually batting in game
        batting_at_bats = at_bats_in_game.filter(batter_id=batter_id)

        # query set that includes every non batting at bat where he made a play
        plays_at_bats_qs = at_bats_in_game.filter(scoring_player_1=batter_id) | \
                           at_bats_in_game.filter(scoring_player_2=batter_id) | \
                           at_bats_in_game.filter(scoring_player_3=batter_id) | \
                           at_bats_in_game.filter(scoring_player_4=batter_id) | \
                           at_bats_in_game.filter(base_stealer_1=batter_id) | \
                           at_bats_in_game.filter(base_stealer_2=batter_id) | \
                           at_bats_in_game.filter(base_stealer_3=batter_id)

        # check if this game was home or away for the batter, home bats second in each inning
        if players_impacted_at_bats[0].inning_half == 'bottom':
            processed_game_stats.update({'home_or_away': 'home'})
        elif players_impacted_at_bats[0].inning_half == 'top':
            processed_game_stats.update({'home_or_away': 'away'})

        homerun = batting_at_bats.filter(home_run=True).count()
        processed_game_stats.update({'homerun': homerun})

        stolen_bases_qs = plays_at_bats_qs.filter(base_stealer_1=batter_id) | \
                          plays_at_bats_qs.filter(base_stealer_2=batter_id) | \
                          plays_at_bats_qs.filter(base_stealer_3=batter_id)
        stolen_bases = stolen_bases_qs.count()
        processed_game_stats.update({'stolen_base': stolen_bases})

        hit_qs = batting_at_bats.filter(single=True) | \
                 batting_at_bats.filter(double=True) | \
                 batting_at_bats.filter(triple=True) | \
                 batting_at_bats.filter(home_run=True)
        hit = hit_qs.count()
        processed_game_stats.update({'hit': hit})

        run_qs = plays_at_bats_qs.filter(scoring_player_1=batter_id) | \
                  plays_at_bats_qs.filter(scoring_player_2=batter_id) | \
                  plays_at_bats_qs.filter(scoring_player_3=batter_id) | \
                  plays_at_bats_qs.filter(scoring_player_4=batter_id)
        run = run_qs.count()
        processed_game_stats.update({'run': run})

        rbi = sum(batting_at_bats.values_list('rbi', flat=True))
        processed_game_stats.update({'rbi': rbi})

        singles = batting_at_bats.filter(single=True).count()
        doubles = batting_at_bats.filter(double=True).count()
        triples = batting_at_bats.filter(triple=True).count()
        home_runs = batting_at_bats.filter(home_run=True).count()
        bases = singles + (doubles * 2) + (triples * 3) + (home_runs * 4)
        processed_game_stats.update({'bases': bases})

        processed_game_stats_di_li.append(processed_game_stats)

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
                                           'games': ordered_games_by_filter_li,
                                           'values': ordered_cumulative_stat_by_filter_li,
                                           'stat': stat,
                                           'filters': stat_filter,
                                           'time_frames': time_frames_li})

    return processed_batter_stats


def process_pitcher_stats(pitcher_di):
    pitcher_id = pitcher_di['player_id']

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
        statistic = di['stat']
        stat_filters = di['filters']
        game_id = None
        game_date = None
        actual_value = None
        sim_values = None
        sim_avg = None
        sim_st_dev = None
        prev_avg = None
        prev_st_dev = None

        for time_interval in time_frames:
            # TODO check that this simulation doesnt currently exist in our simulated numbers table
            time_frame = int(time_interval)

            x = 0
            while x <= time_interval:
                # starting at zero allows us to go ahead and create a sim set for the next future game based
                # on current data, therefore when game = None that will be our future info

                if x > 0:
                    game_id = di['games'][x - 1]
                    game_date = MlbGame.objects.get(game_id=game_id).game_date
                    actual_value = di['values'][x - 1]

                # creates a list of just the previous statistics from the asked for timeframe and
                # doesn't include the current games stat
                prev_values = di['values'][x:time_interval + x]
                # will calculate mean and st dev in simulation

                data.append({'player': player_id,
                             'game_id': game_id,
                             'game_date': game_date,
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
    for d in data:
        row = MlbPlayerSimulations(player=d['player'],
                                   game_id=d['game_id'],
                                   game_date=d['game_date'],
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


def analyze_pitcher_simulations():
    pitcher_ids = get_upcoming_bovada_pitchers()
    prepped_for_db_table_di_li = []

    simulation_group_list = []
    for pitcher_id in pitcher_ids[:2]:
        player_id = pitcher_id
        player_name = MlbPlayer.objects.get(player_id=pitcher_id).full_name
        team_id = MlbPlayer.objects.get(player_id=pitcher_id).current_team.team_id

        # get each unique stat that is stored in simulated data for this pitcher
        player_query_set = MlbPlayerSimulations.objects.filter(player=pitcher_id)
        stat_query_set = player_query_set \
            .values_list('statistic', flat=True) \
            .distinct()

        # get each unique filter that is stored in simulated data for each stat
        for stat in stat_query_set:
            filter_query_set = player_query_set \
                .filter(statistic=stat) \
                .values_list('stat_filters', flat=True) \
                .distinct()

            bovada_qs = MlbBovadaUpcomingPitchers.objects.filter(player_id=pitcher_id).filter(stat=stat)
            if len(bovada_qs) == 1:
                bovada_obj = bovada_qs[0]
            else:
                print("no or multiple bovada pitcher objects found")
                bovada_obj = None

            over_line = bovada_obj.over_line
            over_odds = bovada_obj.over_odds
            under_line = bovada_obj.under_line
            under_odds = bovada_obj.under_odds

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

                    print(stat)
                    print(stat_filter)
                    print(time_interval)
                    print(len(query_set))

                    values_list = []
                    for item in query_set:
                        values_list.append({'sim_value': item.sim_values,
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

        # this can be multi-processed
        analyzed_group_di_li_li = []
        for sim_group_di in simulation_group_list:
            analyzed_group_di_li_li.append(post_sim_analysis(sim_group_di))

        print("finished analyzing pitcher")
        print(analyzed_group_di_li_li[0][0])

        for li in analyzed_group_di_li_li:
            for di in li:
                prepped_for_db_table_di_li.append(di)
        print("finished prepping pitcher data")

    print("Start updating table")
    print(prepped_for_db_table_di_li[0])
    update_bovada_pitcher_post_sim_data_table(prepped_for_db_table_di_li)
    print("Finished updating table")

    update_bovada_pitcher_bet_comparison()


def update_bovada_pitcher_bet_comparison():
    MlbBovadaPitchersBetComparison.objects.all().delete()
    pitcher_ids = MlbBovadaPitchersPostSimData.objects.values_list('player_id', flat=True).distinct()

    for pitcher_id in pitcher_ids:
        pitcher_obj = MlbBovadaUpcomingPitchers.objects.filter(player_id=pitcher_id)[0]
        player_name = pitcher_obj.player_name
        team_id = pitcher_obj.team_id
        game_id = pitcher_obj.game_id
        home_or_away = pitcher_obj.home_or_away

        pitcher_obj_qs = MlbBovadaPitchersPostSimData.objects.filter(player_id=pitcher_id)
        statistics = pitcher_obj_qs.values_list('stat', flat=True).distinct()

        for stat in statistics:
            stat_obj_qs = pitcher_obj_qs.filter(stat=stat)
            stat_obj_no_filter_qs = stat_obj_qs.filter(stat_filter='none')
            stat_obj_home_away_filter_qs = stat_obj_qs.filter(stat_filter=home_or_away)

            qs_li = [stat_obj_no_filter_qs,
                     stat_obj_home_away_filter_qs]

            lowest_diff_by_filter_and_time_interval = []
            for qs in qs_li:
                time_intervals = qs.values_list('time_interval', flat=True).distinct()
                for interval in time_intervals:
                    time_interval_qs = qs.filter(time_interval=interval)
                    best_match_obj = # TODO grab the one with the lowest difference
                    lowest_diff_by_filter_and_time_interval.append(best_match_obj)

                    # TODO run the post sim analysis for each future sim numbers for each of the generated good matches
                    # identify high probability, low probability, avg probability and best match probability -
                    # also show difference numbers
                    # then classify bets as bad, good, great, primo
                    # bad is losing unit per bet based on best match,
                    # good is + expected value per unit based on best match,
                    # great is + expected value per unit even with lowest probability
                    # primo is + expected value per unit even with lowest probability - difference
                    # eventually track accuracy of each category

# TODO for some reason there are more items in most of the timeframe query sets than there should be
#  Also some of the expected probability averages are coming out exactly the same, should have minute difference?
def post_sim_analysis(sim_group_di):
    sim_options = [
        "Raw",
        "Zeroed",
        "Absolute Value",
        "Deleted"
    ]
    round_options = [
        "Raw",
        "Round",
        "Round Up",
        "Round Down"
    ]
    bet_options = [
        "Over",
        "Under"
    ]

    un_pickled_values = []
    for sim in sim_group_di['values']:
        # TODO this try except is due to dirty data I think from my multiprocess work -
        #  need to make sure all sim values are a pickled list
        try:
            un_pickled_sim = pickle.loads(sim['sim_value'])
        except TypeError:
            un_pickled_sim = sim['sim_value']
        actual_value = sim['actual_value']
        un_pickled_values.append({'sim_value': un_pickled_sim,
                                  'actual_value': actual_value})

    print(len(un_pickled_values))

    sim_group_di_li = []
    for s_option in sim_options:
        sim_group_di.update({'values': un_pickled_values})  # in the loop to reset back to originals every round
        s_option_di = {}
        match s_option:
            case 'Raw':
                # case 'Raw' keeps the numbers the same
                temp_value_di_li = []
                for i in range(len(sim_group_di['values'])):
                    temp_value_di_li.append({'sim_value': sim_group_di['values'][i]['sim_value'],
                                             'actual_value': sim_group_di['values'][i]['actual_value']})
                s_option_di.update({'values': temp_value_di_li})
            case 'Zeroed':
                # all negative sim numbers = 0
                temp_value_di_li = []
                for i in range(len(sim_group_di['values'])):
                    prev_sim_li = sim_group_di['values'][i]['sim_value']
                    new_sim_li = zeroed(prev_sim_li)
                    temp_value_di_li.append({'sim_value': new_sim_li,
                                             'actual_value': sim_group_di['values'][i]['actual_value']})
                s_option_di.update({'values': temp_value_di_li})
            case 'Absolute Value':
                # all negative numbers absolute valued
                temp_value_di_li = []
                for i in range(len(sim_group_di['values'])):
                    prev_sim_li = sim_group_di['values'][i]['sim_value']
                    new_sim_li = abs_value(prev_sim_li)
                    temp_value_di_li.append({'sim_value': new_sim_li,
                                             'actual_value': sim_group_di['values'][i]['actual_value']})
                s_option_di.update({'values': temp_value_di_li})
            case 'Deleted':
                # all negative numbers removed
                temp_value_di_li = []
                for i in range(len(sim_group_di['values'])):
                    prev_sim_li = sim_group_di['values'][i]['sim_value']
                    new_sim_li = removed(prev_sim_li)
                    temp_value_di_li.append({'sim_value': new_sim_li,
                                             'actual_value': sim_group_di['values'][i]['actual_value']})
                s_option_di.update({'values': temp_value_di_li})

        for r_option in round_options:
            r_option_di = {}

            match r_option:
                case 'Raw':
                    # case 'Raw' keeps the numbers the same
                    temp_value_di_li = []
                    for i in range(len(s_option_di['values'])):
                        temp_value_di_li.append({'sim_value': s_option_di['values'][i]['sim_value'],
                                                 'actual_value': sim_group_di['values'][i]['actual_value']})
                    r_option_di.update({'values': temp_value_di_li})
                case 'Round':
                    # all numbers rounded normally
                    temp_value_di_li = []
                    for i in range(len(s_option_di['values'])):
                        prev_sim_li = s_option_di['values'][i]['sim_value']
                        new_sim_li = round_list(prev_sim_li)
                        temp_value_di_li.append({'sim_value': new_sim_li,
                                                 'actual_value': sim_group_di['values'][i]['actual_value']})
                    r_option_di.update({'values': temp_value_di_li})
                case 'Round Up':
                    # all numbers rounded up to the nearest int
                    temp_value_di_li = []
                    for i in range(len(s_option_di['values'])):
                        prev_sim_li = s_option_di['values'][i]['sim_value']
                        new_sim_li = round_up_list(prev_sim_li)
                        temp_value_di_li.append({'sim_value': new_sim_li,
                                                 'actual_value': sim_group_di['values'][i]['actual_value']})
                    r_option_di.update({'values': temp_value_di_li})
                case 'Round Down':
                    # all numbers rounded down to the nearest int
                    temp_value_di_li = []
                    for i in range(len(s_option_di['values'])):
                        prev_sim_li = s_option_di['values'][i]['sim_value']
                        new_sim_li = round_down_list(prev_sim_li)
                        temp_value_di_li.append({'sim_value': new_sim_li,
                                                 'actual_value': sim_group_di['values'][i]['actual_value']})
                    r_option_di.update({'values': temp_value_di_li})

            for b_option in bet_options:
                bet_line = None
                bet_odds = None
                expected_prob_avg = None
                actual_result_avg = None

                match b_option:
                    case 'Over':
                        # determine expected value for over the line and compare to actual value
                        bet_line = sim_group_di['over_line']
                        bet_odds = sim_group_di['over_odds']
                        temp_value_di_li = []
                        temp_expected_probability_li = []
                        temp_actual_result_li = []
                        for i in range(len(r_option_di['values'])):

                            sim_li = r_option_di['values'][i]['sim_value']
                            count = sum(x > bet_line for x in sim_li)
                            expected_probability = count / len(sim_li)
                            temp_expected_probability_li.append(expected_probability)

                            actual_value = sim_group_di['values'][i]['actual_value']
                            if actual_value > bet_line:  # need to get this betting line in here programmatically
                                actual_result = 1
                            else:
                                actual_result = 0
                            temp_actual_result_li.append(actual_result)

                            temp_value_di_li.append({'sim_value': sim_li,
                                                     'actual_value': actual_value,
                                                     'expected_probability': expected_probability,
                                                     'actual_result': actual_result})

                        expected_prob_avg = sum(temp_expected_probability_li) / len(temp_expected_probability_li)
                        actual_result_avg = sum(temp_actual_result_li) / len(temp_actual_result_li)
                        sim_group_di.update({'bet_line': bet_line,
                                             'values': temp_value_di_li,
                                             'expected_prob_avg': expected_prob_avg,
                                             'actual_result_avg': actual_result_avg,
                                             'difference': expected_prob_avg - actual_result_avg})
                    case 'Under':
                        # determine expected value for under the line and compare to actual value
                        bet_line = sim_group_di['under_line']
                        bet_odds = sim_group_di['under_odds']
                        temp_value_di_li = []
                        temp_expected_probability_li = []
                        temp_actual_result_li = []
                        for i in range(len(r_option_di['values'])):

                            sim_li = r_option_di['values'][i]['sim_value']
                            count = sum(x < bet_line for x in sim_li)
                            expected_probability = count / len(sim_li)
                            temp_expected_probability_li.append(expected_probability)

                            actual_value = sim_group_di['values'][i]['actual_value']
                            if actual_value < bet_line:  # need to get this betting line in here programmatically
                                actual_result = 1
                            else:
                                actual_result = 0
                            temp_actual_result_li.append(actual_result)

                            temp_value_di_li.append({'sim_value': sim_li,
                                                     'actual_value': actual_value,
                                                     'expected_probability': expected_probability,
                                                     'actual_result': actual_result})

                        expected_prob_avg = sum(temp_expected_probability_li) / len(temp_expected_probability_li)
                        actual_result_avg = sum(temp_actual_result_li) / len(temp_actual_result_li)
                sim_group_di_li.append({'player_id': sim_group_di['player_id'],
                                        'player_name': sim_group_di['player_name'],
                                        'team_id': sim_group_di['team_id'],
                                        'stat': sim_group_di['stat'],
                                        'stat_filter': sim_group_di['stat_filter'],
                                        'time_interval': sim_group_di['time_interval'],
                                        'sim_option': s_option,
                                        'round_option': r_option,
                                        'bet_option': b_option,
                                        'bet_line': bet_line,
                                        'bet_odds': bet_odds,
                                        'expected_prob_avg': expected_prob_avg,
                                        'actual_result_avg': actual_result_avg,
                                        'difference': abs(expected_prob_avg - actual_result_avg)})

    return sim_group_di_li


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


# if you have nested lists of lists this will bring all items to one level
def flatten_list(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten_list(list_of_lists[0]) + flatten_list(list_of_lists[1:])
    return list_of_lists[:1] + flatten_list(list_of_lists[1:])
