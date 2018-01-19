import pygame as pg
from . import state_engine
from player import Player
from map import Map
import score
import item
import monster

CONFIG_JUMP_KEY = [pg.K_SPACE, pg.K_RSHIFT, pg.K_LSHIFT]
CONST_DEFAULT_JUMP_KEY = 0


class StateGame(state_engine.GameState):
    """
    Main state for the game, is the master for the map and the player.
    """

    def __init__(self, options, after_pause, seed=None):
        """
        @rtype: None
        """
        state_engine.GameState.__init__(self)
        self.current_opts = options
        self.after_pause = after_pause

        self.players = []
        for i in range(int(self.current_opts["NUMBER_OF_PLAYER"])):
            if i < len(CONFIG_JUMP_KEY):
                new_player = Player(50 + i * 100, 0, 8, 0, self.current_opts["CHARACTER"], CONFIG_JUMP_KEY[i])
            else:
                new_player = Player(50 + i * 100, 0, 8, 0, self.current_opts["CHARACTER"],
                                    CONFIG_JUMP_KEY[CONST_DEFAULT_JUMP_KEY])
            self.players.append(new_player)

        self.items = item.ItemManager()
        self.monsters = monster.MonsterManager()

        self.game_map = Map(self.items, seed)

        self.acceleration_x = 0  # As said, x variables is not of any use at the moment
        self.acceleration_y = 1
        self.frame = 0  # Number of frame since beginning
        self.max_speed = self.game_map.dim_bloc
        self.next_state = "MAIN_MENU"
        self.score = score.Score("", 0)
        self.difficulty = 1



    def get_event(self, event):
        """
        Do something according to the last event that happened.
        @param event: the last event that occurred.
        @type event: pygame.event
        @rtype: None
        """
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next_state = "PAUSE"
                self.persist["MAP"] = self.game_map
                self.persist["NEXT_STATE"] = self.after_pause
                self.done = True

    def update(self):
        """
        Update the state.
        @rtype: None
        """
        # Score Update
        self.score.update(self.frame)

        # Something to do in case the game is over
        for player in self.players:
            player.update(self.game_map, self.difficulty, self.acceleration_y, self.max_speed)

        # Update of the game_map
        self.game_map.update(int(self.players[0].v_x * self.difficulty))

        self.items.update(int(self.players[0].v_x * self.difficulty), self.players[0], self.game_map)
        for player in self.players[1:]:
            self.items.update(0, player, self.game_map)


        self.game_map.need_antidote = max(0, self.game_map.need_antidote -1)

        #Update the monsters
        self.monsters.update(self.game_map, self.difficulty, self.acceleration_y, self.max_speed, 0, self.players)

        # This part got to stay updated
        self.frame += 1

        self.difficulty = 1 + self.score.score / 2000 + self.players[0].mod_difficulty

    def startup(self, persistent):
        """
        Called when a state resumes being active.
        @param persistent: a dict passed from state to state
        @type persistent: dict{}
        @rtype: None
        """
        self.persist = persistent

    def draw(self, surface):
        """
        Draw everything to the screen
        @param surface: The surface that will be displayed.
        @type surface: pygame.Surface
        @rtype: None
        """
        self.game_map.display(surface)
        for player in self.players:
            player.draw(surface)
        self.items.display(surface, 0, 1200)
        self.score.draw(surface, self.font)
        self.monsters.display(surface)
