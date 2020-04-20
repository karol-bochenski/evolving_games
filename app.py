import pygame
from pygame.locals import *
from game_elements.player import Player
from graphics.boardRenderer import BoardRenderer
from graphics.descriptionRenderer import DecriptionRenderer
from game_definitions.boardGame import BoardGame
from game_elements.board import Board
from threading import Thread
from time import sleep
from mcts import mcts
import yaml


class App:
    widgets = []

    def __init__(self, game, player1Agent="USER", player2Agent="USER"):
        self._running = True
        self._display_surf = None
        self.selected = None
        self.agents = {Player.P1: player1Agent, Player.P2: player2Agent}
        self.game_state = game.initialState()
        self.boardRenderer = BoardRenderer(600,600, self)
        boardWidth, boardHeight = self.boardRenderer.getActualSize()
        self.addWidget(self.boardRenderer, (0,0))
        self.addWidget(DecriptionRenderer(300,600, self), (boardWidth,0))
        self.selectedMoves = None
        self.windowWidth = int(boardWidth + 300)
        self.windowHeight = int(boardHeight)
        
    def currentAgent(self):
        return self.agents[self.game_state.currentPlayer]

    def selectAt(self, position):
        if self.currentAgent() != "USER":
            return
        square = self.game_state.board[position]
        if(square.owner == self.game_state.currentPlayer):
            self.selectedMoves = { move.destination:move for move in self.game_state.possibleMoves if move.origin == position }
            self.selected = position
        
    def playout(self):
        Thread(target=self.on_execute).start()
        while not self.game_state.finished and self._running:
            agent = self.currentAgent()
            if agent == "USER":
                sleep(1/60)
                continue
            if agent == "MCTS":
                self.game_state = mcts.findNextMove(self.game_state).game_state    
        self.finished = True

    def addWidget(self, widget, position):
        self.widgets.append((widget, position))

    def on_click(self, position):
        if self.currentAgent() != "USER":
            return
        if self.selectedMoves is None:
            self.selectAt(position)
        else:
            self.applyMoveOrDeselect(position)

    def applyMoveOrDeselect(self, position):
        if(not position in self.selectedMoves.keys()):
            self.selected = None
            self.selectedMoves = None
            return self.selectAt(position)
        self.game_state = self.game_state.applyMove(self.selectedMoves[position])
        self.canMove = { move.origin for move in self.game_state.possibleMoves }
        self.selected = None
        self.selectedMoves = None

    def updateSelectedMoves(self, position):
        if not self.selected is None:
            return
        square = self.game_state.board[position]
        if(square.owner == self.game_state.currentPlayer):
            self.selectedMoves = { move.destination:move for move in self.game_state.possibleMoves if move.origin == position }
        else:
            self.selectedMoves = None

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth,self.windowHeight), pygame.HWSURFACE)    
        self._running = True
    
    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        clock = pygame.time.Clock()
 
        while( self._running ):
            (x,y) = pygame.mouse.get_pos()
            ev = pygame.event.get()
            clicked = False
            for event in ev:
                if event.type == pygame.MOUSEBUTTONUP:
                    clicked = True
                if event.type == pygame.QUIT:
                    self._running = False
                    pygame.quit()
                    return

            for widget, (posx, posy) in self.widgets:
                widget.setMouse(x - posx, y - posy)
                if clicked:
                    widget.click()
                self._display_surf.blit(widget.render(), (posx, posy))

            pygame.event.pump()
            pygame.display.flip()
            clock.tick(60)

theApp = None
def startApp(game, player1agent, player2agent):
    global theApp
    theApp = App(game, player1agent, player2agent)
    theApp.playout()

def startGameThread(game, player1agent, player2agent):
    thread = Thread(target=startApp, args=[game, player1agent,player2agent])
    thread.start()
    return thread

if __name__ == '__main__':
    App("generated/games/game_34")
