import requests
import unicodedata
from .models import MlbUpcomingGames
from .models import MlbPlayer
from .models import MlbBovadaUpcomingPitchers
from .models import MlbTeam
from .models import MlbBovadaUpcomingBatters
from .import update_mlb_data
import datetime
import time


def refresh_bov_mlb_upcoming_player_tables():
    start = time.time()
    print("starting to refresh bovada data tables")

    mlb_json_url = "https://www.bovada.lv/services/sports/event/coupon/events/A/description/baseball/" \
                   "mlb?marketFilterId=def&preMatchOnly=true&eventsLimit=5000&lang=en"
    print(mlb_json_url)

    list_of_events_json = bov_game_events_json(mlb_json_url)

    pitcher_data_li = []
    batter_data_li = []
    for event in list_of_events_json:

        # check if start time is after midnight of current night then skip the event - only get current day events
        start_time_unix = event['startTime']
        midnight_unix = get_midnight_unix()
        if start_time_unix > midnight_unix:
            continue

        # check if it is a game even vs a total run event
        if "Total Runs" in event['description']:
            continue

        teams = get_teams(event)
        upcoming_game = match_upcoming_game(start_time_unix, teams)

        pitcher_data = get_pitcher_data(event, teams, upcoming_game)
        pitcher_data_li.append(pitcher_data)

        batter_data = get_batter_data(event, teams, upcoming_game)
        batter_data_li.append(batter_data)

    update_bovada_upcoming_pitchers_table(pitcher_data_li)
    update_bovada_upcoming_batters_table(batter_data_li)

    print("finished refreshing bovada data tables in " + str(round(time.time() - start)) + " seconds")


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
        print(temp_link_complete)
        temp_response = requests.get(temp_link_complete)
        if temp_response.status_code == 404:
            continue
        else:
            temp_json = temp_response.json()

        league_games_json.append(temp_json[0]['events'][0])

    return league_games_json


def get_teams(event_json):
    team_info = {}
    for team in event_json['competitors']:
        if bool(team['home']):
            team_info.update({'home': team['name'],
                              'home_id': match_team(team['name'])})
        else:
            team_info.update({'away': team['name'],
                              'away_id': match_team(team['name'])})

    return team_info


def get_midnight_unix():

    date_time = datetime.datetime.today()
    tomorrow_dt = date_time + datetime.timedelta(days=1)
    midnight_dt = tomorrow_dt.replace(hour=0, minute=0, second=0)

    # the thousand puts this in millisecond format which is what bovada is in
    midnight_unix = time.mktime(midnight_dt.timetuple()) * 1000

    return midnight_unix


def get_pitcher_names(event_json):
    pitchers = []
    for team in event_json['competitors']:
        try:
            pitchers.append(team['pitcher']['name'])
        except KeyError:
            print("No probable pitchers named by bovada yet")
    return pitchers


def get_batter_data(event_json, teams, upcoming_game):
    game_id = upcoming_game.game_id

    batter_data_di_li = []
    for prop in event_json['displayGroups']:
        if prop['description'] == 'Player Props':

            for market in prop['markets']:

                if 'Player to hit a Home Run' in market['description']:
                    stat = 'homerun'
                    over_line = .5

                    for outcome in market['outcomes']:

                        player_name = outcome['description']
                        player_id = match_player(player_name, teams)

                        if player_id is None:
                            team_id = None
                        else:
                            team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                        if upcoming_game.home_team_id == team_id:
                            home_or_away = 'home'
                        elif upcoming_game.away_team_id == team_id:
                            home_or_away = 'away'
                        else:
                            home_or_away = None

                        odds = outcome['price']['american']
                        batter_data_di_li.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'game_id': game_id,
                                                  'team_id': team_id,
                                                  'home_or_away': home_or_away,
                                                  'stat': stat,
                                                  'over_line': over_line,
                                                  'odds': odds})

                if 'Steal a Base' in market['description']:
                    stat = 'stolen_base'
                    over_line = .5

                    for outcome in market['outcomes']:

                        player_name = outcome['description']
                        player_id = match_player(player_name, teams)

                        if player_id is None:
                            team_id = None
                        else:
                            team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                        if upcoming_game.home_team_id == team_id:
                            home_or_away = 'home'
                        elif upcoming_game.away_team_id == team_id:
                            home_or_away = 'away'
                        else:
                            home_or_away = None

                        odds = outcome['price']['american']
                        batter_data_di_li.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'game_id': game_id,
                                                  'team_id': team_id,
                                                  'home_or_away': home_or_away,
                                                  'stat': stat,
                                                  'over_line': over_line,
                                                  'odds': odds})

                elif 'Record a Hit' in market['description']:
                    stat = 'hit'
                    over_line = .5

                    for outcome in market['outcomes']:

                        player_name = outcome['description']
                        player_id = match_player(player_name, teams)

                        if player_id is None:
                            team_id = None
                        else:
                            team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                        if upcoming_game.home_team_id == team_id:
                            home_or_away = 'home'
                        elif upcoming_game.away_team_id == team_id:
                            home_or_away = 'away'
                        else:
                            home_or_away = None

                        odds = outcome['price']['american']
                        batter_data_di_li.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'game_id': game_id,
                                                  'team_id': team_id,
                                                  'home_or_away': home_or_away,
                                                  'stat': stat,
                                                  'over_line': over_line,
                                                  'odds': odds})

                elif 'Record a Run' in market['description']:
                    stat = 'run'
                    over_line = .5

                    for outcome in market['outcomes']:

                        player_name = outcome['description']
                        player_id = match_player(player_name, teams)

                        if player_id is None:
                            team_id = None
                        else:
                            team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                        if upcoming_game.home_team_id == team_id:
                            home_or_away = 'home'
                        elif upcoming_game.away_team_id == team_id:
                            home_or_away = 'away'
                        else:
                            home_or_away = None

                        odds = outcome['price']['american']
                        batter_data_di_li.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'game_id': game_id,
                                                  'team_id': team_id,
                                                  'home_or_away': home_or_away,
                                                  'stat': stat,
                                                  'over_line': over_line,
                                                  'odds': odds})

                elif 'Record an RBI' in market['description']:
                    stat = 'rbi'
                    over_line = .5

                    for outcome in market['outcomes']:

                        player_name = outcome['description']
                        player_id = match_player(player_name, teams)

                        if player_id is None:
                            team_id = None
                        else:
                            team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                        if upcoming_game.home_team_id == team_id:
                            home_or_away = 'home'
                        elif upcoming_game.away_team_id == team_id:
                            home_or_away = 'away'
                        else:
                            home_or_away = None

                        odds = outcome['price']['american']
                        batter_data_di_li.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'game_id': game_id,
                                                  'team_id': team_id,
                                                  'home_or_away': home_or_away,
                                                  'stat': stat,
                                                  'over_line': over_line,
                                                  'odds': odds})

                elif 'Player to Hit 2+ Home Runs' in market['description']:
                    stat = 'homerun'
                    over_line = 1.5

                    for outcome in market['outcomes']:

                        player_name = outcome['description']
                        player_id = match_player(player_name, teams)

                        if player_id is None:
                            team_id = None
                        else:
                            team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                        if upcoming_game.home_team_id == team_id:
                            home_or_away = 'home'
                        elif upcoming_game.away_team_id == team_id:
                            home_or_away = 'away'
                        else:
                            home_or_away = None

                        odds = outcome['price']['american']
                        batter_data_di_li.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'game_id': game_id,
                                                  'team_id': team_id,
                                                  'home_or_away': home_or_away,
                                                  'stat': stat,
                                                  'over_line': over_line,
                                                  'odds': odds})

                elif 'Player to Record 2+ Total Bases' in market['description']:
                    stat = 'bases'
                    over_line = 1.5

                    for outcome in market['outcomes']:

                        player_name = outcome['description']
                        player_id = match_player(player_name, teams)

                        if player_id is None:
                            team_id = None
                        else:
                            team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                        if upcoming_game.home_team_id == team_id:
                            home_or_away = 'home'
                        elif upcoming_game.away_team_id == team_id:
                            home_or_away = 'away'
                        else:
                            home_or_away = None

                        odds = outcome['price']['american']
                        batter_data_di_li.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'game_id': game_id,
                                                  'team_id': team_id,
                                                  'home_or_away': home_or_away,
                                                  'stat': stat,
                                                  'over_line': over_line,
                                                  'odds': odds})

                elif 'Player to Record 3+ Total Bases' in market['description']:
                    stat = 'bases'
                    over_line = 2.5

                    for outcome in market['outcomes']:

                        player_name = outcome['description']
                        player_id = match_player(player_name, teams)

                        if player_id is None:
                            team_id = None
                        else:
                            team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                        if upcoming_game.home_team_id == team_id:
                            home_or_away = 'home'
                        elif upcoming_game.away_team_id == team_id:
                            home_or_away = 'away'
                        else:
                            home_or_away = None

                        odds = outcome['price']['american']
                        batter_data_di_li.append({'player_id': player_id,
                                                  'player_name': player_name,
                                                  'game_id': game_id,
                                                  'team_id': team_id,
                                                  'home_or_away': home_or_away,
                                                  'stat': stat,
                                                  'over_line': over_line,
                                                  'odds': odds})

            return batter_data_di_li

    return []


def get_pitcher_data(event_json, teams, upcoming_game):
    game_id = upcoming_game.game_id
    pitchers = get_pitcher_names(event_json)

    pitcher_data_di_li = []
    for prop in event_json['displayGroups']:
        if prop['description'] == 'Pitcher Props':

            for pitcher_name in pitchers:
                player_name = pitcher_name
                player_id = match_player(pitcher_name, teams)
                if player_id is None:
                    team_id = None
                else:
                    team_id = MlbPlayer.objects.get(player_id=player_id).current_team_id

                if upcoming_game.home_team_id == team_id:
                    home_or_away = 'home'
                elif upcoming_game.away_team_id == team_id:
                    home_or_away = 'away'
                else:
                    home_or_away = None

                for market in prop['markets']:

                    if pitcher_name in market['description']:

                        pitcher_data_di = {'player_id': player_id,
                                           'player_name': player_name,
                                           'game_id': game_id,
                                           'team_id': team_id,
                                           'home_or_away': home_or_away,
                                           'stat': None,
                                           'over_line': None,
                                           'under_line': None,
                                           'over_odds': None,
                                           'under_odds': None,
                                           }

                        if 'Total Strikeouts' in market['description']:
                            pitcher_data_di.update({'stat': 'strikeouts'})
                            for outcome in market['outcomes']:
                                match outcome['description']:
                                    case 'Over':
                                        pitcher_data_di.update(
                                            {'over_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'over_odds': check_even_odds(outcome['price']['american'])})
                                    case 'Under':
                                        pitcher_data_di.update(
                                            {'under_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'under_odds': check_even_odds(outcome['price']['american'])})

                            pitcher_data_di_li.append(pitcher_data_di)

                        elif 'Total Walks' in market['description']:
                            pitcher_data_di.update({'stat': 'walks'})
                            for outcome in market['outcomes']:
                                match outcome['description']:
                                    case 'Over':
                                        pitcher_data_di.update(
                                            {'over_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'over_odds': check_even_odds(outcome['price']['american'])})
                                    case 'Under':
                                        pitcher_data_di.update(
                                            {'under_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'under_odds': check_even_odds(outcome['price']['american'])})

                            pitcher_data_di_li.append(pitcher_data_di)

                        elif 'Total Pitching Outs' in market['description']:
                            pitcher_data_di.update({'stat': 'pitching_outs'})
                            for outcome in market['outcomes']:
                                match outcome['description']:
                                    case 'Over':
                                        pitcher_data_di.update(
                                            {'over_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'over_odds': check_even_odds(outcome['price']['american'])})
                                    case 'Under':
                                        pitcher_data_di.update(
                                            {'under_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'under_odds': check_even_odds(outcome['price']['american'])})

                            pitcher_data_di_li.append(pitcher_data_di)

                        elif 'Total Earned Runs' in market['description']:
                            pitcher_data_di.update({'stat': 'earned_runs'})
                            for outcome in market['outcomes']:
                                match outcome['description']:
                                    case 'Over':
                                        pitcher_data_di.update(
                                            {'over_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'over_odds': check_even_odds(outcome['price']['american'])})
                                    case 'Under':
                                        pitcher_data_di.update(
                                            {'under_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'under_odds': check_even_odds(outcome['price']['american'])})

                            pitcher_data_di_li.append(pitcher_data_di)

                        elif 'Total Hits Allowed' in market['description']:
                            pitcher_data_di.update({'stat': 'hits_allowed'})
                            for outcome in market['outcomes']:
                                match outcome['description']:
                                    case 'Over':
                                        pitcher_data_di.update(
                                            {'over_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'over_odds': check_even_odds(outcome['price']['american'])})
                                    case 'Under':
                                        pitcher_data_di.update(
                                            {'under_line': outcome['price']['handicap']})
                                        pitcher_data_di.update(
                                            {'under_odds': check_even_odds(outcome['price']['american'])})

                            pitcher_data_di_li.append(pitcher_data_di)

    return pitcher_data_di_li


def check_even_odds(odds):
    if odds == 'EVEN':
        return 100
    else:
        return odds


def match_upcoming_game(start_time_unix, teams):
    home_team_id = teams['home_id']
    away_team_id = teams['away_id']

    query_set = MlbUpcomingGames.objects.filter(home_team_id=home_team_id).filter(away_team_id=away_team_id)

    # TODO use start time to narrow down double header information
    game = query_set[0]

    return game


def match_team(team_name):
    team_object = MlbTeam.objects.get(name=team_name)
    team_id = team_object.team_id
    update_mlb_data.update_team_roster(team_object)
    return team_id


def match_player(name, teams):
    home_team_id = teams['home_id']
    away_team_id = teams['away_id']
    name_split = name.split(' ')
    first_name = strip_accents(name_split[0])
    last_name = strip_accents(name_split[1])
    if len(last_name) <= 2 and "." in last_name:
        last_name = strip_accents(name_split[2])

    query_set_active = MlbPlayer.objects.filter(active=True)
    query_set_teams = query_set_active.filter(current_team=home_team_id) | \
                      query_set_active.filter(current_team=away_team_id)
    query_set = query_set_teams.filter(last_name=last_name)

    player_id = None
    if len(query_set) == 1:
        player_id = query_set[0].player_id

    # if more than one player with same last name, filter by first name, if none with first name try middle name
    elif len(query_set) > 1:
        query_set_fn = query_set.filter(first_name=first_name)
        query_set_mn = query_set.filter(middle_name=first_name)

        if len(query_set_fn) == 1:
            player_id = query_set_fn[0].player_id
        elif len(query_set_fn) == 0:
            if len(query_set_mn) == 1:
                player_id = query_set_mn[0].player_id
        else:
            player_id = None

    return player_id


def reconcile_bov_players(player_data, teams):
    player_name = player_data['player_name']
    name_split = player_name.split(' ')
    first_name = strip_accents(name_split[0])
    last_name = strip_accents(name_split[1])
    home_team_id = match_team(teams['home'])
    away_team_id = match_team(teams['away'])

    query_set_active = MlbPlayer.objects.filter(active=True)
    query_set_teams = query_set_active(current_team=home_team_id) | query_set_active(current_team=away_team_id)
    query_set = query_set_teams.filter(position_abbreviation='P').filter(last_name=last_name)

    if len(query_set) == 1:
        player_id = query_set[0].player_id
        player_data.update({'player_id': player_id,
                            'first_name': first_name,
                            'last_name': last_name})
    elif len(query_set) > 1:
        query_set = query_set.filter(first_name=first_name)
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


def update_bovada_upcoming_pitchers_table(pitcher_data_li):
    start = time.time()
    print("starting to delete then update bovada upcoming pitcher table")

    MlbBovadaUpcomingPitchers.objects.all().delete()

    for pitcher_data in pitcher_data_li:
        for d in pitcher_data:
            row = MlbBovadaUpcomingPitchers(player_id=d['player_id'],
                                            player_name=d['player_name'],
                                            game_id=d['game_id'],
                                            team_id=d['team_id'],
                                            home_or_away=d['home_or_away'],
                                            stat=d['stat'],
                                            over_line=d['over_line'],
                                            under_line=d['under_line'],
                                            over_odds=d['over_odds'],
                                            under_odds=d['under_odds'],
                                            )
            row.save()

    print("finished updating bovada upcoming pitcher table in " + str(round(time.time() - start)) + " seconds")


def update_bovada_upcoming_batters_table(batter_data_li):
    start = time.time()
    print("starting to delete then update bovada upcoming batter table")
    MlbBovadaUpcomingBatters.objects.all().delete()

    for batter_data in batter_data_li:
        for d in batter_data:
            row = MlbBovadaUpcomingBatters(player_id=d['player_id'],
                                           player_name=d['player_name'],
                                           game_id=d['game_id'],
                                           team_id=d['team_id'],
                                           home_or_away=d['home_or_away'],
                                           stat=d['stat'],
                                           over_line=d['over_line'],
                                           odds=check_even_odds(d['odds']),
                                           )
            row.save()

    print("finished updating bovada upcoming batter table in " + str(round(time.time() - start)) + " seconds")


def get_upcoming_bov_pitchers():
    probable_pitchers = MlbBovadaUpcomingPitchers.objects.values_list('player_id', flat=True).distinct()
    probable_pitchers = list(filter(None, probable_pitchers))  # remove None values
    return probable_pitchers


def get_upcoming_bov_batters():
    probable_batters = MlbBovadaUpcomingBatters.objects.values_list('player_id', flat=True).distinct()
    probable_batters = list(filter(None, probable_batters))  # remove None values
    print(probable_batters)
    return probable_batters



