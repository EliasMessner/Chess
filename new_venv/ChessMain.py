"""
Handle user input and display current GameState Object
"""
from time import time

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
CONTROL_PANE_WIDTH = 200
CHECK_TEXT = "Check!"
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on
IMAGES = {}
HIGHLIGHTED_FIELDS = {}  # {(col, row): (color, milliseconds, timeSet)}
POINTER_PIECE = "--"
BACKGROUND_COLOR = "white"

#REMOVE_HIGHLIGHT_EVENT = p.USEREVENT + 1


def loadImages():
    """
    Initialize a global dict of images. Only Called once
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

    IMAGES["hl"] = p.transform.scale(p.image.load("images/highlight.png"), (SQ_SIZE, SQ_SIZE))


def main():
    """
    main driver, handle input and update graphics
    """
    global POINTER_PIECE, HIGHLIGHTED_FIELDS
    p.init()
    p.display.set_caption("Chess")
    screen = p.display.set_mode((WIDTH + CONTROL_PANE_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(BACKGROUND_COLOR))
    gs = ChessEngine.GameState()
    loadImages()
    running = True
    player_clicks = []  # two  tuples: [(6, 4), (4, 4)]

    while running:
        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                clearHighlightedFields(p.Color("green"), p.Color("black"))
                (col, row) = getSquareUnderCursor()
                POINTER_PIECE = gs.board[row][col]
                if (POINTER_PIECE[0] == 'w') != gs.whiteToMove:
                    POINTER_PIECE = "--"
                player_clicks.append((col, row))
                if len(player_clicks) == 1:  # first click
                    if not (col, row) in HIGHLIGHTED_FIELDS:
                        HIGHLIGHTED_FIELDS[(col, row)] = (p.Color("black"), None, time())  # highlight the clicked field
                elif len(player_clicks) == 2:  # second click
                    validMoves = gs.getValidMoves(player_clicks[0])
                    # iterate valid moves, if the move that the player selected is among them, execute the move
                    for move in validMoves:
                        if move.fromSq == player_clicks[0] and move.toSq == player_clicks[1]:
                            # player1 chose this move
                            gs.makeMove(move)  # switch players turns -> now player2's turn
                            p2CheckingMoves = gs.getCheckingMoves(currentPlayer=True)
                            p1CheckingMoves = gs.getCheckingMoves(currentPlayer=False)
                            if len(p2CheckingMoves) != 0:
                                # player1 put themselves into check
                                # undo move and switch back players -> now player1 turn
                                gs.undoMove()
                                # show player2's checking moves for 1 second
                                addHighlightedFields(p2CheckingMoves, color=p.Color("red"), toSquareHighlight=False, milliseconds=1000)
                                break
                            elif len(p1CheckingMoves) != 0:
                                # player1 checked player2 and player2 is at turn
                                blitCheckedLabel(True)
                                # highlight all the player2 kings that are under attack
                                addHighlightedFields(p1CheckingMoves, color=p.Color("red"), fromSquareHighlight=False)
                            else:
                                # nobody is checked
                                clearHighlightedFields()
                                blitCheckedLabel(False)
                            print(move)
                            break
                    #  reset the variables
                    player_clicks = []
                    POINTER_PIECE = "--"

            elif e.type == p.MOUSEMOTION:
                if not cursorOnBoard(screen):
                    continue
                (col, row) = getSquareUnderCursor()
                if not ((gs.board[row][col][0] == 'w') == gs.whiteToMove):
                    # do nothing if user hovers over opponent's pieces
                    continue
                if len(player_clicks) == 0:
                    validMoves = gs.getValidMoves((col, row))
                    clearHighlightedFields(p.Color("green"))
                    addHighlightedFields(validMoves, p.Color("green"), fromSquareHighlight=False)
                    continue

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()

        clock.tick(MAX_FPS)
        p.display.flip()
        drawGameState(screen, gs)


def drawGameState(screen, gs):
    """
    responsible for all the graphics in current game state
    :param gs: the gamestate to be displayed
    :type gs: ChessEngine.GameState
    :param screen: the screen to draw on
    :type screen: surface
    """
    drawBoard(screen)
    drawPieces(screen, gs.board)
    updateHighlightings(screen)
    drawPointerImage(screen)


def drawPointerImage(screen):
    if POINTER_PIECE == "--":
        return
    pointer_img = IMAGES[POINTER_PIECE]
    pointer_img_rect = pointer_img.get_rect()
    pointer_img_rect.center = p.mouse.get_pos()
    screen.blit(pointer_img, pointer_img_rect)


def updateHighlightings(screen):
    toPop = []
    for field in HIGHLIGHTED_FIELDS:
        color, milliseconds, timeSet = HIGHLIGHTED_FIELDS[field]
        now = time()
        if milliseconds is not None and timeSet*1000 + milliseconds < now*1000:
            toPop.append(field)
            continue
        highlightField(field, screen, color=color)
    for field in toPop:
        HIGHLIGHTED_FIELDS.pop(field)


def highlightField(field, screen, color):
    """
    :param field: the field to be highlighted e.g. (5, 0)
    :type field: tuple
    :param screen: the screen to highlight on
    :type screen: surface
    :param color: the color to highlight in e.g. (0, 255, 0, 255)
    :type color: Color
    """
    col = field[0]
    row = field[1]
    coloredHighlight = IMAGES["hl"].copy()
    colorSurface(coloredHighlight, color)
    screen.blit(coloredHighlight, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def addHighlightedFields(moves, color, fromSquareHighlight=True, toSquareHighlight=True, milliseconds=None):
    """
    :param moves: the moves which should be highlighted
    :type moves: list
    :param color: color to use for highlight
    :type color: Color
    :param milliseconds: amount of time the highlight should be visible. If None it is visible until removed manually
    :type milliseconds: int
    :param fromSquareHighlight: True if start square should also be highlighted, otherwise just end square is
    highlighted
    :type fromSquareHighlight: bool
    """
    for move in moves:
        now = time()
        if toSquareHighlight:
            HIGHLIGHTED_FIELDS[move.toSq] = (color, milliseconds, now)
        if fromSquareHighlight:
            HIGHLIGHTED_FIELDS[move.fromSq] = (color, milliseconds, now)


def clearHighlightedFields(*colors):
    toPop = []
    for field in HIGHLIGHTED_FIELDS:
        fieldColor, millis, timeSet = HIGHLIGHTED_FIELDS[field]
        if millis is None:
            if colors == () or fieldColor in colors:
                toPop.append(field)
    for field in toPop:
        HIGHLIGHTED_FIELDS.pop(field)


def drawBoard(screen):
    """
    draw the squares on the board
    :return:
    :rtype:
    """
    colors = ["white", "gray"]
    for x in range(DIMENSION):
        for y in range(DIMENSION):
            p.draw.rect(screen, p.Color(colors[(x+y) % 2]), p.rect.Rect(x * SQ_SIZE, y * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    """
    draw pieces on the squares of the board
    :param screen:
    :type screen:
    :param board:
    :type board:
    :return:
    :rtype:
    """
    for x in range(DIMENSION):
        for y in range(DIMENSION):
            piece = board[y][x]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(x*SQ_SIZE, y*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def colorSurface(surface, color):
    red = color[0]
    green = color[1]
    blue = color[2]
    arr = p.surfarray.pixels3d(surface)
    arr[:, :, 0] = red
    arr[:, :, 1] = green
    arr[:, :, 2] = blue


def getSquareUnderCursor():
    pos = p.mouse.get_pos()
    col = pos[0] // SQ_SIZE
    row = pos[1] // SQ_SIZE
    return col, row


def blitCheckedLabel(visible):
    font = p.font.SysFont("monospace", 20, bold=True)
    x = (WIDTH + CONTROL_PANE_WIDTH//2)
    y = 100
    h = font.size(CHECK_TEXT)[1]
    w = font.size(CHECK_TEXT)[0]
    screen = p.display.get_surface()
    x_center = x - w//2
    y_center = y - h//2
    if not visible:
        screen.fill(BACKGROUND_COLOR, p.Rect(x_center, y_center, w, h))
        return
    color = p.Color("firebrick")
    antialias = visible
    label = font.render(CHECK_TEXT, antialias, color)
    screen.blit(label, (x_center, y_center))


def cursorOnBoard(screen):
    pos = p.mouse.get_pos()
    if pos[0] in range(WIDTH) and pos[1] in range(HEIGHT):
        return True
    return False




if __name__ == "__main__":
    main()
