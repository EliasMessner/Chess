"""
Handle user input and display current GameState Object
"""
import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on
IMAGES = {}
HIGHLIGHTED_MOVES = []
HIGHLIGHTED_FIELDS = {}
POINTER_PIECE = "--"


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
    global POINTER_PIECE, HIGHLIGHTED_MOVES, HIGHLIGHTED_FIELDS
    p.init()
    p.display.set_caption("Chess")
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    loadImages()
    running = True
    player_clicks = []  # two  tuples: [(6, 4), (4, 4)]

    while running:
        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                (col, row) = getSquareUnderCursor()
                POINTER_PIECE = gs.board[row][col]
                if (POINTER_PIECE[0] == 'w') != gs.whiteToMove:
                    POINTER_PIECE = "--"
                player_clicks.append((col, row))
                if len(player_clicks) == 1:  # first click
                    HIGHLIGHTED_FIELDS[(col, row)] = p.Color("black")  # highlight the clicked field
                elif len(player_clicks) == 2:  # second click
                    validMoves = gs.getPossibleMoves(player_clicks[0])
                    #  iterate valid moves, if the move that the player selected is among them, execute the move
                    for move in validMoves:
                        if move.fromSq == player_clicks[0] and move.toSq == player_clicks[1]:
                            gs.makeMove(move)
                            print(move)
                            break
                    #  reset the variables
                    player_clicks = []
                    POINTER_PIECE = "--"
                    HIGHLIGHTED_FIELDS = {}
                    HIGHLIGHTED_MOVES = []

            elif e.type == p.MOUSEMOTION:
                (col, row) = getSquareUnderCursor()
                if len(player_clicks) == 0:
                    validMoves = gs.getPossibleMoves((col, row))
                    HIGHLIGHTED_MOVES = validMoves

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
    for move in HIGHLIGHTED_MOVES:
        highlightField((move.toCol, move.toRow), screen, p.Color('green'))
    for field in HIGHLIGHTED_FIELDS:
        highlightField(field, screen, color=HIGHLIGHTED_FIELDS[field])
    drawPointerImage(screen)


def drawPointerImage(screen):
    if POINTER_PIECE == "--":
        return
    pointer_img = IMAGES[POINTER_PIECE]
    pointer_img_rect = pointer_img.get_rect()
    pointer_img_rect.center = p.mouse.get_pos()
    screen.blit(pointer_img, pointer_img_rect)


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


if __name__ == "__main__":
    main()
