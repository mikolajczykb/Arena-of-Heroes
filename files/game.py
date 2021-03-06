from random import randint
import datetime
import pytz
from potions import HealthPotion, SpeedPotion, AttackPotion
import random


def create_potions():
    potions = {
        "HEALTH": HealthPotion,
        "SPEED": SpeedPotion,
        "ATTACK": AttackPotion
    }
    return [potion() for potion in random.choices(list(potions.values()), k=3)]


class Game:
    def __init__(self):
        self.time_start = datetime.datetime.now(pytz.timezone('Poland')).strftime("%c")
        self.last_saved = None
        self.player_turn = 0
        self.turns = 0
        self.potions = create_potions()
        self.players = [None, None]
        self.which_map = randint(0, 3)
        self.is_ready = [False, False]
        self.winner = None
        self.loser = None
        self.add = False
        self.is_saved = False

    def get_next_turn(self):
        self.player_turn = abs(self.player_turn - 1)
        self.turns += 1

    def __str__(self):

        description = "The game is between {0} and {1}.\nStarted: {2}.\nLast saved: {3}."\
                .format(self.players[0].name, self.players[1].name, self.time_start, self.last_saved)

        return description
