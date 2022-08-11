import requests
import time
from django.utils import timezone
import datetime
from .models import MlbAtBat
from .models import MlbPlayer
from .models import MlbGame
from .models import MlbTeam
from .models import MlbLocation
from .models import MlbUpcomingGames
from .models import MlbUpcomingPlayers

BASE_URL = "https://statsapi.mlb.com"


def update_completed_games():
    # put in the code delete anything older than 5 season.
    overall_start = time.time()
    # retrieve the game_ids that we need to add to our database
    previous_game_ids = previous_games_to_update()
    # retrieve all the game ids currently in the database
    existing_game_ids = MlbGame.objects.values_list('game_id', flat=True)
    # create a list that only has the games not currently in database
    game_ids = [ele for ele in previous_game_ids if ele not in existing_game_ids]
    # create entries in database for all games not yet entered
    for game in game_ids:
        start = time.time()
        update_completed_game_table(game)
        end = time.time()
        total = round(end-start)
        print("game id: " + str(game) + " updated in " + str(total) + " seconds")
    overall_end = time.time()
    overall_total = round(overall_end-overall_start)
    print("completed games updated in " + str(overall_total) + " seconds")


def update_upcoming_games():
    overall_start = time.time()
    start_date = datetime.date.today().strftime('%m/%d/%Y')
    end_date = (datetime.date.today() + datetime.timedelta(1)).strftime('%m/%d/%Y')  # yesterday
    url = f"{BASE_URL}/api/v1/schedule?startDate={start_date}&endDate={end_date}&sportId=1"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    jason = response.json()
    upcoming_game_ids = []
    for date in jason['dates']:
        for game in date['games']:
            upcoming_game_ids.append(int(game['gamePk']))
    existing_game_ids = MlbUpcomingGames.objects.values_list('game_id', flat=True)
    game_ids = [ele for ele in upcoming_game_ids if ele not in existing_game_ids]
    for game in game_ids:
        start = time.time()
        update_upcoming_game_table(game)
        end = time.time()
        total = round(end-start)
        print("game id: " + str(game) + " updated in " + str(total) + " seconds")
    overall_end = time.time()
    overall_total = round(overall_end-overall_start)
    print("upcoming games updated in " + str(overall_total) + " seconds")


def update_upcoming_game_table(g_id):
    gi_json = game_info_json(g_id)
    gp_json = game_preview_json(g_id)

    # pull out the elements from the json that I want to track for each game
    game_id = int(g_id)

    # some future games have no pre-populated info and some games have been postponed
    try:
        g = gi_json['dates'][0]['games'][0]
        if g['seriesDescription'] in ['Spring Training', 'Exhibition']:
            print('spring training or exhibition game')
            return
        # check to see if the game was postponed and if so move to the last date in the supplied json
        if g['status']['detailedState'] == 'Postponed':
            g = gi_json['dates'][len(gi_json['dates']) - 1]['games'][0]

        game_date_time = g['gameDate']
        temp_id = int(g['venue']['id'])
        update_location_table(temp_id)
        location = MlbLocation.objects.get(location_id=temp_id)
        games_in_series_current = int(g['seriesGameNumber'])
        games_in_series_total = int(g['gamesInSeries'])

    except KeyError:
        game_date_time = gp_json['gameDate']
        location = None
        games_in_series_current = None
        games_in_series_total = None

    away_team_id = int(gp_json['probables']['awayId'])
    update_team_table(away_team_id)
    away_team = MlbTeam.objects.get(team_id=away_team_id)

    try:
        temp_id = int(gp_json['probables']['awayProbable'])
        update_player_table(temp_id)
        away_probable_pitcher = MlbPlayer.objects.get(player_id=temp_id)
    except (KeyError, TypeError):
        away_probable_pitcher = None

    home_team_id = int(gp_json['probables']['homeId'])
    update_team_table(home_team_id)
    home_team = MlbTeam.objects.get(team_id=home_team_id)

    try:
        temp_id = int(gp_json['probables']['homeProbable'])
        update_player_table(temp_id)
        home_probable_pitcher = MlbPlayer.objects.get(player_id=temp_id)
    except (KeyError, TypeError):
        home_probable_pitcher = None

    game_type = gp_json['probables']['gameType']

    # create the new MLB Game Info entry in the MlbGame table
    g = MlbUpcomingGames(game_id=game_id,
                         away_team=away_team,
                         away_probable_pitcher=away_probable_pitcher,
                         home_team=home_team,
                         home_probable_pitcher=home_probable_pitcher,
                         game_date_time=game_date_time,
                         game_type=game_type,
                         location=location,
                         games_in_series_current=games_in_series_current,
                         games_in_series_total=games_in_series_total)
    g.save()

    update_upcoming_player_table(g_id, away_team_id, gp_json['away'])
    update_upcoming_player_table(g_id, home_team_id, gp_json['home'])


def update_upcoming_player_table(g_id, t_id, players):
    game = MlbUpcomingGames.objects.get(game_id=int(g_id))
    team = MlbTeam.objects.get(team_id=int(t_id))

    for athlete in players:
        temp_id = int(athlete['id'])
        update_player_table(temp_id)
        player = MlbPlayer.objects.get(player_id=temp_id)
        first_name = player.first_name
        last_name = player.last_name

        p = MlbUpcomingPlayers(game=game,
                               team=team,
                               player=player,
                               first_name=first_name,
                               last_name=last_name)
        p.save()


# always check that tables ready for production are removed from here, this is used in place of flush
def reset_test_tables():
    MlbUpcomingGames.objects.all().delete()
    MlbUpcomingPlayers.objects.all().delete()
    # MlbPlayerSimulations.objects.all().delete()


def play_by_play_json(game_id):
    url = BASE_URL + f"/api/v1/game/{game_id}/playByPlay"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    p_b_p_json = response.json()
    return p_b_p_json


def game_info_json(game_id):
    url = BASE_URL + f"/api/v1/schedule?gamePk={game_id}"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    jason = response.json()
    return jason


def game_preview_json(game_id):
    url = f"https://bdfed.stitch.mlbinfra.com/bdfed/matchup/{game_id}"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    jason = response.json()
    return jason


def team_roster_json(team_id):
    url = BASE_URL + f"/api/v1/teams/{team_id}/roster"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    jason = response.json()
    return jason


def player_info_json(player_id):
    url = BASE_URL + f"/api/v1/people/{player_id}"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    jason = response.json()
    return jason


def team_info_json(team_id):
    url = BASE_URL + f"/api/v1/teams/{team_id}"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    jason = response.json()
    return jason


def location_info_json(location_id):
    url = BASE_URL + f"/api/v1/venues/{location_id}"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    jason = response.json()
    return jason


def previous_games_to_update():
    # if the table is empty it will start over building it from a season 5 years aog
    # if the table has entries creates a list of games from a week before most recent through yesterday
    try:
        last_saved_game_date = MlbGame.objects.latest('game_date').game_date
        start_date = (last_saved_game_date - datetime.timedelta(6)).strftime('%m/%d/%Y')
    except:
        five_years_ago = datetime.date.today().year - 5
        start_date = f"01/01/{five_years_ago}"  # January 1st from 5 years ago - use when initializing table

    end_date = (datetime.date.today() - datetime.timedelta(1)).strftime('%m/%d/%Y')  # yesterday
    url = f"{BASE_URL}/api/v1/schedule?startDate={start_date}&endDate={end_date}&sportId=1"
    print(url)
    time.sleep(.1)
    response = requests.get(url)
    jason = response.json()
    game_ids = []
    for date in jason['dates']:
        for game in date['games']:
            game_ids.append(int(game['gamePk']))
    return game_ids


def update_player_table(p_id):
    if MlbPlayer.objects.filter(player_id=int(p_id)).exists():
        return

    p_json = player_info_json(p_id)
    p = p_json['people'][0]

    player_id = int(p_id)
    first_name = p['firstName']

    try:
        middle_name = p['middleName']
    except KeyError:
        middle_name = None

    last_name = p['lastName']

    try:
        name_title = p['nameTitle']
    except KeyError:
        name_title = None

    full_name = p['fullName']
    position_name = p['primaryPosition']['name']
    position_type = p['primaryPosition']['type']
    position_abbreviation = p['primaryPosition']['abbreviation']
    active = bool(p['active'])
    last_updated = datetime.datetime.now(tz=timezone.utc)

    p = MlbPlayer(player_id=player_id,
                  first_name=first_name,
                  middle_name=middle_name,
                  last_name=last_name,
                  name_title=name_title,
                  full_name=full_name,
                  position_name=position_name,
                  position_type=position_type,
                  position_abbreviation=position_abbreviation,
                  last_updated=last_updated,
                  active=active)
    p.save()


def update_team_table(t_id):
    if MlbTeam.objects.filter(team_id=int(t_id)).exists():
        return

    t_json = team_info_json(t_id)
    t = t_json['teams'][0]

    team_id = t_id
    name = t['name']
    abbreviation = t['abbreviation']
    short_name = t['shortName']
    team_code = t['teamCode']
    file_code = t['fileCode']
    franchise_name = t['franchiseName']
    club_name = t['clubName']
    league = t['league']['name']

    try:
        division = t['division']['name']
    except KeyError:
        division = None

    temp_id = int(t['venue']['id'])
    update_location_table(temp_id)
    home_venue = MlbLocation.objects.get(location_id=temp_id)
    active = bool(t['active'])
    last_updated = datetime.datetime.now(tz=timezone.utc)

    t = MlbTeam(team_id=team_id,
                name=name,
                abbreviation=abbreviation,
                short_name=short_name,
                team_code=team_code,
                file_code=file_code,
                franchise_name=franchise_name,
                club_name=club_name,
                league=league,
                division=division,
                home_venue=home_venue,
                active=active,
                last_updated=last_updated)
    t.save()


def update_location_table(l_id):
    if MlbLocation.objects.filter(location_id=int(l_id)).exists():
        return

    l_json = location_info_json(l_id)
    loc = l_json['venues'][0]

    location_id = int(l_id)
    name = loc['name']
    active = bool(loc['active'])
    last_updated = datetime.datetime.now(tz=timezone.utc)

    loc = MlbLocation(location_id=location_id,
                      name=name,
                      active=active,
                      last_updated=last_updated)
    loc.save()


def update_at_bats_table(g_id):
    pbp_json = play_by_play_json(g_id)
    at_bats = pbp_json['allPlays']

    # away batting lineup list
    away_lu = []
    # home batting lineup list
    home_lu = []
    for bat in at_bats:

        game = MlbGame.objects.get(game_id=int(g_id))
        at_bat = int(bat['atBatIndex']) + 1
        inning = bat['about']['inning']
        inning_half = bat['about']['halfInning']
        event_type = bat['result']['eventType']

        temp_id = int(bat['matchup']['pitcher']['id'])
        update_player_table(temp_id)
        pitcher = MlbPlayer.objects.get(player_id=temp_id)

        pitcher_hand = bat['matchup']['pitchHand']['code']

        temp_id = int(bat['matchup']['batter']['id'])
        update_player_table(temp_id)
        batter = MlbPlayer.objects.get(player_id=temp_id)

        batter_hand = bat['matchup']['batSide']['code']

        game_info = MlbGame.objects.filter(game_id=int(g_id)).first()
        home_team = MlbTeam.objects.get(team_id=game_info.home_team_id)
        away_team = MlbTeam.objects.get(team_id=game_info.away_team_id)

        pitching_team = None
        batting_team = None
        position = 0

        if inning_half == 'top':
            pitching_team = home_team
            batting_team = away_team

            away_lu.append(batter) if batter not in away_lu else away_lu
            position = away_lu.index(batter)

        elif inning_half == 'bottom':
            pitching_team = away_team
            batting_team = home_team

            home_lu.append(batter) if batter not in home_lu else home_lu
            position = home_lu.index(batter)

        lineup_position = position

        single = True if event_type == 'single' else False
        double = True if event_type == 'double' else False
        triple = True if event_type == 'triple' else False
        home_run = True if event_type == 'home_run' else False
        scoring_play = bool(bat['about']['isScoringPlay'])
        rbi = int(bat['result']['rbi'])

        scoring_runners = []
        base_stealers = []
        earned_runs = 0
        stolen_bases = 0
        for runner in bat['runners']:
            if bool(runner['details']['isScoringEvent']):
                scoring_runners.append(runner['details']['runner']['id'])
            if bool(runner['details']['earned']):
                earned_runs += 1
            if 'stolen' in runner['details']['eventType']:
                stolen_bases += 1
                base_stealers.append(runner['details']['runner']['id'])

        scoring_player_1 = None
        scoring_player_2 = None
        scoring_player_3 = None
        scoring_player_4 = None

        if len(scoring_runners) > 0:
            temp_id = scoring_runners[0]
            update_player_table(temp_id)
            scoring_player_1 = MlbPlayer.objects.get(player_id=temp_id)
            if len(scoring_runners) > 1:
                temp_id = scoring_runners[1]
                update_player_table(temp_id)
                scoring_player_2 = MlbPlayer.objects.get(player_id=temp_id)
                if len(scoring_runners) > 2:
                    temp_id = scoring_runners[2]
                    update_player_table(temp_id)
                    scoring_player_3 = MlbPlayer.objects.get(player_id=temp_id)
                    if len(scoring_runners) > 3:
                        temp_id = scoring_runners[3]
                        update_player_table(temp_id)
                        scoring_player_4 = MlbPlayer.objects.get(player_id=temp_id)

        strikeout = True if event_type == 'strikeout' else False

        base_stealer_1 = None
        base_stealer_2 = None
        base_stealer_3 = None

        if len(base_stealers) > 0:
            temp_id = base_stealers[0]
            update_player_table(temp_id)
            base_stealer_1 = MlbPlayer.objects.get(player_id=temp_id)
            if len(base_stealers) > 1:
                temp_id = base_stealers[1]
                update_player_table(temp_id)
                base_stealer_2 = MlbPlayer.objects.get(player_id=temp_id)
                if len(base_stealers) > 2:
                    temp_id = base_stealers[2]
                    update_player_table(temp_id)
                    base_stealer_3 = MlbPlayer.objects.get(player_id=temp_id)

        error = False
        error_committer = None
        if 'error' in event_type:
            error = True
            for runner in bat['runners']:
                if 'error' in runner['details']['eventType']:
                    for credit in runner['credits']:
                        if 'error' in credit['credit']:
                            temp_id = credit['player']['id']
                            update_player_table(temp_id)
                            error_committer = MlbPlayer.objects.get(player_id=temp_id)

        try:
            description = bat['result']['description']
        except KeyError:
            description = None

        ab = MlbAtBat(game=game,
                      at_bat=at_bat,
                      inning=inning,
                      inning_half=inning_half,
                      event_type=event_type,
                      pitching_team=pitching_team,
                      pitcher=pitcher,
                      pitcher_hand=pitcher_hand,
                      batting_team=batting_team,
                      batter=batter,
                      batter_hand=batter_hand,
                      lineup_position=lineup_position,
                      single=single,
                      double=double,
                      triple=triple,
                      home_run=home_run,
                      scoring_play=scoring_play,
                      scoring_player_1=scoring_player_1,
                      scoring_player_2=scoring_player_2,
                      scoring_player_3=scoring_player_3,
                      scoring_player_4=scoring_player_4,
                      rbi=rbi,
                      earned_runs=earned_runs,
                      strikeout=strikeout,
                      stolen_bases=stolen_bases,
                      base_stealer_1=base_stealer_1,
                      base_stealer_2=base_stealer_2,
                      base_stealer_3=base_stealer_3,
                      error=error,
                      error_committer=error_committer,
                      description=description)
        ab.save()


def update_completed_game_table(g_id):
    gi_json = game_info_json(g_id)

    # some future games have no pre-populated info and some games have been postponed
    try:
        g = gi_json['dates'][0]['games'][0]
    except KeyError:
        return

    # check to see if the game was postponed and if so move to the last date in the supplied json
    if g['status']['detailedState'] == 'Postponed':
        g = gi_json['dates'][len(gi_json['dates'])-1]['games'][0]

    # check to see if the game is over - previous code has already checked if this game is already in our database
    if not g['status']['detailedState'] in ['Final', 'Completed Early']:
        print('Game ' + str(g_id) + ' in ' + g['status']['detailedState'] + ' state instead of Final')
        return

    # filter out spring training and exhibition games
    if g['seriesDescription'] in ['Spring Training', 'Exhibition']:
        print('spring training or exhibition game')
        return

    # pull out the elements from the json that I want to track for each game
    game_id = int(g_id)

    temp_id = int(g['teams']['away']['team']['id'])
    update_team_table(temp_id)
    away_team = MlbTeam.objects.get(team_id=temp_id)

    try:
        temp_id = int(g['teams']['away']['probablePitcher']['id'])
        update_player_table(temp_id)
        away_probable_pitcher = MlbPlayer.objects.get(player_id=temp_id)
    except KeyError:
        away_probable_pitcher = None

    temp_id = int(g['teams']['home']['team']['id'])
    update_team_table(temp_id)
    home_team = MlbTeam.objects.get(team_id=temp_id)

    try:
        temp_id = int(g['teams']['home']['probablePitcher']['id'])
        update_player_table(temp_id)
        home_probable_pitcher = MlbPlayer.objects.get(player_id=temp_id)
    except KeyError:
        home_probable_pitcher = None

    game_date = g['officialDate']
    game_type = g['gameType']

    temp_id = int(g['venue']['id'])
    update_location_table(temp_id)
    location = MlbLocation.objects.get(location_id=temp_id)

    try:
        games_in_series_current = int(g['seriesGameNumber'])
    except KeyError:
        games_in_series_current = None

    try:
        games_in_series_total = int(g['gamesInSeries'])
    except KeyError:
        games_in_series_total = None

    season = g['season']

    # create the new MLB Game Info entry in the MlbGame table
    g = MlbGame(game_id=game_id,
                away_team=away_team,
                away_probable_pitcher=away_probable_pitcher,
                home_team=home_team,
                home_probable_pitcher=home_probable_pitcher,
                game_date=game_date,
                game_type=game_type,
                location=location,
                games_in_series_current=games_in_series_current,
                games_in_series_total=games_in_series_total,
                season=season)
    g.save()

    update_at_bats_table(g_id)


def update_team_roster(team_object):
    team_id = team_object.team_id
    roster_json = team_roster_json(team_id)['roster']

    # take all players with current team listed and remove this team from them
    players_prev_on_team = MlbPlayer.objects.filter(current_team=team_object)
    for player in players_prev_on_team:
        player.current_team = team_object
        player.save()

    # take all players on api roster and add team as current team - keeps list updated
    for player in roster_json:
        obj = MlbPlayer.objects.get(player_id=player['person']['id'])
        obj.current_team = team_object
        obj.save()
