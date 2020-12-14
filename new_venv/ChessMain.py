"""
Handle user input and display current GameState Object
"""
import time
import pygame as p
import PygameUtils as pu
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
import json
import os

import ChessEngine
from Scripts.ChessClock import ChessClock
from Spinner import Spinner

WIDTH = HEIGHT = 512
CONTROL_PANE_WIDTH = 200
CHECK_TEXT = "Check!"
CHECKMATE_TEXT = "Checkmate!"
STALEMATE_TEXT = "Stalemate!"
START_CLOCK = "Start Clock"
RESUME_CLOCK = "Resume"
PAUSE_CLOCK = "Pause"
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 40
IMAGES = {}
HIGHLIGHTED_FIELDS = {}  # {(col, row): (color, milliseconds, timeSet)}
POINTER_PIECE = "--"
BACKGROUND_COLOR = "white"
FONT = None
FONT_COLOR = "firebrick"
LABEL_Y_POS = 80
CHECK = CHECKMATE = STALEMATE = False
checkBoxPos = (WIDTH + CONTROL_PANE_WIDTH // 20, 400)


def initializeControlWidgets():
    global showPossibleMoves_checkBox, toddlerChess_checkBox, set_minutes_spinner, start_clock_btn, saveButton, loadButton
    showPossibleMoves_checkBox = pu.checkbox(color=p.Color("black"), x=checkBoxPos[0],
                                             y=checkBoxPos[1], width=15,
                                             height=15, size=11, text="Show possible moves", check=True,
                                             font="dejavusans")
    toddlerChess_checkBox = pu.checkbox(color=p.Color("black"), x=checkBoxPos[0],
                                        y=checkBoxPos[1] + 20, width=15,
                                        height=15, size=11, text="Toddler-Chess", check=False,
                                        font="dejavusans")
    set_minutes_spinner = Spinner(checkBoxPos[0], checkBoxPos[1] - 350, width=100, height=20, value=7)
    start_clock_btn = pu.button(p.Color("lightgreen"), x=checkBoxPos[0] + set_minutes_spinner.width + 5,
                                y=set_minutes_spinner.top, width=80, height=20, text=START_CLOCK, size=11,
                                font="dejavusans")
    saveButton = pu.button(p.Color("lightgray"), x=WIDTH+15, y=HEIGHT-30, width=80, height=20, text="Save", size=11,
                                font="dejavusans")
    loadButton = pu.button(p.Color("lightgray"), x=WIDTH + saveButton.width + 20, y=HEIGHT - 30, width=80, height=20, text="Load", size=11,
                           font="dejavusans")


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
    global POINTER_PIECE, HIGHLIGHTED_FIELDS, FONT, BLIT_CHECKMATE, BLIT_CHECK, BLIT_STALEMATE, \
            showPossibleMoves_checkBox, toddlerChess_checkBox, set_minutes_spinner, start_clock_btn, saveButton, \
            loadButton
    p.init()
    FONT = p.font.SysFont("monospace", 20, bold=True)
    p.display.set_caption("Chess")
    screen = p.display.set_mode((WIDTH + CONTROL_PANE_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(BACKGROUND_COLOR))
    gs = ChessEngine.GameState()
    loadImages()
    running = True
    player_clicks = []  # two  tuples: [(6, 4), (4, 4)]
    initializeControlWidgets()
    chessClock = ChessClock((7*60, 7*60), gs.whiteToMove)

    while running:
        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not cursorOnBoard(screen):
                    # check if spinner was clicked
                    if set_minutes_spinner.onClick(p.mouse.get_pos()):
                        chessClock.reset((set_minutes_spinner.value*60, set_minutes_spinner.value*60))
                        start_clock_btn.text = START_CLOCK
                    # check if start chess clock button was clicked
                    elif start_clock_btn.isOver(p.mouse.get_pos()):
                        chessClock.startStop()
                        start_clock_btn.text = PAUSE_CLOCK if chessClock.running else RESUME_CLOCK
                    # check if checkBox was clicked
                    elif showPossibleMoves_checkBox.isOver(p.mouse.get_pos()):
                        showPossibleMoves_checkBox.check = not showPossibleMoves_checkBox.check
                    elif toddlerChess_checkBox.isOver(p.mouse.get_pos()):
                        toddlerChess_checkBox.check = not toddlerChess_checkBox.check
                    # save game clicked?
                    elif saveButton.isOver(p.mouse.get_pos()):
                        onClickSaveBtn(gs, chessClock)
                    # load game clicked?
                    elif loadButton.isOver(p.mouse.get_pos()):
                        onClickLoadBtn(gs, chessClock)
                    continue
                (col, row) = getSquareUnderCursor()
                POINTER_PIECE = gs.board[row][col]
                allyColor = 'w' if gs.whiteToMove else 'b'
                if POINTER_PIECE[0] != allyColor:
                    POINTER_PIECE = "--"
                    if len(player_clicks) == 0:  # player did not click on an allied piece in the first click
                        break
                player_clicks.append((col, row))
                if len(player_clicks) == 1:  # first click
                    # highlight the clicked field
                    if not (col, row) in HIGHLIGHTED_FIELDS:
                        HIGHLIGHTED_FIELDS[(col, row)] = (p.Color("black"), None, time.time())
                elif len(player_clicks) == 2:  # second click
                    clearHighlightedFields()
                    validMoves = gs.getValidMoves(player_clicks[0])
                    moveToBeMade = None
                    if not toddlerChess_checkBox.check:
                        # validate the move:
                        for move in validMoves:
                            if move.fromSq == player_clicks[0] and move.toSq == player_clicks[1]:
                                # player chose this move
                                moveToBeMade = move
                    else:
                        moveToBeMade = ChessEngine.Move(player_clicks[0], player_clicks[1], gs)
                    if moveToBeMade is not None:
                        makeMoveAndHandleCheck(gs, moveToBeMade)  # make move and switch players
                        print(moveToBeMade)
                    #  reset the variables
                    player_clicks = []
                    POINTER_PIECE = "--"

            elif e.type == p.MOUSEMOTION:
                if not cursorOnBoard(screen):
                    continue
                (col, row) = getSquareUnderCursor()
                if len(player_clicks) == 0:
                    clearHighlightedFields(p.Color("green"))
                    validMoves = gs.getValidMoves((col, row))
                    addHighlightedMoves(validMoves, p.Color("green"), fromSquareHighlight=False)
                    continue

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    clearHighlightedFields()
                    undoMoveAndHandleCheck(gs)
                if e.key == p.K_l:
                    gs.printMoveLog()

        clock.tick(MAX_FPS)
        p.display.flip()
        drawGameState(screen, gs, chessClock)


def makeMoveAndHandleCheck(gs, move):
    gs.makeMove(move)
    handleIfCheck(gs)


def undoMoveAndHandleCheck(gs):
    gs.undoMove()
    handleIfCheck(gs)


def drawGameState(screen, gs, chessClock):
    """
    responsible for all the graphics in current game state
    :param gs: the gamestate to be displayed
    :type gs: ChessEngine.GameState
    :param screen: the screen to draw on
    :type screen: surface
    """
    screen.fill(BACKGROUND_COLOR)
    drawBoard(screen)
    drawPieces(screen, gs.board)
    updateHighlightings(screen)
    drawPointerImage(screen)
    drawControlWidgets(screen)
    displayChessClock(screen, chessClock, gs.whiteToMove)
    blitCurrentCheckLabels()
    # drawMoveLog(screen)


def updateHighlightings(screen):
    toPop = []
    for field in HIGHLIGHTED_FIELDS:
        color, milliseconds, timeSet = HIGHLIGHTED_FIELDS[field]
        if not showPossibleMoves_checkBox.check and color == p.Color("green"):
            # Green highlights are for possible moves only. Continue if possibleMoves-checkbox is off
            continue
        now = time.time()
        if milliseconds is not None and timeSet * 1000 + milliseconds < now * 1000:
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


def addHighlightedMoves(moves, color, fromSquareHighlight=True, toSquareHighlight=True, milliseconds=None):
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
        now = time.time()
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
            p.draw.rect(screen, p.Color(colors[(x + y) % 2]), p.rect.Rect(x * SQ_SIZE, y * SQ_SIZE, SQ_SIZE, SQ_SIZE))


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
                screen.blit(IMAGES[piece], p.Rect(x * SQ_SIZE, y * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPointerImage(screen):
    if POINTER_PIECE == "--":
        return
    pointer_img = IMAGES[POINTER_PIECE]
    pointer_img_rect = pointer_img.get_rect()
    pointer_img_rect.center = p.mouse.get_pos()
    screen.blit(pointer_img, pointer_img_rect)


def drawMoveLog(screen):
    # TODO
    pass


def drawControlWidgets(screen):
    showPossibleMoves_checkBox.draw(screen)
    set_minutes_spinner.draw(screen)
    start_clock_btn.draw(screen)
    toddlerChess_checkBox.draw(screen)
    saveButton.draw(screen)
    loadButton.draw(screen)


def displayChessClock(screen, chessClock, whiteToMove):
    font = p.font.SysFont("monospace", 37)
    chessClockTime = chessClock.getTime()
    clock_label_white = font.render(time.strftime("%H:%M:%S", time.gmtime(chessClockTime[0])), True, p.Color(
        "red" if chessClockTime[0] == 0 else "darkgray" if not whiteToMove and chessClockTime[
            1] != 0 or not chessClock.running else "black"))
    clock_label_black = font.render(time.strftime("%H:%M:%S", time.gmtime(chessClockTime[1])), True, p.Color(
        "red" if chessClockTime[1] == 0 else "darkgray" if whiteToMove and chessClockTime[
            0] != 0 or not chessClock.running else "black"))
    x = checkBoxPos[0]
    y = HEIGHT // 2 - clock_label_white.get_height()
    screen.blit(clock_label_white, (x, y + clock_label_white.get_height()))
    screen.blit(clock_label_black, (x, y))


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


def handleIfCheck(gs):
    global chess_clock_running, CHECKMATE, STALEMATE, CHECK
    CHECKMATE = CHECK = STALEMATE = False
    p1CheckingMoves = gs.getKingCapturingMoves(currentPlayer=False)  # the moves of enemy that check current player
    if len(p1CheckingMoves) != 0:  # check or checkmate
        # highlight all the player2 kings that are under attack
        addHighlightedMoves(p1CheckingMoves, color=p.Color("red"), fromSquareHighlight=False)
        if gs.isCheckmate():
            chess_clock_running = False
            CHECKMATE = True
            return
        else:
            CHECK = True
            return
    elif gs.isStalemate():
        chess_clock_running = False
        STALEMATE = True


def blitCurrentCheckLabels():
    if STALEMATE:
        blitStalemateLabel()
    elif CHECK:
        blitCheckLabel()
    elif CHECKMATE:
        blitCheckmateLabel()


def blitCheckLabel():
    x = (WIDTH + CONTROL_PANE_WIDTH // 2)
    y = LABEL_Y_POS
    h = FONT.size(CHECK_TEXT)[1]
    w = FONT.size(CHECK_TEXT)[0]
    screen = p.display.get_surface()
    x_center = x - w // 2
    y_center = y - h // 2
    color = p.Color(FONT_COLOR)
    label = FONT.render(CHECK_TEXT, True, color)
    screen.blit(label, (x_center, y_center))


def blitCheckmateLabel():
    x = (WIDTH + CONTROL_PANE_WIDTH // 2)
    y = LABEL_Y_POS
    h = FONT.size(CHECKMATE_TEXT)[1]
    w = FONT.size(CHECKMATE_TEXT)[0]
    screen = p.display.get_surface()
    x_center = x - w // 2
    y_center = y - h // 2
    color = p.Color(FONT_COLOR)
    label = FONT.render(CHECKMATE_TEXT, True, color)
    screen.blit(label, (x_center, y_center))


def blitStalemateLabel():
    x = (WIDTH + CONTROL_PANE_WIDTH // 2)
    y = LABEL_Y_POS
    h = FONT.size(STALEMATE_TEXT)[1]
    w = FONT.size(STALEMATE_TEXT)[0]
    screen = p.display.get_surface()
    x_center = x - w // 2
    y_center = y - h // 2
    color = p.Color(FONT_COLOR)
    label = FONT.render(STALEMATE_TEXT, True, color)
    screen.blit(label, (x_center, y_center))


def cursorOnBoard(screen):
    pos = p.mouse.get_pos()
    if pos[0] in range(WIDTH) and pos[1] in range(HEIGHT):
        return True
    return False


def onClickSaveBtn(gs, chessClock):
    Tk().withdraw()
    filepath = asksaveasfilename(initialdir=os.getcwd(), title = "Select file", initialfile="gameState.json", filetypes=[("JSON Files", "*.json")])
    if filepath is None or filepath == "":
        return
    jsonData = {
        "board": gs.board,
        "whiteToMove": gs.whiteToMove,
        "enPassantSquare": gs.enPassantSquare,
        "piecesMoved": gs.piecesMoved,
        "chessClockTime": chessClock.currentTime
    }
    with open(filepath, 'w') as file:
        json.dump(jsonData, file, sort_keys=True, indent=4)


def onClickLoadBtn(gs, chessClock):
    Tk().withdraw()
    filepath = askopenfilename(filetypes=[("JSON Files", "*.json")])
    if filepath is None:
        return
    jsonData = None
    with open(filepath, 'r') as file:
        try:
            jsonData = json.loads(file.read())
        except json.decoder.JSONDecodeError:
            messagebox.showinfo("Bad File", "Could not load game from this file. File seems empty or formatted wrong")
            return
    try:
        gs.board = jsonData["board"]
        gs.whiteToMove = jsonData["whiteToMove"]
        gs.enPassantSquare = jsonData["enPassantSquare"]
        gs.piecesMoved = jsonData["piecesMoved"]
        chessClock.reset(jsonData["chessClockTime"])
        gs.updatePossibleMoves()
        gs.updateValidMoves()
    except KeyError:
        messagebox.showinfo("Bad File", "Could not load game from this file. The file does not contain all the "
                                        "necessary information")


if __name__ == "__main__":
    main()
