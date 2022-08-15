import random
import statistics
from scipy.stats import norm
import pickle
import math


def run_monte_carlo_sim(di):
    simulations = 10000

    prev_values = di['prev_values']
    prev_avg = statistics.mean(prev_values)
    prev_st_dev = statistics.stdev(prev_values)

    pickled_prev_values = pickle.dumps(prev_values)

    # most stats will have values, but some could all be zero  or all the same number creating a st_dev of 0
    # and the sim fails.
    if prev_avg == 0:
        di.update({'sim_values': pickled_prev_values,
                   'sim_avg': prev_avg,
                   'sim_st_dev': prev_st_dev,
                   'prev_values': pickled_prev_values,
                   'prev_avg': prev_avg,
                   'prev_st_dev': prev_st_dev})

    elif prev_st_dev == 0:
        di.update({'sim_values': pickle.dumps(prev_avg),
                   'sim_avg': prev_avg,
                   'sim_st_dev': prev_st_dev,
                   'prev_values': pickled_prev_values,
                   'prev_avg': prev_avg,
                   'prev_st_dev': prev_st_dev})
    else:
        sim_list = []
        for x in range(simulations):
            sim_list.append(norm.ppf(random.random(),
                                     loc=prev_avg,
                                     scale=prev_st_dev))
        di.update({'sim_values': pickle.dumps(sim_list),
                        'sim_avg': statistics.mean(sim_list),
                        'sim_st_dev': statistics.stdev(sim_list),
                        'prev_values': pickled_prev_values,
                        'prev_avg': prev_avg,
                        'prev_st_dev': prev_st_dev})
    return di


# TODO some of the expected probability averages are coming out exactly the same, should have minute difference?
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
        # lots of funkiness with pickling and multiprocessing keep an eye out
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