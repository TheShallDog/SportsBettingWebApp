from .models import MlbUpcomingGames
from .models import MlbPlayer
from .models import MlbAtBat
from .models import MlbGame
from .models import MlbPlayerSimulations
from .models import MlbBovadaUpcomingBatters
from .models import MlbBovadaUpcomingPitchers
import math
import statistics
import pickle


def get_upcoming_pitchers():
    probable_pitchers = MlbBovadaUpcomingPitchers.objects.values_list('player_id', flat=True).distinct()
    probable_pitchers = list(filter(None, probable_pitchers))  # remove None values
    return probable_pitchers


def get_upcoming_batters():
    probable_batters = MlbBovadaUpcomingBatters.objects.values_list('player_id', flat=True).distinct()
    probable_batters = list(filter(None, probable_batters))  # remove None values
    print(probable_batters)
    return probable_batters


def get_time_frames(input_list):
    list_length = len(input_list)
    if list_length < 10:
        return False

    max_sims = int(math.floor(list_length / 2))
    temp_length = 5
    time_frames = []
    while temp_length < max_sims:
        time_frames.append(temp_length)
        temp_length *= 2

    time_frames.append(max_sims)

    return time_frames


def mp_prepare_upcoming_player_data():
    probable_pitchers = []  # get_upcoming_pitchers() - temporary for improvement
    batters = get_upcoming_batters()

    processed_pitchers = []
    for p in probable_pitchers:
        processed_pitchers.append(process_pitchers(p))

    flat_list = flatten_list(processed_pitchers)

    processed_batters = process_batters(batters)

    return flat_list


def process_batters(batters):

    batter_pre_sim_complete_di_li = []

    for batter in batters:
        print(MlbPlayer.objects.get(pk=batter).full_name)
        player_name = MlbBovadaUpcomingBatters.objects.filter(player_id=batter)[0].player_name
        print(player_name)

        # get queryset of games where they have an at_bat in order of most recent first
        at_bats_played_qs = MlbAtBat.objects.filter(batter_id=batter) | \
                            MlbAtBat.objects.filter(scoring_player_1=batter) | \
                            MlbAtBat.objects.filter(scoring_player_2=batter) | \
                            MlbAtBat.objects.filter(scoring_player_3=batter) | \
                            MlbAtBat.objects.filter(scoring_player_4=batter) | \
                            MlbAtBat.objects.filter(base_stealer_1=batter) | \
                            MlbAtBat.objects.filter(base_stealer_2=batter) | \
                            MlbAtBat.objects.filter(base_stealer_3=batter)

        print(len(MlbAtBat.objects.filter(batter_id=batter)))  # quick check to see if there is a difference
        print(len(at_bats_played_qs))
        played_game_ids_qs = at_bats_played_qs.values_list('game_id', flat=True).distinct()
        played_games_ordered_qs = MlbGame.objects.filter(pk__in=played_game_ids_qs).order_by('-game_date')

        # turn the queryset into an ordered list
        ordered_game_ids_li = []
        for game in played_games_ordered_qs:
            ordered_game_ids_li.append(game.game_id)

        # get all batting stat categories to bet on for this batter and make into a text list
        stats_qs = MlbBovadaUpcomingBatters.objects.filter(player_id=batter).values_list('stat', flat=True).distinct()
        stats = []
        for stat in stats_qs:
            stats.append(stat)

        stat_filters = ['none', 'home', 'away']

        temp_di = {'player_id': batter,
                   'player_name': player_name,
                   'ordered_game_ids': ordered_game_ids_li,
                   'stats': stats,
                   'stat_filters': stat_filters}

        print(temp_di)

        # this method will return a list of dictionaries containing the full stats for each stat and filter by game
        processed_batter_stats_di_li = process_batter_stats(temp_di)

        print(processed_batter_stats_di_li[0])
        print(processed_batter_stats_di_li[1])

        # this method expands on the previous to break them down by individual timeframes
        # and with their respective values
        batter_pre_sim_complete_di_li = process_batter_timeframes(processed_batter_stats_di_li)

        print(batter_pre_sim_complete_di_li[0])
        print(batter_pre_sim_complete_di_li[1])

    return batter_pre_sim_complete_di_li


def flatten_list(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten_list(list_of_lists[0]) + flatten_list(list_of_lists[1:])
    return list_of_lists[:1] + flatten_list(list_of_lists[1:])


def process_pitchers(pitcher):
    print(MlbPlayer.objects.get(pk=pitcher).full_name)

    # get queryset of games where they start in order of most recent first
    started_queryset = MlbAtBat.objects.filter(pitcher_id=pitcher).filter(inning=1).filter(lineup_position=0)
    started_games_ids = started_queryset.values_list('game_id', flat=True).distinct()
    started_games_ordered = MlbGame.objects.filter(pk__in=started_games_ids).order_by('-game_date')

    # turn the queryset into an ordered list
    started_games_all = []
    for game in started_games_ordered:
        started_games_all.append(game.game_id)

    stats = ["strikeout"]  # look closely at pitcher props offered
    processed_stats = process_pitcher_stats(pitcher, started_games_all, stats)

    processed_info = []
    for p in processed_stats:
        if p['time_frames']:
            processed_info.append(process_pitcher_info(p))

    return processed_info


def process_batter_stats(batter_di):
    batter_id = batter_di['player_id']

    processed_batter_stats = []
    print(batter_di['stats'])

    for stat in batter_di['stats']:

        for stat_filter in batter_di['stat_filters']:
            ordered_games_by_filter_li = []
            ordered_cumulative_stat_by_filter_li = []

            for game_id in batter_di['ordered_game_ids']:

                at_bats_in_game = MlbAtBat.objects.filter(game_id=game_id)

                # query set that includes every at bat, that was impacted by the batter in this game
                the_qs = at_bats_in_game.filter(batter_id=batter_id) | \
                         at_bats_in_game.filter(scoring_player_1=batter_id) | \
                         at_bats_in_game.filter(scoring_player_2=batter_id) | \
                         at_bats_in_game.filter(scoring_player_3=batter_id) | \
                         at_bats_in_game.filter(scoring_player_4=batter_id) | \
                         at_bats_in_game.filter(base_stealer_1=batter_id) | \
                         at_bats_in_game.filter(base_stealer_2=batter_id) | \
                         at_bats_in_game.filter(base_stealer_3=batter_id)

                # check if this game was home or away for the batter, home bats second in each inning
                current_game_home = False
                if the_qs[0].inning_half == 'bottom':
                    current_game_home = True

                cumulative_stat = 0
                match stat:

                    case 'home_run':
                        cumulative_stat = the_qs.filter(batter_id=batter_id).filter(home_run=True).count()

                    case 'stolen_base':
                        cumulative_stat_qs = the_qs.filter(base_stealer_1=batter_id) | \
                                             the_qs.filter(base_stealer_2=batter_id) | \
                                             the_qs.filter(base_stealer_3=batter_id)

                        cumulative_stat = cumulative_stat_qs.count()

                    case 'hit':
                        temp_qs = the_qs.filter(batter_id=batter_id)

                        cumulative_stat_qs = temp_qs.filter(single=True) | \
                                             temp_qs.filter(double=True) | \
                                             temp_qs.filter(triple=True) | \
                                             temp_qs.filter(home_run=True)

                        cumulative_stat = cumulative_stat_qs.count()

                    case 'run':
                        cumulative_stat_qs = the_qs.filter(scoring_player_1=batter_id) | \
                                             the_qs.filter(scoring_player_2=batter_id) | \
                                             the_qs.filter(scoring_player_3=batter_id) | \
                                             the_qs.filter(scoring_player_4=batter_id)

                        cumulative_stat = cumulative_stat_qs.count()

                    case 'rbi':
                        temp_qs = the_qs.filter(batter_id=batter_id)
                        cumulative_stat = sum(temp_qs.values_list('rbi', flat=True))

                    case 'bases':
                        temp_qs = the_qs.filter(batter_id=batter_id)

                        singles = temp_qs.filter(single=True).count()
                        doubles = temp_qs.filter(double=True).count()
                        triples = temp_qs.filter(triple=True).count()

                        home_runs = temp_qs.filter(home_run=True).count()

                        cumulative_stat = singles + (doubles * 2) + (triples * 3) + (home_runs * 4)

                match stat_filter:
                    case 'none':
                        ordered_games_by_filter_li.append(game_id)
                        ordered_cumulative_stat_by_filter_li.append(cumulative_stat)
                    case 'home':
                        if current_game_home:
                            ordered_games_by_filter_li.append(game_id)
                            ordered_cumulative_stat_by_filter_li.append(cumulative_stat)
                    case 'away':
                        if not current_game_home:
                            ordered_games_by_filter_li.append(game_id)
                            ordered_cumulative_stat_by_filter_li.append(cumulative_stat)

            time_frames_li = get_time_frames(ordered_cumulative_stat_by_filter_li)

            processed_batter_stats.append({'player_id': batter_id,
                                           'games': ordered_games_by_filter_li,
                                           'values': ordered_cumulative_stat_by_filter_li,
                                           'stat': stat,
                                           'filters': stat_filter,
                                           'time_frames': time_frames_li})

    return processed_batter_stats


def process_batter_timeframes(processed_batter_stats_di_li):

    data = []
    for di in processed_batter_stats_di_li:
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
            time_frame = time_interval

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


def process_pitcher_stats(pitcher_id, games_all, stats):
    # TODO this has to be able to made more programmatic based on different filter setups
    processed_stats = []
    for stat in stats:
        stat_all = []
        stat_home = []
        stat_away = []
        games_home = []
        games_away = []

        for game_id in games_all:
            all_pitched_at_bats = MlbAtBat.objects.filter(game_id=game_id).filter(pitcher_id=pitcher_id)

            if stat == 'home_run' or stat == 'strikeout':  # Boolean statistics vs integers,
                # could turn booleans into integers in model file
                cumulative_stat = all_pitched_at_bats.filter(**{stat: True}).count()
            else:
                cumulative_stat = all_pitched_at_bats.values(stat).sum()
            stat_all.append(cumulative_stat)
            if all_pitched_at_bats.values_list('inning_half', flat=True)[0] == 'top':
                stat_home.append(cumulative_stat)
                games_home.append(game_id)
            elif all_pitched_at_bats.values_list('inning_half', flat=True)[0] == 'bottom':
                stat_away.append(cumulative_stat)
                games_away.append(game_id)

        processed_stats.append({'player_id': pitcher_id, 'time_frames': get_time_frames(stat_all),
                                'games': games_all, 'values': stat_all, 'stat': stat, 'filters': "all"})
        processed_stats.append({'player_id': pitcher_id, 'time_frames': get_time_frames(stat_home),
                                'games': games_home, 'values': stat_home, 'stat': stat, 'filters': "home"})
        processed_stats.append({'player_id': pitcher_id, 'time_frames': get_time_frames(stat_away),
                                'games': games_away, 'values': stat_away, 'stat': stat, 'filters': "away"})
    return processed_stats


def process_pitcher_info(processed_stat_dict):
    di = processed_stat_dict
    time_frames = di['time_frames']
    data = []

    for time_interval in time_frames:
        # TODO check that this simulation doesnt currently exist in the table
        x = 0
        while x <= time_interval:
            # this allows us to have a future set of simulations when x = 0
            # when game = None that is our future prediction
            player = MlbPlayer.objects.get(player_id=di['player_id'])

            if x == 0:
                game = None
                game_date = None
                actual_value = None
            else:
                game = di['games'][x - 1]
                game_date = MlbGame.objects.get(game_id=game).game_date
                actual_value = di['values'][x - 1]

            statistic = di['stat']
            time_frame = time_interval
            stat_filters = di['filters']

            # creates a list of just the previous statistics from the asked for timeframe and
            # doesn't include the current games stat
            prev_values = di['values'][x:time_interval + x]
            prev_avg = statistics.mean(prev_values)
            prev_st_dev = statistics.stdev(prev_values)

            sim_values = None
            sim_avg = None
            sim_st_dev = None

            temp_dict = {'player': player,
                         'game_id': game,
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
                         'actual_value': actual_value,
                         }
            data.append(temp_dict)
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


def analyze_pitcher_simulations(player_id):
    print(MlbPlayer.objects.get(player_id=player_id).full_name)
    # figure out how to get betting line information programmatically from updated table
    over_line = 4.5  # betting lines updated from Bovada
    under_line = 4.5

    simulation_group_list = []

    # get each unique stat that is stored in simulated date
    player_query_set = MlbPlayerSimulations.objects.filter(player=player_id)
    stat_query_set = player_query_set \
        .values_list('statistic', flat=True) \
        .distinct()
    # get each unique filter that is stored in simulated data for each stat
    for stat in stat_query_set:
        filter_query_set = player_query_set \
            .filter(statistic=stat) \
            .values_list('stat_filters', flat=True) \
            .distinct()
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

                simulation_group_list.append({'stat': stat,
                                              'stat_filter': stat_filter,
                                              'time_interval': time_interval,
                                              'values': values_list,
                                              'over_line': over_line,
                                              'under_line': under_line})

    # this can be multi-processed
    analyzed_group_list = []
    for sim_group_di in simulation_group_list:
        analyzed_group_list.append(post_sim_analysis(sim_group_di))

    """
    this is where i pull out the best of the best information for each one and analyze the sim numbers
    for each item in the analyzed group
        query_set = player_query_set\
                    .filter(statistic=stat)\
                    .filter(stat_filters=stat_filter)\
                    .filter(time_frame=time_interval)\
                    .filter(actual_value=None)
        expected_value = analyse(query_set, betting_line)
        american odds = convert(expected_value)
    """


def post_sim_analysis(sim_group_di):  # needs to actually be a dictionary so can send a list of dicts
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
        un_pickled_sim = pickle.loads(sim['sim_value'])
        actual_value = sim['actual_value']
        un_pickled_values.append({'sim_value': un_pickled_sim,
                                  'actual_value': actual_value})

    print(len(un_pickled_values))

    sim_group_li = []
    for s_option in sim_options:
        sim_group_di.update({'values': un_pickled_values})  # this has to be in the loop to reset the dictionary
        sim_group_di.update({'sim_option': s_option})
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
            sim_group_di.update({'round_option': r_option})
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

                sim_group_di.update({'bet_option': b_option})
                match b_option:
                    case 'Over':
                        # determine expected value for over the line and compare to actual value
                        bet_line = sim_group_di['over_line']
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
                        sim_group_di.update({'bet_line': bet_line,
                                             'values': temp_value_di_li,
                                             'expected_prob_avg': expected_prob_avg,
                                             'actual_result_avg': actual_result_avg,
                                             'difference': expected_prob_avg - actual_result_avg})

                print(sim_group_di['stat'] + "\t" + sim_group_di['stat_filter'] + "\t" + str(
                    sim_group_di['time_interval'])
                      + "\t" + sim_group_di['sim_option'] + "\t\t" + sim_group_di['round_option'] + "\t" + sim_group_di[
                          'bet_option']
                      + "\t" + "bet line: " + str(sim_group_di['bet_line'])
                      + "\t" + "exp prob: " + str(round((sim_group_di['expected_prob_avg']) * 100, 2)) + "%"
                      + "\t" + "act res: " + str(round((sim_group_di['actual_result_avg']) * 100, 2)) + "%"
                      + "\t" + "Difference: " + str(round((sim_group_di['difference']) * 100, 6)) + "%")
                if sim_group_di['bet_option'] == 'Under' and False:  # choose True or False if I want to see for debug
                    for item in sim_group_di['values']:
                        print(str(item['sim_value'][0]) + "\t length: " + str(len(item['sim_value']))
                              + "\t" + "below zero: " + str(len(below_zero(item['sim_value'])))
                              + "\t" + "equal zero: " + str(len(equal_zero(item['sim_value'])))
                              + "\t" + "min value: " + str(min(item['sim_value']))
                              + "\t" + "max value: " + str(max(item['sim_value'])))

    return sim_group_li


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
