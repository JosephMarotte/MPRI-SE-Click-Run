import pygame as pg
from . import state_game
import os
import replay as rp

CONFIG_JUMP_KEY = [pg.K_SPACE, pg.K_RSHIFT, pg.K_LSHIFT]
CONST_DEFAULT_JUMP_KEY = 0


class FakeEvent:
    type = pg.KEYDOWN

    def __init__(self, key):
        self.key = key


class StateGameReplay(state_game.StateGame):
    """
    Main state for the game, is the master for the map and the player.
    """

    def __init__(self, replay="last_game_replay"):
        """
        @param replay: replay path
        @type replay: str
        @rtype: None
        """
        if os.path.isfile(replay):
            self.replay = rp.Replay(path=replay)
            state_game.StateGame.__init__(self, self.replay.get_opts(), ["GAME_REPLAY", "MAIN_MENU"], self.replay.seed)

    def startup(self, persistent):
        try:
            self = self.__init__(persistent["REPLAY_PATH"])
        except KeyError:
            self = self.__init__()

    def get_event(self, event):
        """
        Do something according to the last event that happened.
        @param event: the last event that occurred.
        @type event: pygame.event
        @rtype: None
        """
        state_game.StateGame.get_event(self, event)

    def update(self):
        """
        Update the state.
        @rtype: None
        """
        # Loading the events from the replay
        key = self.replay.read(self.frame)
        if key:
            event = FakeEvent(key)
            for player in self.players:
                player.get_event(event, self.game_map)
        state_game.StateGame.update(self)

        # Something to do in case the game is over
        if all([player.is_dead for player in self.players]):
            self.persist = {"MAP": self.game_map}
            self.next_state = "GAME_OVER"
            self.done = True
