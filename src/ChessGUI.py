import pygame as p
import time

from Util import *


class ChessGUI:
    """
    Generally applicable class for Chess GUI. An instance of this class will hold all the information about the
    current state of the chess game's GUI. This Instance can draw a given game onto a pyGame screen.
    """
    def __init__(self, dimension=8, width=512, height=None, imgPath="../images/", backGroundColor="white",
                 whiteFieldColor="white", blackFieldColor="grey"):
        """
        :param dimension: The dimension of the chess game (8 if not specified)
        :type dimension: int
        :param width: the width of the chess game in pixels (512 if not specified)
        :type width: int
        :param height: the height of the chess game in pixels (the same as width if not specified)
        :type height: int
        :param imgPath: The path where the images for the chess pieces and the highlighting of the field are stored.
        The images must be png files with filenames representing each piece, the first char represents the color of the
        piece, 'b' or 'w'. the second char represents the type of the piece 'K', 'Q', 'B', 'N', 'R' or 'p'. The path is
        assumed to be "../images/" if not specified otherwise.
        :type imgPath: str
        :param backGroundColor: The background color of the pygame (not visible under the board itself). Must be a
        valid descriptive color string. Will be white, if not specified.
        :type backGroundColor: str
        :param whiteFieldColor: The color of a white field on the board. "white" by default. Must be a
        valid descriptive color string.
        :type whiteFieldColor: str
        :param blackFieldColor: The color of a black field on the board. "grey" by default. Must be a
        valid descriptive color string.
        :type blackFieldColor: str
        """
        if not isValidColorString(backGroundColor):
            raise ValueError(f"\"{backGroundColor}\" is not a valid color string")
        if not isValidColorString(whiteFieldColor):
            raise ValueError(f"\"{whiteFieldColor}\" is not a valid color string")
        if not isValidColorString(blackFieldColor):
            raise ValueError(f"\"{blackFieldColor}\" is not a valid color string")
        if not (isinstance(dimension, int) and dimension > 0):
            raise ValueError(f"Parameter dimension must be positive int, instead found {type(dimension)}, ({dimension}).")
        if not (isinstance(width, int) and width > 0):
            raise ValueError(f"Parameter width must be positive int, instead found {type(width)}, ({width}).")
        if height is not None and not (isinstance(height, int) and height > 0):
            raise ValueError(f"Parameter height must be positive int, instead found {type(height)}, ({height}).")
        self.dimension = dimension
        self.width = width
        self.height = height if height is not None else width
        self.sqSize = self.height//self.dimension
        self.backGroundColor = backGroundColor
        self.whiteFieldColor = whiteFieldColor
        self.blackFieldColor = blackFieldColor
        self.pointerPiece = "--"
        self.highlightings = {}  # {(col, row): (color, milliseconds, timeSet)}

        # load images
        self.images = {}
        self._vacantFieldName = "--"
        self._pieceNames = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in self._pieceNames:
            self.images[piece] = p.transform.scale(p.image.load(imgPath + piece + ".png"), (self.sqSize, self.sqSize))
        self.images["hl"] = p.transform.scale(p.image.load(imgPath + "highlight.png"), (self.sqSize, self.sqSize))

    def drawGameState(self, screen, board, mousePos):
        """
        Draws the game state onto a pygame surface
        :param screen: the pygame surface to draw on
        :type screen: pygame.Surface
        :param board: a 2D list of strings representing each field, the first char represents the color of the piece,
        'b' or 'w'. the second char represents the type of the piece 'K', 'Q', 'B', 'N', 'R' or 'p' "--" represents a
        vacant field
        :type board: list of list of str
        :param mousePos: the current position of the mouse
        :type mousePos: tuple of (int, int)
        """
        if not len(board) == self.dimension and all(len(board[i]) == self.dimension for i in board):
            raise ValueError(f"Wrong Board dimension.")
        if not all(all(field in (self._pieceNames + [self._vacantFieldName]) for field in row) for row in board):
            raise ValueError("Bad Field String on board.")
        if not isinstance(screen, p.Surface):
            raise ValueError(f"Parameter screen must be pygame.Surface, instead found {type(screen)}.")
        if not isinstance(mousePos, tuple) and len(mousePos) == 2 and all(isinstance(i, int) for i in mousePos):
            raise ValueError(f"Parameter mousePos must be tuple of (int, int), instead found {type(mousePos)}")
        screen.fill(self.backGroundColor)
        self._drawBoard(screen)
        self._drawPieces(screen, board)
        self._updateHighlightings(screen)
        self._drawPointerImage(screen, mousePos)

    def getSquareUnderCursor(self):
        """
        Return the position as tuple of ints i.e. (column, row) of the square under the cursor. If the cursor is not on
        the board, return None.
        """
        if not self.cursorOnBoard():
            return None
        pos = p.mouse.get_pos()
        col = pos[0] // self.sqSize
        row = pos[1] // self.sqSize
        return col, row

    def cursorOnBoard(self):
        """
        Return True if the cursor is on the board, otherwise return False
        """
        pos = p.mouse.get_pos()
        if pos[0] in range(self.width) and pos[1] in range(self.height):
            return True
        return False

    def addHighlightings(self, fields, color, milliseconds=None):
        """
        Calls addHighlighting for an iterable of fields
        """
        for field in fields:
            self.addHighlighting(field, color, milliseconds)

    def addHighlighting(self, field, color, milliseconds=None):
        """
        Add field to be highlighted in a certain color, for a certain time or until removed from highlightings.
        :param field: The position of the field to be highlighted, i.e. (column, row)
        :type field: tuple of int, length 2
        :param color: The color in which the field shall be highlighted given as valid descriptive string, e.g. "green"
        :type color: str
        :param milliseconds: If specified, the highlighting will only remain for x milliseconds. Otherwise it will
        reamin until removed manually.
        :type milliseconds: int
        """
        if not len(field) == 2 and all(index in range(self.dimension) for index in field):
            raise ValueError(f"Parameter field must be tuple of 2 ints, i.e. (int, int), instead found {type(field)}.")
        if not isValidColorString(color):
            raise ValueError(f"'{color}' is not a valid color string")
        if not (isinstance(color, str)):
            raise ValueError(f"Parameter color must be str, instead found {type(color)}.")
        if milliseconds is not None:
            if not isinstance(milliseconds, int):
                raise ValueError(f"Parameter milliseconds must be int, instead found {type(milliseconds)}.")
            if milliseconds < 0:
                raise ValueError(f"Parameter milliseconds must be greater that 0 ({milliseconds}).")
        now = time.time()
        self.highlightings[field] = (color, milliseconds, now)

    def removeHighlightings(self, *colors, ignoreTemporaryHighlightings=True):
        """
        remove all highlightings of certain color(s). If no colors specified, remove all highlightings.
        :param colors: the colors as strings that are valid colors
        :type colors: str
        :param ignoreTemporaryHighlightings: if True, don't remove the highlightings that have limited time until they
        expire. Else, treat these the same way as all the others.
        :type ignoreTemporaryHighlightings: bool
        """
        if not all(isValidColorString(color) for color in colors):
            raise ValueError("Parameters colors must all be valid color strings.")
        toPop = []
        for field in self.highlightings:
            fieldColor, millis, timeSet = self.highlightings[field]
            if millis is not None and ignoreTemporaryHighlightings:
                continue
            if colors == () or fieldColor in colors:
                toPop.append(field)
        for field in toPop:
            self.highlightings.pop(field)

    def _drawBoard(self, screen):
        colors = [self.whiteFieldColor, self.blackFieldColor]
        for x in range(self.dimension):
            for y in range(self.dimension):
                p.draw.rect(screen, p.Color(colors[(x + y) % 2]),
                            p.rect.Rect(x * self.sqSize, y * self.sqSize, self.sqSize, self.sqSize))

    def _drawPieces(self, screen, board):
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
            color, milliseconds, then = self.highlightings[field]
            then *= 1000  # convert to milliseconds
            now = time.time() * 1000
            if milliseconds is not None and then + milliseconds < now:
                toPop.append(field)
                continue
            self._highlightField(field, screen, color=color)
        for field in toPop:
            self.highlightings.pop(field)

    def _highlightField(self, field, screen, color):
        col = field[0]
        row = field[1]
        coloredHighlight = self.images["hl"].copy()
        colorSurface(coloredHighlight, color)
        screen.blit(coloredHighlight, p.Rect(col * self.sqSize, row * self.sqSize, self.sqSize, self.sqSize))

    def _drawPointerImage(self, screen, pos):
        if self.pointerPiece == "--" or not self.cursorOnBoard():
            return
        pointerImg = self.images[self.pointerPiece]
        pointerImgRect = pointerImg.get_rect()
        pointerImgRect.center = pos
        screen.blit(pointerImg, pointerImgRect)

