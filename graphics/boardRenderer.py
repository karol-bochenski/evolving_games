import pygame
from mcts import mcts
from mcts.alphabeta import AlphaBeta
from game_elements.player import Player

class BoardRenderer:
    def __init__(self, width, height, app):
        self.width = width
        self.height = height
        self.app = app
        self.font = None

    @property
    def selected(self):
        return self.app.selected

    @property
    def columns(self):
        return self.app.game_state.board.width

    @property
    def rows(self):
        return self.app.game_state.board.height

    @property
    def scale(self):
        board_ratio = self.columns / self.rows
        surface_ratio = self.width / self.height
        return (self.width / self.columns) if (board_ratio > surface_ratio) else (self.height / self.rows)

    def getActualSize(self):
        return self.columns * self.scale, self.rows * self.scale

    @property
    def canMove(self):
        return { move.origin for move in self.app.game_state.possibleMoves }

    def setMouse(self, column, row):
        self.mouseX = column
        self.mouseY = row
    
    def getMousePos(self):
        return int(self.mouseX // self.scale), int(self.mouseY // self.scale)

    def click(self):
        self.app.on_click(self.getMousePos())

    def renderBackground(self, x,y):
        return (255,255,255) if (((x+y) % 2) == 0) else (200,200,200)

    def renderSelected(self, x,y, color):
        if self.selected is None or self.selected != (x,y):
            return color
        return (55, 255, 105)

    def renderPotentialMove(self, x,y, color):
        if self.app.selectedMoves is None or (not (x,y) in self.app.selectedMoves.keys()):
            return color
        containsEnemy = (self.app.game_state.board[(x,y)].owner == ~self.app.game_state.currentPlayer)
        if containsEnemy:
            return (255, 105, 105)
        else:
            return (155, 255, 205)

    def renderHoveredMoves(self, x,y, color):
        if self.app.selectedMoves is None or (not (x,y) in self.app.selectedMoves.keys()):
            return color
        containsEnemy = (self.app.game_state.board[(x,y)].owner == ~self.app.game_state.currentPlayer)
        if containsEnemy:
            return (255, 155, 155)
        else:
            return (175, 255, 235)

    def renderCanMove(self, x,y, color):
        if (x,y) in self.canMove:
            return (155, 255, 205)
        return color

    def renderCell(self, x,y):
        isHover = self.getMousePos() == (x,y)
        
        color = self.renderBackground(x,y)
        if(self.selected is None):
            color = self.renderCanMove(x,y, color)
            color = self.renderHoveredMoves(x,y, color)
        else:
            color = self.renderSelected(x,y, color)
            color = self.renderPotentialMove(x,y,color)

        if isHover:
            color = (color[0] - 20,color[1] - 20,color[2] - 20)
        return color

    def render(self):
        self.app.updateSelectedMoves(self.getMousePos())
        if (self.font is None):
            self.font = pygame.font.Font('freesansbold.ttf',30)
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        for i in range(self.columns):
            for j in range(self.rows):
                color = self.renderCell(i,j)
                posX, posY = i * self.scale, j * self.scale
                pygame.draw.rect(surface, color, pygame.Rect(posX, posY, self.scale-1, self.scale-1))
                square = self.app.game_state.board[(i,j)]
                if(square.owner != None):
                    textsurface = self.font.render(str(square.piece), True, square.owner.color())
                    surface.blit(textsurface, (posX + (self.scale//3), posY + (self.scale // 3)))
        if (self.app.game_state.finished):
            overlay = self.getEndingOverlay()
            surface.blit(overlay, (0,0))    
            
        return surface
    
    def getEndingOverlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        overlay.fill((0,0,0,180))
        if(self.app.game_state.winner):
            if(self.app.game_state.winner == Player.P1):
                textsurface = self.font.render("Player 1(green) won" , True, (255,255,255))
            else:
                textsurface = self.font.render("Player 2(red) won", True, (255,255,255))
        else:
            textsurface = self.font.render("Draw", True, (255,255,255))
        text_width,text_height = textsurface.get_width(), textsurface.get_height()
        width, height = self.getActualSize()
        overlay.blit(textsurface, ((width - text_width)/2, (height - text_height)/2))
        return overlay