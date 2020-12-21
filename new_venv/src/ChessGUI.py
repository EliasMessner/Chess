import pygame as p
import time

class ChessGUI:
    """
    Generally applicable class for Chess GUI. An instance of this class will hold all the information about the
    current state of the chess game's GUI. This Instance can draw a given gameState onto a pyGame screen.
    """
    def __init__(self, dimension=(8, 8), width=512, height=width, imgPath="../images/", backGroundColor="white"):
        self.dimension = dimension
        self.width = width
        self.height = height
        self.sqSize = self.height//self.dimension
        self.backGroundColor = backGroundColor
        self.pointerPiece = "--"
        self.highlightings = {}  # {(col, row): (color, milliseconds, timeSet)}

        # load images
        self.images = {}
        pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            self.images[piece] = p.transform.scale(p.image.load(imgPath + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        self.images["hl"] = p.transform.scale(p.image.load(imgPath + "highlight.png"), (SQ_SIZE, SQ_SIZE))

    def drawGameState(self, screen, gameState, mousePos):
        screen.fill(self.backGroundColor)
        self._drawBoard(screen)
        self._drawPieces(screen, gameState.board)
        self._updateHighlightings(screen)
        self._drawPointerImage(screen, mousePos)

    def getSquareUnderCursor(pos):
        col = pos[0] // self.sqSize
        row = pos[1] // self.sqSize
        return col, row

    def cursorOnBoard(self, pos):
        if pos[0] in range(self.width) and pos[1] in range(self.height):
            return True
        return False

    def _drawBoard(self, screen):
        colors = ["white", "gray"]
        for x in range(self.dimension):
            for y in range(self.dimension):
                p.draw.rect(screen, p.Color(colors[(x + y) % 2]),
                            p.rect.Rect(x * self.sqSize, y * self.sqSize, self.sqSize, self.sqSize))

    def _drawPieces(self, board):
        for x in range(self.dimension):
            for y in range(self.dimension):
                piece = board[y][x]
                if piece != "--":
                    screen.blit(self.images[piece], p.Rect(x * self.sqSize, y * self.sqSize, self.sqSize, self.sqSize))

    def _updateHighlightings(self, screen):
        """
        Deletes all the highlightings that have expired and redraws the remaining ones.
        """
        toPop = []
        for field in self.highlightings:
            color, milliseconds, timeSet = self.highlightings[field]
            now = time.time()
            if milliseconds is not None and timeSet * 1000 + milliseconds < now * 1000:
                toPop.append(field)
                continue
            self._highlightField(field, screen, color=color)
        for field in toPop:
            self.highlightings.pop(field)

    def _highlightField(self, field, screen, color):
        col = field[0]
        row = field[1]
        coloredHighlight = self.images["hl"].copy()
        self._colorSurface(coloredHighlight, color)
        screen.blit(coloredHighlight, p.Rect(col * self.sqSize, row * self.sqSize, self.sqSize, self.sqSize))

    def _colorSurface(self, surface, color):
        red = color[0]
        green = color[1]
        blue = color[2]
        arr = p.surfarray.pixels3d(surface)
        arr[:, :, 0] = red
        arr[:, :, 1] = green
        arr[:, :, 2] = blue

    def _drawPointerImage(screen, pos):
        if self.pointerPiece == "--" or not self.cursorOnBoard(pos):
            return
        pointerImg = self.images[self.pointerPiece]
        pointerImgRect = pointerImg.get_rect()
        pointerImgRect.center = pos
        screen.blit(pointerImg, pointerImgRect)
