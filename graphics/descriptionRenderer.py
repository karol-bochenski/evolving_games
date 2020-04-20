import pygame
from game_elements.player import Player
import yaml


class DecriptionRenderer:
    def __init__(self, width, height, app):
        self.width = width
        self.height = height
        self.app = app
        self.font = None

    @property
    def selected(self):
        return self.app.selected

    def setMouse(self, x,y):
        ...

    def click(self):
        ...

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        if self.selected:
            i,j = self.selected
            pieceId = self.app.game_state.board[(i,j)].piece
            piece = self.app.game_state.game.piece_types[Player.P1][pieceId]
            lines = yaml.dump(piece.toDict()).split("\n")
            posY = 0
            lineHeight = min(20,(self.height / len(lines)))
            if (self.font is None):
                self.font = pygame.font.Font('freesansbold.ttf', int(lineHeight) )
            for line in lines:
                textsurface = self.font.render(line, True, (255,255,255))
                surface.blit(textsurface, (0, posY))
                posY += lineHeight
        return surface