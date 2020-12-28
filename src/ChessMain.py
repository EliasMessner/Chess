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
from ChessClock import ChessClock
from Spinner import Spinner
from ChessGUI import ChessGUI


# ui stuff
WIDTH = HEIGHT = 512
START_CLOCK = "Start Clock"
RESUME_CLOCK = "Resume"
PAUSE_CLOCK = "Pause"
CONTROL_PANE_WIDTH = 200
CHECK_TEXT = "Check!"
CHECKMATE_TEXT = "Checkmate!"
STALEMATE_TEXT = "Stalemate!"
FONT = None
FONT_COLOR = "firebrick"
LABEL_Y_POS = 80
CHECK = CHECKMATE = STALEMATE = False
checkBoxPos = (WIDTH + CONTROL_PANE_WIDTH // 20, 400)
MAX_FPS = 40


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


def main():
    """
    main driver, handle input and update graphics
    """
    global FONT, BLIT_CHECKMATE, BLIT_CHECK, BLIT_STALEMATE, showPossibleMoves_checkBox, toddlerChess_checkBox, \
        set_minutes_spinner, start_clock_btn, saveButton, loadButton
    chessGUI = ChessGUI()
    p.init()
    FONT = p.font.SysFont("monospace", 20, bold=True)
    p.display.set_caption("Chess")
    screen = p.display.set_mode((WIDTH + CONTROL_PANE_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(chessGUI.backGroundColor))
    gs = ChessEngine.GameState()
    running = True
    playerClicks = []  # two  tuples: [(6, 4), (4, 4)]
    initializeControlWidgets()
    chessClock = ChessClock((7*60, 7*60), gs.whiteToMove)

    handleIfCheck(gs, chessGUI)

    while running:
        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not chessGUI.cursorOnBoard():
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
                        saveGame(gs, chessClock)
                    # load game clicked?
                    elif loadButton.isOver(p.mouse.get_pos()):
                        loadGame(gs, chessClock)
                else:
                    (col, row) = chessGUI.getSquareUnderCursor()
                    allyColor = 'w' if gs.whiteToMove else 'b'
                    playerClicks.append((col, row))
                    if len(playerClicks) == 1:  # first click
                        # unless it's toddler chess, break if player clicked on something other than an allied piece
                        if gs.getPieceAt(col, row)[0] != allyColor and not toddlerChess_checkBox.check:
                            playerClicks = []
                            break
                        chessGUI.pointerPiece = gs.getPieceAt(col, row)
                        # highlight the clicked field
                        chessGUI.addHighlighting((col, row), "black")
                    elif len(playerClicks) == 2:  # second click
                        chessGUI.removeHighlightings("black")
                        if playerClicks[0] != playerClicks[1]:
                            if not toddlerChess_checkBox.check:
                                moveToBeMade = validateMove(playerClicks, gs.validMoves)
                            else: # toddlerchess
                                moveToBeMade = ChessEngine.Move(playerClicks[0], playerClicks[1], gs)
                            if moveToBeMade is not None:
                                chessGUI.removeHighlightings("red")
                                makeMoveSafe(gs, moveToBeMade, chessClock, chessGUI)  # make move and switch players
                                print(moveToBeMade)
                        #  reset the variables
                        playerClicks = []
                        chessGUI.pointerPiece = "--"

            elif e.type == p.MOUSEMOTION:
                if not chessGUI.cursorOnBoard():
                    continue
                (col, row) = chessGUI.getSquareUnderCursor()
                if len(playerClicks) == 0:
                    chessGUI.removeHighlightings("green")
                    if showPossibleMoves_checkBox.check:
                        validMoves = gs.getValidMoves((col, row))
                        chessGUI.addHighlightings([move.toSq for move in validMoves], "green")
                    continue

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    chessGUI.removeHighlightings()
                    undoMoveSafe(gs, chessClock, chessGUI)
                if e.key == p.K_l:
                    gs.printMoveLog()

        clock.tick(MAX_FPS)
        p.display.flip()
        chessGUI.drawGameState(screen, gs.board, p.mouse.get_pos())
        drawControlWidgets(screen, chessClock, gs.whiteToMove)


def validateMove(playerClicks, validMoves):
    """
    Checks if chosen fields represent a move in valid moves and returns this move if yes, else returns None
    :param playerClicks: the fields chosen by two clicks
    :type playerClicks: Iterable of two tuples with each two ints i.e. [(int, int), (int, int)]
    :param validMoves: the valid moves
    :type validMoves: Iterable of ChessEngine.Move Objects
    :return: The chosen valid move or None if no such exists
    :rtype: ChessEngine.Move
    """
    moveToBeMade = None
    for move in validMoves:
        if move == playerClicks:
            moveToBeMade = move
            break
    return moveToBeMade


def makeMoveSafe(gs, move, chessClock, chessGUI):
    gs.makeMove(move)
    handleIfCheck(gs, chessGUI)
    chessClock.switchPlayer()


def undoMoveSafe(gs, chessClock, chessGUI):
    gs.undoMove()
    handleIfCheck(gs, chessGUI)
    chessClock.switchPlayer()


def drawControlWidgets(screen, chessClock, whiteToMove):
    showPossibleMoves_checkBox.draw(screen)
    set_minutes_spinner.draw(screen)
    start_clock_btn.draw(screen)
    toddlerChess_checkBox.draw(screen)
    saveButton.draw(screen)
    loadButton.draw(screen)
    displayChessClock(screen, chessClock, whiteToMove)
    blitCurrentCheckLabels()
    # drawMoveLog(screen)


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


def handleIfCheck(gs, chessGUI):
    global chess_clock_running, CHECKMATE, STALEMATE, CHECK
    CHECKMATE = CHECK = STALEMATE = False
    p1CheckingMoves = gs.getAttackingMoves(currentPlayer=False, pieceType='K')  # the moves of enemy that check current player
    if len(p1CheckingMoves) != 0:  # check or checkmate
        # highlight all the player2 kings that are under attack
        chessGUI.addHighlightings([move.toSq for move in p1CheckingMoves], "red")
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
    if CHECK:
        blitCheckLabel()
    elif CHECKMATE:
        blitCheckmateLabel()
    elif STALEMATE:
        blitStalemateLabel()


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


def saveGame(gs, chessClock):
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


def loadGame(gs, chessClock):
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
