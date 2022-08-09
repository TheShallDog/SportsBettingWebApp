import requests
import create_mlb_tables
from datetime import date

BASE_URL = "https://statsapi.mlb.com"


def play_by_play_json(game_id):
    url = BASE_URL + f"/api/v1/game/{game_id}/playByPlay"
    print(url)
    response = requests.get(url)
    p_b_p_json = response.json()
    return p_b_p_json


def games_to_update():
    # TODO make this use a GUI to ask the date range and tell the user the last date of games from database.
    #  suggest from the last date to yesterday - should also check for games to be complete before sending to updater
    return ["661312"]


def update_at_bats(game_id):
    pbp_json = play_by_play_json(game_id)
    at_bats = pbp_json['allPlays']

    if not bool(at_bats[0]['about']['isComplete']):
        return f"Game {game_id} not yet finished"

    column_names = create_mlb_tables.at_bats_table_columns()
    # away batting lineup list
    away_lu = []
    # home batting lineup list
    home_lu = []
    for at_bat in at_bats:
        # create a list to match values to column names, use tuple index for reference
        # then combine into tuple at end for insert statement
        values = list(column_names)
        for column in column_names:
            i = column_names.index(column)
            match column:
                case 'Game_ID':
                    values[i] = game_id

                case 'At_Bat':
                    values[i] = int(at_bat['atBatIndex']) + 1

                case 'Inning':
                    values[i] = at_bat['about']['inning']

                case 'Inning_Half':
                    team = at_bat['about']['halfInning']
                    if team == 'top':
                        values[i] = 'away'
                    else:
                        values[i] = 'home'

                case 'Event_Type':
                    values[i] = at_bat['result']['eventType']

                case 'Pitcher_ID':
                    values[i] = at_bat['matchup']['pitcher']['id']

                case 'Pitcher_Hand':
                    values[i] = at_bat['matchup']['pitchHand']['code']

                case 'Batter_ID':
                    batter_id = at_bat['matchup']['batter']['id']
                    values[i] = batter_id
                    # set batting lineup information
                    inning_half = at_bat['about']['halfInning']
                    if inning_half == 'top':
                        away_lu.append(batter_id) if batter_id not in away_lu else away_lu
                    elif inning_half == 'bottom':
                        home_lu.append(batter_id) if batter_id not in home_lu else home_lu

                case 'Batter_Hand':
                    values[i] = at_bat['matchup']['batSide']['code']

                case 'Lineup_Position':
                    position = 0
                    inning_half = at_bat['about']['halfInning']
                    b_id = at_bat['matchup']['batter']['id']
                    # these two lists are set in the batter ID section
                    if inning_half == 'top':
                        position = away_lu.index(b_id)
                    elif inning_half == 'bottom':
                        position = home_lu.index(b_id)

                    values[i] = position

                case 'Single':
                    if at_bat['result']['eventType'] == 'single':
                        values[i] = True
                    else:
                        values[i] = False

                case 'Double':
                    if at_bat['result']['eventType'] == 'double':
                        values[i] = True
                    else:
                        values[i] = False

                case 'Triple':
                    if at_bat['result']['eventType'] == 'triple':
                        values[i] = True
                    else:
                        values[i] = False

                case 'Home_Run':
                    if at_bat['result']['eventType'] == 'home_run':
                        values[i] = True
                    else:
                        values[i] = False

                case 'Scoring_Play':
                    values[i] = bool(at_bat['about']['isScoringPlay'])

                case 'Scoring_Player_1':
                    scorers = int(at_bat['result']['rbi'])
                    if scorers > 0:
                        scoring_runners = []
                        for runner in at_bat['runners']:
                            if bool(runner['details']['isScoringEvent']):
                                scoring_runners.append(runner['details']['runner']['id'])
                        values[i] = scoring_runners[0]
                    else:
                        values[i] = None

                case 'Scoring_Player_2':
                    scorers = int(at_bat['result']['rbi'])
                    if scorers > 1:
                        scoring_runners = []
                        for runner in at_bat['runners']:
                            if bool(runner['details']['isScoringEvent']):
                                scoring_runners.append(runner['details']['runner']['id'])
                        values[i] = scoring_runners[1]
                    else:
                        values[i] = None

                case 'Scoring_Player_3':
                    scorers = int(at_bat['result']['rbi'])
                    if scorers > 2:
                        scoring_runners = []
                        for runner in at_bat['runners']:
                            if bool(runner['details']['isScoringEvent']):
                                scoring_runners.append(runner['details']['runner']['id'])
                        values[i] = scoring_runners[2]
                    else:
                        values[i] = None

                case 'Scoring_Player_4':
                    scorers = int(at_bat['result']['rbi'])
                    if scorers > 3:
                        scoring_runners = []
                        for runner in at_bat['runners']:
                            if bool(runner['details']['isScoringEvent']):
                                scoring_runners.append(runner['details']['runner']['id'])
                        values[i] = scoring_runners[3]
                    else:
                        values[i] = None

                case 'RBI':
                    values[i] = int(at_bat['result']['rbi'])

                case 'Earned_Runs':
                    scorers = int(at_bat['result']['rbi'])
                    if scorers > 0:
                        er = 0
                        for runner in at_bat['runners']:
                            if bool(runner['details']['earned']):
                                er += 1
                        values[i] = er
                    else:
                        values[i] = 0

                case 'Strikeout':
                    if at_bat['result']['eventType'] == 'strikeout':
                        values[i] = True
                    else:
                        values[i] = False

                case 'Stolen_Bases':
                    stolen_bases = 0
                    for runner in at_bat['runners']:
                        if 'stolen' in runner['details']['eventType']:
                            stolen_bases += 1
                    values[i] = stolen_bases

                case 'Base_Stealer_1':
                    base_stealers = []
                    for runner in at_bat['runners']:
                        if 'stolen' in runner['details']['eventType']:
                            base_stealers.append(runner['details']['runner']['id'])
                    if len(base_stealers) > 0:
                        values[i] = base_stealers[0]
                    else:
                        values[i] = None

                case 'Base_Stealer_2':
                    base_stealers = []
                    for runner in at_bat['runners']:
                        if 'stolen' in runner['details']['eventType']:
                            base_stealers.append(runner['details']['runner']['id'])
                    if len(base_stealers) > 1:
                        values[i] = base_stealers[1]
                    else:
                        values[i] = None

                case 'Base_Stealer_3':
                    base_stealers = []
                    for runner in at_bat['runners']:
                        if 'stolen' in runner['details']['eventType']:
                            base_stealers.append(runner['details']['runner']['id'])
                    if len(base_stealers) > 2:
                        values[i] = base_stealers[2]
                    else:
                        values[i] = None

                case 'Error':
                    if 'error' in at_bat['result']['eventType']:
                        values[i] = True
                    else:
                        values[i] = False

                case 'Error_Committer':
                    if 'error' in at_bat['result']['eventType']:
                        for runner in at_bat['runners']:
                            if 'error' in runner['details']['eventType']:
                                for credit in runner['credits']:
                                    if 'error' in credit['credit']:
                                        values[i] = credit['player']['id']
                    else:
                        values[i] = None

                case 'Description':
                    values[i] = at_bat['result']['description']

                case 'Date_Updated':
                    values[i] = date.today()

                case _:
                    i = column_names.index(column)
                    values[i] = "update method"
        print(values)
        values = tuple(values)


def update_data():
    game_ids = games_to_update()
    for game in game_ids:
        # update_game_info(game)
        update_at_bats(game)
        # update_player_info(game)
        # update_team_info(game)
        # update_location_info(game)


if __name__ == '__main__':
    update_data()
    print("done")
