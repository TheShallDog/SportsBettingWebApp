import requests
import unicodedata
from .models import MlbUpcomingGames
from .models import MlbPlayer
from .models import MlbBovadaUpcomingPitchers
from .models import MlbUpcomingPlayers
from .models import MlbTeam


def refresh_bov_mlb_upcoming_games():
    mlb_json_url = "https://www.bovada.lv/services/sports/event/coupon/events/A/description/baseball/" \
                   "mlb?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en"
    list_of_events_json = bov_game_events_json(mlb_json_url)

    for event in list_of_events_json:
        start_time_unix = event['startTime']
        teams = get_teams(event)
        print(teams)
        game_id = match_game_id(start_time_unix, teams)
        pitchers = get_pitcher_names(event)
        pitcher_data = []
        for pitcher in pitchers:
            temp_data = get_pitcher_data(pitcher, event)
            reconciled_data = reconcile_bov_players(temp_data, teams, game_id)
            pitcher_data.append(reconciled_data)

        for p in pitcher_data:
            print(p)

        update_bovada_upcoming_pitchers_table(pitcher_data)


def bov_game_events_json(league_json_url):
    # store individual game json
    league_games_json = []

    response = requests.get(league_json_url)
    # json encapsulated in a 1 item list so removing that while creating json object
    j = response.json()[0]
    # list of upcoming games json data - always changing
    upcoming_games = j['events']

    # running a loop for every game in the upcoming game list to store json for each one
    for x in range(len(upcoming_games)):
        # pull out the link to the individual game page from the league games page
        temp_link_insert = upcoming_games[x]['link']
        # create a complete api link
        temp_link_complete = "https://www.bovada.lv/services/sports/event/coupon/events/A/description" \
                             "{}?lang=en".format(temp_link_insert)
        temp_response = requests.get(temp_link_complete)
        print(temp_link_complete)
        temp_json = temp_response.json()[0]
        league_games_json.append(temp_json['events'][0])
        # break  # TODO this makes it go just once for testing purposes

    return league_games_json


def get_teams(event_json):
    team_info = {}
    for team in event_json['competitors']:
        if bool(team['home']):
            team_info.update({'home': team['name']})
        else:
            team_info.update({'away': team['name']})

    return team_info


def get_pitcher_names(event_json):
    pitchers = []
    for team in event_json['competitors']:
        pitchers.append(team['pitcher']['name'])
    return pitchers


def get_pitcher_data(pitcher, event_json):
    pitcher_data_di = {'player_id': None,
                       'player_name': pitcher,
                       'strikeout_over_line': None,
                       'strikeout_under_line': None,
                       'strikeout_over_odds': None,
                       'strikeout_under_odds': None,
                       'walks_over_line': None,
                       'walks_under_line': None,
                       'walks_over_odds': None,
                       'walks_under_odds': None,
                       'pitching_out_over_line': None,
                       'pitching_out_under_line': None,
                       'pitching_out_over_odds': None,
                       'pitching_out_under_odds': None,
                       'earned_runs_over_line': None,
                       'earned_runs_under_line': None,
                       'earned_runs_over_odds': None,
                       'earned_runs_under_odds': None,
                       'hits_allowed_over_line': None,
                       'hits_allowed_under_line': None,
                       'hits_allowed_over_odds': None,
                       'hits_allowed_under_odds': None,
                       }

    for prop in event_json['displayGroups']:

        if prop['description'] == 'Pitcher Props':

            for market in prop['markets']:

                if pitcher in market['description']:

                    if 'Total Strikeouts' in market['description']:
                        for outcome in market['outcomes']:
                            match outcome['description']:
                                case 'Over':
                                    pitcher_data_di.update(
                                        {'strikeout_over_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'strikeout_over_odds': check_even_odds(outcome['price']['american'])})
                                case 'Under':
                                    pitcher_data_di.update(
                                        {'strikeout_under_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'strikeout_under_odds': check_even_odds(outcome['price']['american'])})

                    elif 'Total Walks' in market['description']:
                        for outcome in market['outcomes']:
                            match outcome['description']:
                                case 'Over':
                                    pitcher_data_di.update(
                                        {'walks_over_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'walks_over_odds': check_even_odds(outcome['price']['american'])})
                                case 'Under':
                                    pitcher_data_di.update(
                                        {'walks_under_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'walks_under_odds': check_even_odds(outcome['price']['american'])})

                    elif 'Total Pitching Outs' in market['description']:
                        for outcome in market['outcomes']:
                            match outcome['description']:
                                case 'Over':
                                    pitcher_data_di.update(
                                        {'pitching_out_over_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'pitching_out_over_odds': check_even_odds(outcome['price']['american'])})
                                case 'Under':
                                    pitcher_data_di.update(
                                        {'pitching_out_under_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'pitching_out_under_odds': check_even_odds(outcome['price']['american'])})

                    elif 'Total Earned Runs' in market['description']:
                        for outcome in market['outcomes']:
                            match outcome['description']:
                                case 'Over':
                                    pitcher_data_di.update(
                                        {'earned_runs_over_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'earned_runs_over_odds': check_even_odds(outcome['price']['american'])})
                                case 'Under':
                                    pitcher_data_di.update(
                                        {'earned_runs_under_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'earned_runs_under_odds': check_even_odds(outcome['price']['american'])})

                    elif 'Total Hits Allowed' in market['description']:
                        for outcome in market['outcomes']:
                            match outcome['description']:
                                case 'Over':
                                    pitcher_data_di.update(
                                        {'hits_allowed_over_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'hits_allowed_over_odds': check_even_odds(outcome['price']['american'])})
                                case 'Under':
                                    pitcher_data_di.update(
                                        {'hits_allowed_under_line': outcome['price']['handicap']})
                                    pitcher_data_di.update(
                                        {'hits_allowed_under_odds': check_even_odds(outcome['price']['american'])})
    return pitcher_data_di


def check_even_odds(odds):
    if odds == 'EVEN':
        return 100
    else:
        return odds


def match_game_id(start_time_unix, teams):
    home_team_id = match_team_di(teams['home'])
    away_team_id = match_team_di(teams['away'])

    query_set = MlbUpcomingGames.objects.filter(home_team_id=home_team_id).filter(away_team_id=away_team_id)

    game_id = list(query_set.values_list('game_id', flat=True))[0]

    return game_id


def match_team_di(team_name):
    team_id = MlbTeam.objects.get(name=team_name).team_id
    return team_id


def reconcile_bov_players(player_data, teams, game_id):
    player_name = player_data['player_name']
    name_split = player_name.split(' ')
    first_name = strip_accents(name_split[0])
    last_name = strip_accents(name_split[1])

    # mlb upcoming players doesn't update with pitchers
    query_set = MlbPlayer.objects.filter(active=True).filter(position_abbreviation='P')\
        .filter(first_name=first_name).filter(last_name=last_name)

    if len(query_set) == 1:
        player_id = query_set[0].player_id
        player_data.update({'player_id': player_id,
                            'first_name': first_name,
                            'last_name': last_name})
    return player_data


def strip_accents(text):
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def update_bovada_upcoming_pitchers_table(pitcher_data):
    for d in pitcher_data:
        row = MlbBovadaUpcomingPitchers(player_id=d['player_id'],
                                        player_name=d['player_name'],
                                        strikeout_over_line=d['strikeout_over_line'],
                                        strikeout_under_line=d['strikeout_under_line'],
                                        strikeout_over_odds=d['strikeout_over_odds'],
                                        strikeout_under_odds=d['strikeout_under_odds'],
                                        walks_over_line=d['walks_over_line'],
                                        walks_under_line=d['walks_under_line'],
                                        walks_over_odds=d['walks_over_odds'],
                                        walks_under_odds=d['walks_under_odds'],
                                        pitching_out_over_line=d['pitching_out_over_line'],
                                        pitching_out_under_line=d['pitching_out_under_line'],
                                        pitching_out_over_odds=d['pitching_out_over_odds'],
                                        pitching_out_under_odds=d['pitching_out_under_odds'],
                                        earned_runs_over_line=d['earned_runs_over_line'],
                                        earned_runs_under_line=d['earned_runs_under_line'],
                                        earned_runs_over_odds=d['earned_runs_over_odds'],
                                        earned_runs_under_odds=d['earned_runs_under_odds'],
                                        hits_allowed_over_line=d['hits_allowed_over_line'],
                                        hits_allowed_under_line=d['hits_allowed_under_line'],
                                        hits_allowed_over_odds=d['hits_allowed_over_odds'],
                                        hits_allowed_under_odds=d['hits_allowed_under_odds'],
                                        )
        row.save()


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