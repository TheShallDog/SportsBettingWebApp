from django.db import models
from base_model import BaseModel
import requests
import datetime
import time
from team import Team
from venue import Venue


class Game(BaseModel):
    id = models.IntegerField(primary_key=True)
    date_time = models.DateTimeField(blank=True, null=True)
    game_type = models.CharField(max_length=10, blank=True, null=True)

    # status codes
    abstract_game_state = models.CharField(max_length=100, blank=True, null=True)
    abstract_game_code = models.CharField(max_length=10, blank=True, null=True)
    coded_game_state = models.CharField(max_length=10, blank=True, null=True)
    detailed_state = models.CharField(max_length=100, blank=True, null=True)
    status_code = models.CharField(max_length=10, blank=True, null=True)
    start_time_tbd = models.BooleanField(blank=True, null=True)

    # team information
    away_team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='away_team',
                                  blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)             # only in JSON after complete game
    away_is_winner = models.BooleanField(blank=True, null=True)         # only in JSON after complete game

    home_team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='home_team',
                                  blank=True, null=True)
    home_score = models.IntegerField(blank=True, null=True)             # only in JSON after complete game
    home_is_winner = models.BooleanField(blank=True, null=True)         # only in JSON after complete game

    # location information
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='game_venue',
                              blank=True, null=True)

    # general game info
    double_header = models.CharField(max_length=10, blank=True, null=True)
    day_night = models.CharField(max_length=100, blank=True, null=True)
    total_games_in_series = models.IntegerField(blank=True, null=True)
    current_game_in_series = models.IntegerField(blank=True, null=True)
    series_description = models.CharField(max_length=100, blank=True, null=True)
    season = models.CharField(max_length=10, blank=True, null=True)

    # housekeeping - automatically sets to last saved date time
    last_updated = models.DateTimeField(auto_now=True)

    @staticmethod
    def populate():
        x = 5  # record game data from 5 years ago through this year
        while x >= 0:
            season_year = datetime.date.today().year - x

            start_date = f"01/01/{season_year}"
            end_date = f"12/31/{season_year}"

            # TODO could change end date when x is 0 to being today or through the next week

            url = f"https://statsapi.mlb.com/api/v1/schedule?startDate={start_date}&endDate={end_date}&sportId=1"
            print(url)
            time.sleep(.1)
            response = requests.get(url)
            jason = response.json()

            season_game_ids = []
            for date in jason['dates']:
                for game in date['games']:
                    season_game_ids.append(int(game['gamePk']))

            try:
                existing_game_ids = Game.objects.values_list('game_id', flat=True)
                # remove game_ids already in the database
                game_ids = [game_id for game_id in season_game_ids if game_id not in existing_game_ids]
            except:
                game_ids = season_game_ids

            for game_id in game_ids:
                start = time.time()
                Game.update(game_id)
                print("game id: " + str(game_id) + " updated in " + str(round(time.time() - start)) + " seconds")

            x -= 1

    @staticmethod
    def update(game_id, override=False):
        if Game.objects.get(id=game_id).exists():
            obj = Game.objects.get(id=game_id)
            if obj.last_updated > (datetime.date.today() - datetime.timedelta(weeks=50)):
                if obj.detailed_state in ['Final', 'Completed Early', 'Cancelled']:
                    if override is not True:
                        return

        game_id_json = Game.get_json(game_id)

        # some future games have no pre-populated info and some games have been postponed
        try:
            g = game_id_json['dates'][0]['games'][0]
        except KeyError:
            return

        # check to see if the game was postponed and if so move to the last date in the supplied json
        if g['status']['detailedState'] == 'Postponed':
            g = game_id_json['dates'][len(game_id_json['dates']) - 1]['games'][0]

        # pull out the elements from the json that I want to track for each game
        date_time = datetime.datetime.strptime(g['gameDate'], '%Y-%m-%dT%H:%M:%SZ')
        game_type = g['gameType']

        abstract_game_state = g['status']['abstractGameState']
        abstract_game_code = g['status']['abstractGameCode']
        coded_game_state = g['status']['codedGameState']
        detailed_state = g['status']['detailedState']
        status_code = g['status']['statusCode']
        start_time_tbd = bool(g['status']['startTimeTBD'])

        temp_id = int(g['teams']['away']['team']['id'])
        Team.update(temp_id)
        away_team = Team.objects.get(id=temp_id)
        try:
            away_score = int(g['teams']['away']['score'])
            away_is_winner = bool(g['teams']['away']['isWinner'])
        except KeyError:
            away_score = None
            away_is_winner = None

        temp_id = int(g['teams']['home']['team']['id'])
        Team.update(temp_id)
        home_team = Team.objects.get(id=temp_id)
        try:
            home_score = int(g['teams']['home']['score'])
            home_is_winner = bool(g['teams']['home']['isWinner'])
        except KeyError:
            home_score = None
            home_is_winner = None

        temp_id = int(g['venue']['id'])
        Venue.update(temp_id)
        venue = Venue.objects.get(id=temp_id)

        double_header = g['doubleHeader']
        day_night = g['dayNight']

        try:
            total_games_in_series = int(g['gamesInSeries'])
        except KeyError:
            total_games_in_series = None

        try:
            current_game_in_series = int(g['seriesGameNumber'])
        except KeyError:
            current_game_in_series = None

        series_description = g['seriesDescription']
        season = g['season']

        # create or update the game info row/instance in the Game table
        obj, created = Game.objects.update_or_create(
            id=game_id,
            defaults={'date_time': date_time,
                      'game_type': game_type,
                      'abstract_game_state': abstract_game_state,
                      'abstract_game_code': abstract_game_code,
                      'coded_game_state': coded_game_state,
                      'detailed_state': detailed_state,
                      'status_code': status_code,
                      'start_time_tbd': start_time_tbd,
                      'away_team': away_team,
                      'away_score': away_score,
                      'away_is_winner': away_is_winner,
                      'home_team': home_team,
                      'home_score': home_score,
                      'home_is_winner': home_is_winner,
                      'venue': venue,
                      'double_header': double_header,
                      'day_night': day_night,
                      'total_games_in_series': total_games_in_series,
                      'current_game_in_series': current_game_in_series,
                      'series_description': series_description,
                      'season': season})
        obj.save()

#        row = Game(id=game_id,
#                   date_time=date_time,
#                   game_type=game_type,
#                   abstract_game_state=abstract_game_state,
#                   abstract_game_code=abstract_game_code,
#                   coded_game_state=coded_game_state,
#                   detailed_state=detailed_state,
#                   status_code=status_code,
#                   start_time_tbd=start_time_tbd,
#                   away_team=away_team,
#                   away_score=away_score,
#                   away_is_winner=away_is_winner,
#                   home_team=home_team,
#                   home_score=home_score,
#                   home_is_winner=home_is_winner,
#                   venue=venue,
#                   double_header=double_header,
#                   day_night=day_night,
#                   total_games_in_series=total_games_in_series,
#                   current_game_in_series=current_game_in_series,
#                   series_description=series_description,
#                   season=season)
#        row.save()

    @staticmethod
    def get_json(game_id):
        url = f"https://statsapi.mlb.com/api/v1/schedule?gamePk={game_id}"
        print(url)
        time.sleep(.1)
        response = requests.get(url)
        return response.json()
