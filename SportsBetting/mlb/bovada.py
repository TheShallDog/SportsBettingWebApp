import requests
import unicodedata
from .models import MlbUpcomingGames
from .models import MlbPlayer
from .models import MlbBovadaUpcomingPitchers
from .models import MlbUpcomingPlayers
from .models import MlbTeam
from .models import MlbBovadaUpcomingBatters
from .import update_mlb_data


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
        print(pitchers)
        pitcher_data = []
        for pitcher in pitchers:
            temp_data_li = get_pitcher_data(pitcher, event)

            reconciled_data_li = []
            for temp_data in temp_data_li:
                reconciled_data = reconcile_bov_players(temp_data, teams, game_id)
                reconciled_data_li.append(reconciled_data)
            pitcher_data.append(reconciled_data_li)

        update_bovada_upcoming_pitchers_table(pitcher_data)

        batter_data = get_batter_data(event, teams)
        update_bovada_upcoming_batters_table(batter_data)


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
        if x == 2:
            break  # TODO this makes it go just once for testing purposes

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


def get_pitcher_names(event_json):
    pitchers = []
    for team in event_json['competitors']:
        try:
            pitchers.append(team['pitcher']['name'])
        except KeyError:
            print("No probable pitchers named by bovada yet")
    return pitchers


def get_batter_data(event_json, teams):
    for prop in event_json['displayGroups']:
        if prop['description'] == 'Player Props':

            batter_data_di_li = []

            for market in prop['markets']:

                if 'Player to hit a Home Run' in market['description']:
                    stat = 'homerun'
                    over_line = .5

                    for outcome in market['outcomes']:

                        batter_name = outcome['description']
                        odds = outcome['price']['american']
                        batter_data_di_li.append({'stat': stat,
                                                  'over_line': over_line,
                                                  'player_name': outcome['description'],
                                                  'player_id': match_player(batter_name, teams),
                                                  'odds': odds})

                if 'Steal a Base' in market['description']:
                    stat = 'stolen_base'
                    over_line = .5

                    for outcome in market['outcomes']:

                        batter_name = outcome['description']
                        odds = outcome['price']['american']
                        batter_data_di_li.append({'stat': stat,
                                                  'over_line': over_line,
                                                  'player_name': outcome['description'],
                                                  'player_id': match_player(batter_name, teams),
                                                  'odds': odds})

                elif 'Record a Hit' in market['description']:
                    stat = 'hit'
                    over_line = .5

                    for outcome in market['outcomes']:

                        batter_name = outcome['description']
                        odds = outcome['price']['american']
                        batter_data_di_li.append({'stat': stat,
                                                  'over_line': over_line,
                                                  'player_name': batter_name,
                                                  'player_id': match_player(batter_name, teams),
                                                  'odds': odds})

                elif 'Record a Run' in market['description']:
                    stat = 'run'
                    over_line = .5

                    for outcome in market['outcomes']:

                        batter_name = outcome['description']
                        odds = outcome['price']['american']
                        batter_data_di_li.append({'stat': stat,
                                                  'over_line': over_line,
                                                  'player_name': batter_name,
                                                  'player_id': match_player(batter_name, teams),
                                                  'odds': odds})

                elif 'Record an RBI' in market['description']:
                    stat = 'rbi'
                    over_line = .5

                    for outcome in market['outcomes']:

                        batter_name = outcome['description']
                        odds = outcome['price']['american']
                        batter_data_di_li.append({'stat': stat,
                                                  'over_line': over_line,
                                                  'player_name': batter_name,
                                                  'player_id': match_player(batter_name, teams),
                                                  'odds': odds})

                elif 'Player to Hit 2+ Home Runs' in market['description']:
                    stat = 'homerun'
                    over_line = 1.5

                    for outcome in market['outcomes']:

                        batter_name = outcome['description']
                        odds = outcome['price']['american']
                        batter_data_di_li.append({'stat': stat,
                                                  'over_line': over_line,
                                                  'player_name': batter_name,
                                                  'player_id': match_player(batter_name, teams),
                                                  'odds': odds})

                elif 'Player to Record 2+ Total Bases' in market['description']:
                    stat = 'bases'
                    over_line = 1.5

                    for outcome in market['outcomes']:

                        batter_name = outcome['description']
                        odds = outcome['price']['american']
                        batter_data_di_li.append({'stat': stat,
                                                  'over_line': over_line,
                                                  'player_name': batter_name,
                                                  'player_id': match_player(batter_name, teams),
                                                  'odds': odds})

                elif 'Player to Record 3+ Total Bases' in market['description']:
                    stat = 'bases'
                    over_line = 2.5

                    for outcome in market['outcomes']:

                        batter_name = outcome['description']
                        odds = outcome['price']['american']
                        batter_data_di_li.append({'stat': stat,
                                                  'over_line': over_line,
                                                  'player_name': batter_name,
                                                  'player_id': match_player(batter_name, teams),
                                                  'odds': odds})

            return batter_data_di_li

    return []


def get_pitcher_data(pitcher, event_json):

    pitcher_data_di_li = []
    for prop in event_json['displayGroups']:

        if prop['description'] == 'Pitcher Props':

            for market in prop['markets']:

                if pitcher in market['description']:

                    pitcher_data_di = {'player_id': None,
                                       'player_name': pitcher,
                                       'stat': None,
                                       'over_line': None,
                                       'under_line': None,
                                       'over_odds': None,
                                       'under_odds': None,
                                       }

                    if 'Total Strikeouts' in market['description']:
                        pitcher_data_di.update({'stat': 'strikeout'})
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
                    print(pitcher_data_di)

    return pitcher_data_di_li


def check_even_odds(odds):
    if odds == 'EVEN':
        return 100
    else:
        return odds


def match_game_id(start_time_unix, teams):
    home_team_id = match_team(teams['home'])
    away_team_id = match_team(teams['away'])

    query_set = MlbUpcomingGames.objects.filter(home_team_id=home_team_id).filter(away_team_id=away_team_id)

    game_id = list(query_set.values_list('game_id', flat=True))[0]

    return game_id


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

    elif len(query_set) > 1:
        query_set = query_set.filter(first_name=first_name)
        if len(query_set) == 1:
            player_id = query_set[0].player_id
        else:
            player_id = None

    return player_id


def reconcile_bov_players(player_data, teams, game_id):
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


def update_bovada_upcoming_pitchers_table(pitcher_data):
    for p_recon_data in pitcher_data:
        for d in p_recon_data:
            row = MlbBovadaUpcomingPitchers(player_id=d['player_id'],
                                            player_name=d['player_name'],
                                            stat=d['stat'],
                                            over_line=d['over_line'],
                                            under_line=d['under_line'],
                                            over_odds=d['over_odds'],
                                            under_odds=d['under_odds'],
                                            )
            row.save()


def update_bovada_upcoming_batters_table(batter_data):
    for d in batter_data:
        row = MlbBovadaUpcomingBatters(player_id=d['player_id'],
                                       player_name=d['player_name'],
                                       stat=d['stat'],
                                       over_line=d['over_line'],
                                       odds=check_even_odds(d['odds']),
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