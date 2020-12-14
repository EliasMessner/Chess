"""
Client for Chess multiplayer version. Handle graphics, server connection and user input.
"""

import pygame as p
from ChessMain import loadImages, drawGameState

IMAGES = {}
WIDTH = HEIGHT = 512
CHECK_TEXT = "Check!"
CHECKMATE_TEXT = "Checkmate!"
STALEMATE_TEXT = "Stalemate!"
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
BACKGROUND_COLOR = "white"
MAX_FPS = 40

class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

    def draw(self, win):
        p.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = p.font.SysFont("Monospace", 20)
        text = font.render(self.text, True, (255, 255, 255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


def menu_screen():
    p.init()
    run = True
    p.display.set_caption("Chess Multiplayer")
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    connectBtn = Button("Connect", WIDTH//3, HEIGHT//2, p.Color("lightgrey"))

    while run:
        p.display.flip()
        clock.tick(MAX_FPS)
        screen.fill(BACKGROUND_COLOR)
        connectBtn.draw(screen)
        for e in p.event.get():
            if e.type == p.QUIT:
                run = False
                continue
            elif e.type == p.MOUSEBUTTONDOWN:
                pos = p.mouse.get_pos()
                if connectBtn.click(pos):
                    # connect to server
                    # TODO
                    print("trying to connenct...")
                    pass

    p.quit()


if __name__ == "__main__":
    menu_screen()
