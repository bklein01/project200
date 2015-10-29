"""User statistics M/C.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:

"""

import math
from core.datamodel import DataModelController, Collection


class UserStatistics(DataModelController):

    MODEL_RULES = {
        'games_won': ('games_won', int, None),
        'games_lost': ('games_lost', int, None),
        'history': ('history', Collection.List(int), None),
        'twofers': ('twofers', int, None),
        'won_bet_rounds': ('won_bet_rounds', int, None),
        'lost_bet_rounds': ('lost_bet_rounds', int, None),
        'won_counter_rounds': ('won_counter_rounds', int, None),
        'lost_counter_rounds': ('lost_counter_rounds', int, None),
        'avg_win_bet': ('avg_bet_win', int, None),
        'avg_counter_win': ('avg_counter_win', int, None),
        'team_mates': ('team_mates', Collection.Dict(list), None),
        'elo': ('elo', float, None),
        'rank': ('rank', int, None),
        'ranked_wins': ('ranked_wins', int, None)
    }

    def __init__(self, games_won=0, games_lost=0, history=None, twofers=0,
                 won_bet_rounds=0, lost_bet_rounds=0, won_counter_rounds=0,
                 lost_counter_rounds=0, avg_win_bet=0, avg_counter_win=0,
                 elo=800.0, rank=1, ranked_wins=0, team_mates=None):
        if not history:
            history = []
        if not team_mates:
            team_mates = {}
        (self.games_won, self.games_lost, self.history, self.twofers,
         self.won_bet_rounds, self.lost_bet_rounds, self.won_counter_rounds,
         self.lost_counter_rounds, self.avg_win_bet, self.avg_counter_win,
         self.elo, self.rank, self.ranked_wins, self.team_mates) = (
            games_won, games_lost, history, twofers, won_bet_rounds,
            lost_bet_rounds, won_counter_rounds, lost_counter_rounds,
            avg_win_bet, avg_counter_win, elo, rank, ranked_wins, team_mates)
        super(UserStatistics, self).__init__(self.__class__.MODEL_RULES)

    def won_bet_round(self, bet):
        self.avg_win_bet = _avg(self.won_bet_rounds,
                                self.avg_win_bet, bet)
        self.won_bet_rounds += 1
        if bet is 100:
            self.twofers += 1

    def lost_bet_round(self):
        self.lost_bet_rounds += 1

    def won_counter_round(self, points):
        self.avg_counter_win = _avg(self.won_counter_rounds,
                                    self.avg_counter_win, points)
        self.won_counter_rounds += 1

    def lost_counter_round(self):
        self.lost_counter_rounds += 1

    def add_game_to_history(self, game_id):
        self.history.insert(0, game_id)
        self._update_model_collection('history', {'action': 'insert',
                                                  'index': 0})

    def update_comp_game_stats(self, game_id, team_elo, opposing_team_elo,
                               win):
        self.add_game_to_history(game_id)
        if win:
            self.games_won += 1
            self.ranked_wins += 1
        else:
            self.games_lost += 1
        games_played = self.games_won + self.games_lost
        elo_change = _elo_calc(team_elo, games_played, opposing_team_elo, win,
                               self.ranked_wins)
        self.elo = min(200, self.elo + elo_change)
        self.rank = _elo_rank(self.elo, self.ranked_wins)

    def update_casual_game_stats(self, game_id, team_mate, opposing_team_elo,
                                 win):
        self.add_game_to_history(game_id)
        if win:
            self.games_won += 1
            self.elo += 1.0
        else:
            self.games_lost += 1
            self.elo = min(200, self.elo - 1)
        self.rank = _elo_rank(self.elo, self.ranked_wins)
        if team_mate not in self.team_mates:
            self.team_mates[team_mate] = (0, 0)
        self.team_mates[team_mate][1] = _performance_rating(
            self.team_mates[team_mate][0],
            self.team_mates[team_mate][1],
            opposing_team_elo, win)
        self.team_mates[team_mate][0] += 1

    def update_free_game_stats(self, game_id):
        self.add_game_to_history(game_id)


def _avg(count, avg, new_num):
    """Incremental average.

    :param count: int -- The previous total.
    :param avg: float -- The previous average.
    :param new_num: int|float -- The new number.
    :return: float -- The new average.
    """
    if not count:
        return float(new_num)
    return (count * avg + new_num) / (count + 1.0)


def _performance_rating(count, rating, opposing_elo, win=True):
    """Elo-based performance rating.

    Algorithm adapted from: https://en.wikipedia.org/wiki/Elo_rating_system#Performance_rating

    :param count: int -- Number of games won in team.
    :param rating: float -- Current team rating.
    :param opposing_elo: float -- Average elo of opposing team.
    :param win: bool -- Whether to update with a win or a loss.
    :return: float -- New team rating
    """
    add = 400 if win else -400
    if not count:
        return opposing_elo + add
    return (rating * count + opposing_elo + add) / (count + 1.0)


def _effective_games(num_games, player_elo):
    """Determine effective number of games for elo calculation.

    :param num_games: int
    :param player_elo: float
    :return: int -- Effective number of games.
    """
    if player_elo > 2355:
        return num_games
    else:
        fifty = 50 / math.sqrt(0.662 + 0.00000739 * math.pow(2569 - player_elo, 2))
        num_games -= 50
        if num_games < 0:
            num_games = 0
        return (num_games - 50) + int(0.5 + fifty)


def _prediction(player_elo, opponent_elo):
    """Standard elo prediction probability.

    Based on the USCF rating algorithm. Predicts the probability of the player
    winning over the opponent.

    :param player_elo: float
    :param opponent_elo: float
    :return: float -- Probability of win.
    """
    exponent = -1 * (player_elo - opponent_elo) / 400.0
    return 1.0 / (1.0 + math.pow(10, exponent))


def _elo_calc(player_elo, num_games, opponent_elo, win, num_games_won):
    """Standard elo calculation.

    Based on the USCF rating algorithm.

    :param player_elo: float
    :param num_games: int -- Total number of games played.
    :param opponent_elo: float
    :param win: bool
    :param num_games_won: int -- Total number of games won.
    :return: float -- Elo change.
    """
    outcome = 1 if win else 0
    effective_games = _effective_games(num_games, player_elo)
    if num_games_won <= 10:
        effective_games += num_games_won
        prediction = _unranked_prediction(player_elo, opponent_elo)
    else:
        prediction = _prediction(player_elo, opponent_elo)
    k_factor = 800.0 / effective_games
    return k_factor * (outcome - prediction)


def _unranked_prediction(player_elo, opponent_elo):
    """Special elo prediction probability for unranked player.

    :param player_elo: float
    :param opponent_elo: float
    :return: float -- Probability of win.
    """
    if player_elo >= opponent_elo + 400:
        prob = 1.0
    elif player_elo <= opponent_elo - 400:
        prob = 0.0
    else:
        prob = 0.5 + (player_elo - opponent_elo) / 800
    return prob


def _elo_rank(player_elo, num_games_won):
    if num_games_won < 10:
        return 1
    else:
        return max(14, 1 + (player_elo / 200))
