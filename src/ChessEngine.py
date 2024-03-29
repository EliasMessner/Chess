# Author Elias Messner, November 2020
# The terms "field" and "piece" are often used synonymously here. A square is always
# a tuple if two integers from 0 to 7 and a piece or field is always a two character string
# representation of a piece
# a possible move is any move a piece can do according to its physique, even if it puts its own King into check.
# a valid move is a possible move where the player doesn't move themselves into check
# this distinction is important, because in order to know if a move (myMove) is valid we need to know
# about the possible moves the opponent could to after we executed myMove
# these possible moves of the opponent may also result into putting the opponent into check,
# because they don't actually have to be executed in order to check us.

import copy
from collections.abc import Iterable

class GameState:
    """
    This class is responsible for storing all the information about the current state of a chess game and for
    determining the valid moves at the current state. It will also keep a move log.
    """

    def __init__(self):
        # the first char represents the color of the piece 'b' or 'w'
        # the second char represents the type of the piece 'K', 'Q', 'B', 'N', 'R' or 'p'
        # "--" represents a vacant field
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.board = [
            ['bR', '--', 'bB', '--', 'bK', 'bB', '--', 'bR'],
            ['bp', 'bp', 'bp', '--', '--', 'bp', 'bp', 'bp'],
            ['bN', '--', '--', '--', '--', 'bN', '--', '--'],
            ['--', '--', 'bQ', 'bp', 'bp', '--', '--', '--'],
            ['--', '--', '--', '--', 'wp', 'wQ', '--', '--'],
            ['--', '--', 'wN', 'wp', 'bQ', '--', '--', 'wN'],
            ['wp', 'wp', 'wp', '--', '--', 'wp', 'wp', 'wp'],
            ['wR', '--', 'wB', '--', 'wK', 'wB', '--', 'wR']
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.possibleMoves = []
        self.validMoves = []
        self.enPassantSquare = None  # here a tuple should be stored representing the square a pawn omitted so that an
        # opponent's pawn can capture this pawn via en passant by checking if this variable is set
        # it is reset to None in the very next move because en passant is only allowed immediately
        self.piecesMoved = {"wK": False,  # white king
                            "wLR": False,  # white left rook
                            "wRR": False,  # white right rook
                            "bK": False,  # and so on
                            "bLR": False,
                            "bRR": False}  # keeping track if the rooks or kings have been moved to see if
        # castling is possible
        self.updatePossibleMoves()
        self.updateValidMoves()

    def getPieceAt(self, col, row):
        return self.board[row][col]

    def setPieceAt(self, col, row, piece):
        self.board[row][col] = piece

    def calculatePossibleMoves(self, fromSq):
        """
        Determines possible moves:
        1) from a given square,
        2) for both colors,
        3) without regard to check.
        :param fromSq: given square, e.g. (4, 5)
        :type fromSq: tuple
        :return: a list of ChessEngine.Move Objects which are valid moves from the
        given square on this board
        :rtype: list
        """
        possibleMoves = []
        fromCol = fromSq[0]
        fromRow = fromSq[1]
        pieceMoved = self.getPieceAt(fromCol, fromRow)

        # Pawn
        if pieceMoved[1] == 'p':
            # check if pawn is not on the finish row
            if fromRow != (0 if pieceMoved[0] == 'w' else 7):
                # add the field in front of the pawn if it is vacant
                rowInFrontOfPawn = fromRow - 1 if pieceMoved[0] == 'w' else fromRow + 1
                pieceInFrontOfPawn = self.getPieceAt(fromCol, rowInFrontOfPawn)
                if pieceInFrontOfPawn == "--":
                    possibleMoves.append(Move(fromSq, (fromCol, rowInFrontOfPawn), self))
                # add the two fields diagonally in front of the pawn if they have an opponent's piece on it
                # or if they are vacant and an en passant is possible
                for direction in (-1, 1):
                    if fromCol + direction not in range(8):
                        continue
                    # check if they have an opponent's piece on it
                    if self.getPieceAt(fromCol + direction, rowInFrontOfPawn)[0]not in (pieceMoved[0], '-'):
                        possibleMoves.append(Move(fromSq, (fromCol + direction, rowInFrontOfPawn), self))
                    # check if an enpassant is possible
                    elif self.getPieceAt(fromCol + direction, rowInFrontOfPawn) == "--" and \
                            (fromCol + direction, rowInFrontOfPawn) == self.enPassantSquare:
                        possibleMoves.append(Move(fromSq, (fromCol + direction, rowInFrontOfPawn),
                                                  self, enPassant=True))
                # if the pawn is on the start row, add the field two steps ahead of it, if the two fields in front of
                # the pawn are vacant
                if fromRow == (6 if pieceMoved[0] == 'w' else 1):
                    rowTwoAheadOfPawn = fromRow - 2 if pieceMoved[0] == 'w' else fromRow + 2
                    pieceTwoAheadOfPawn = self.getPieceAt(fromCol, rowTwoAheadOfPawn)
                    if pieceInFrontOfPawn == pieceTwoAheadOfPawn == "--":
                        possibleMoves.append(Move(fromSq, (fromCol, rowTwoAheadOfPawn), self))

        # Rook
        elif pieceMoved[1] == 'R':
            # each field ahead of the Rook (in all four parallel directions) until there is a collision
            # in case if collision, the colliding field is valid if it is an opponent's piece.
            # we start by iterating the fields neighboring the piece except the diagonal neighbors
            for direction in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                checkSq = fromSq
                while True:
                    checkSq = (checkSq[0] + direction[0], checkSq[1] + direction[1])
                    # check if field is out of the board
                    if not (checkSq[0] in range(8) and checkSq[1] in range(8)):
                        break
                    # check if there is a piece from the same color as the Rook
                    if self.getPieceAt(checkSq[0], checkSq[1])[0] == pieceMoved[0]:
                        break
                    possibleMoves.append(Move(fromSq, (checkSq[0], checkSq[1]), self))
                    # check if collision with opponent's piece
                    if self.getPieceAt(checkSq[0], checkSq[1])[0] not in (pieceMoved[0], '-'):
                        break

        # Knight
        elif pieceMoved[1] == 'N':
            # iterate all the fields accessible for the knight
            for col_step in (-2, -1, 1, 2):
                for row_step in (-2, -1, 1, 2):
                    if abs(row_step) == abs(col_step):
                        continue  # knight can only go 2 and 1, not 2 and 2 or 1 and 1
                    row = fromRow + row_step
                    col = fromCol + col_step
                    # continue if the field is out of the board
                    if row not in range(8) or col not in range(8):
                        continue
                    # assure that there is not a piece from the same color as the knight
                    if self.getPieceAt(col, row)[0] != pieceMoved[0]:
                        possibleMoves.append(Move(fromSq, (col, row), self))

        # Bishop
        elif pieceMoved[1] == 'B':
            # each field ahead of the Bishop (in all four diagonal directions) until there is a collision
            # in case if collision, the colliding field is valid if it is an opponent's piece.
            # we start by iterating the fields neighboring the piece diagonally
            for col_step in (-1, 1):
                for row_step in (-1, 1):
                    checkSq = fromSq
                    while True:
                        checkSq = (checkSq[0] + col_step, checkSq[1] + row_step)
                        # check if field is on the board
                        if not (checkSq[0] in range(8) and checkSq[1] in range(8)):
                            break
                        # check if collision with own piece
                        if self.getPieceAt(checkSq[0], checkSq[1])[0] == pieceMoved[0]:
                            break
                        possibleMoves.append(Move(fromSq, (checkSq[0], checkSq[1]), self))
                        # check if collision with opponent's piece
                        if self.getPieceAt(checkSq[0], checkSq[1])[0] not in (pieceMoved[0], '-'):
                            break

        # Queen
        elif pieceMoved[1] == 'Q':
            # each field ahead of the Queen (in all 8 directions) until there is a collision
            # in case if collision, the colliding field is valid if it is an opponent's piece.
            for col_step in (-1, 0, 1):  # Here we are iterating the fields neighboring the piece
                for row_step in (-1, 0, 1):
                    if col_step == row_step == 0:
                        continue
                    checkSq = fromSq
                    while True:
                        checkSq = (checkSq[0] + col_step, checkSq[1] + row_step)
                        # check if field is out of the board
                        if not (checkSq[0] in range(8) and checkSq[1] in range(8)):
                            break
                        # check if there is a piece from the same color as the Rook
                        if self.getPieceAt(checkSq[0], checkSq[1])[0] == pieceMoved[0]:
                            break
                        possibleMoves.append(Move(fromSq, (checkSq[0], checkSq[1]), self))
                        # check if collision with opponent's piece
                        if self.getPieceAt(checkSq[0], checkSq[1])[0] not in (pieceMoved[0], '-'):
                            break

        # King
        elif pieceMoved[1] == 'K':
            # each field next to the King if it doesn't have a piece from the same color as the King on it
            for col_step in (-1, 0, 1):  # Here we are iterating the fields neighboring the piece
                for row_step in (-1, 0, 1):
                    if col_step == row_step == 0:
                        continue
                    checkSq = (fromSq[0] + col_step, fromSq[1] + row_step)
                    # check if field is out of the board
                    if not (checkSq[0] in range(8) and checkSq[1] in range(8)):
                        continue
                    # check if there is a piece from the same color as the King
                    if self.getPieceAt(checkSq[0], checkSq[1])[0] == pieceMoved[0]:
                        continue
                    possibleMoves.append(Move(fromSq, (checkSq[0], checkSq[1]), self))
            # check if castling is possible
            if pieceMoved[0] == 'w' and not self.piecesMoved["wK"]:  # white king and hasn't moved yet
                if not self.piecesMoved["wLR"] and self.getPieceAt(0, 7) == "wR":  # white left rook not moved yet
                    if all(self.getPieceAt(c, 7) == "--" for c in range(1, 4)):  # way between wLR and wK is free
                        if all(not self.isUnderAttack((c, 7)) for c in range(0, 5)):  # none of the fields from wLR to wK are under attack
                            possibleMoves.append(Move(fromSq, (2, 7), self, castling=True))
                if not self.piecesMoved["wRR"] and self.getPieceAt(7, 7) == "wR":  # white right rook not moved yet
                    if all(self.getPieceAt(c, 7) == "--" for c in range(5, 7)):  # way between wRR and wK is free
                        if all(not self.isUnderAttack((c, 7)) for c in range(4, 8)):  # none of the fields from wRR to wK are under attack
                            possibleMoves.append(Move(fromSq, (6, 7), self, castling=True))
            elif pieceMoved[0] == 'b' and not self.piecesMoved["bK"]:  # black king not moved yet
                if not self.piecesMoved["bLR"] and self.getPieceAt(0, 0) == "bR":  # black left rook not moved yet
                    if all(self.getPieceAt(c, 0) == "--" for c in range(1, 4)):  # way between bLR and bK is free
                        if all(not self.isUnderAttack((c, 0)) for c in range(0, 5)):  # none of the fields from bLR to bK are under attack
                            possibleMoves.append(Move(fromSq, (2, 0), self, castling=True))
                if not self.piecesMoved["bRR"] and self.getPieceAt(7, 0) == "bR":  # black right rook not moved yet
                    if all(self.getPieceAt(c, 0) == "--" for c in range(5, 7)):  # way between bRR and bK is free
                        if all(not self.isUnderAttack((c, 0)) for c in range(4, 8)):  # none of the fields from bRR to bK is under attack
                            possibleMoves.append(Move(fromSq, (6, 0), self, castling=True))

        return possibleMoves

    def updatePossibleMoves(self):
        """
        Calls calculatePossibleMoves and stores the result
        1) from all the squares,
        2) for both colors,
        3) without regard to check.
        Should only be called when a move was made in order to save performance.
        :return:
        :rtype:
        """
        possibleMoves = []
        for col in range(8):
            for row in range(8):
                possibleMoves += self.calculatePossibleMoves((col, row))
        self.possibleMoves = possibleMoves

    def calculateValidMoves(self, fromSq):
        """
        Determines from the pre calculated possible moves the valid moves
        1) from a given square,
        2) for only the current player,
        3) with regard to check. (no move is valid where a player checks themselves)
        :param fromSq:
        :type fromSq:
        :return:
        :rtype:
        """
        validMoves = []
        for move in self.possibleMoves:
            # check if the move starts at the specified square and if it is a piece of the player at turn
            allyColor = 'w' if self.whiteToMove else 'b'
            if move.fromSq == fromSq and move.pieceMoved[0] == allyColor:
                # we make and undo the move to see if it puts us in check
                boardBefore = copy.deepcopy(self.board)
                self.makeMove(move, testMove=True)
                if not self.isCheck(currentPlayer=False):
                    validMoves.append(move)
                self.undoMove(testMove=True)
                # assert self.board == boardBefore
        return validMoves

    def updateValidMoves(self):
        """
        Calls calculateValidMoves on all the squares and stores the result.
        """
        validMoves = []
        for col in range(8):
            for row in range(8):
                validMoves += self.calculateValidMoves((col, row))
        self.validMoves = validMoves

    def getValidMoves(self, fromSq):
        """
        Returns a subset of the pre calculated valid moves, so that they all start at a given square.
        Should be called instead of calculateValidMoves if no move was made since updating the valid moves.
        """
        validMoves = []
        for move in self.validMoves:
            if move.fromSq == fromSq:
                validMoves.append(move)
        return validMoves

    def makeMove(self, move, testMove=False):
        """
        Executes a move and logs it, and changes which player's turn it is.
        Keeps track the enPassantSquare variable.
        Calls updatePossibleMoves
        :param move: a Move object that should be executed
        :type : ChessEngine.Move
        :return:
        :rtype:
        """
        self.setPieceAt(move.toCol, move.toRow, move.pieceMoved)
        self.setPieceAt(move.fromCol, move.fromRow, "--")
        self.moveLog.append(move)
        if not testMove:
            self.handlePawnPromotion()
            # taking care of en passant
            self.enPassantSquare = None
            if move.pawnMadeTwoSteps():  # the move before an en passant capture
                omittedRow = (move.fromRow + move.toRow) // 2
                self.enPassantSquare = (move.fromCol, omittedRow)
            elif move.enPassant:  # the en passant capture itself
                if move.pieceMoved[0] == 'w':
                    squareCapturedByEnpassant = move.toCol, move.toRow + 1
                    self.setPieceAt(squareCapturedByEnpassant[0], squareCapturedByEnpassant[1], "--")
                else:
                    squareCapturedByEnpassant = move.toCol, move.toRow - 1
                    self.setPieceAt(squareCapturedByEnpassant[0], squareCapturedByEnpassant[1], "--")
            # taking care of castling
            self.handleCastling(move)
        self.whiteToMove = not self.whiteToMove
        # updatePossibleMoves needs to be called before updateValidMoves, but after handlePawnPromotion.
        self.updatePossibleMoves()
        if not testMove:
            self.updateValidMoves()

    def undoMove(self, testMove=False):
        """
        undoes the last move and deletes it from the log, thus allowing to undo all the moves
        """
        if len(self.moveLog) == 0:
            return
        move = self.moveLog.pop()
        self.setPieceAt(move.fromCol, move.fromRow, move.pieceMoved)
        self.setPieceAt(move.toCol, move.toRow, move.pieceCaptured)
        if not testMove:
            # taking care of en passant
            self.enPassantSquare = move.enPassantSquare
            if move.enPassant:
                if move.pieceMoved[0] == 'w':
                    pieceCapturedByEnpassant = move.toCol, move.toRow + 1
                    self.setPieceAt(pieceCapturedByEnpassant[0], pieceCapturedByEnpassant[1], "bp")
                else:
                    pieceCapturedByEnpassant = move.toCol, move.toRow - 1
                    self.setPieceAt(pieceCapturedByEnpassant[0], pieceCapturedByEnpassant[1], "wp")
            # taking care of castling
            self.handleCastling(move, undo=True)
        self.whiteToMove = not self.whiteToMove
        self.updatePossibleMoves()
        if not testMove:
            self.updateValidMoves()

    def handleFirstMoveWithRooksOrKing(self, move, undo=False):
        if move.isFirstMoveWithBlackLeftRook:
            self.piecesMoved["bLR"] = not undo
        if move.isFirstMoveWithBlackRightRook:
            self.piecesMoved["bRR"] = not undo
        if move.isFirstMoveWithBlackKing:
            self.piecesMoved["bK"] = not undo
        if move.isFirstMoveWithWhiteLeftRook:
            self.piecesMoved["wLR"] = not undo
        if move.isFirstMoveWithWhiteRightRook:
            self.piecesMoved["wRR"] = not undo
        if move.isFirstMoveWithWhiteKing:
            self.piecesMoved["wK"] = not undo

    def handleCastling(self, move, undo=False):
        self.handleFirstMoveWithRooksOrKing(move, undo=undo)
        if move.castling:
            if not undo:
                if move.toSq == (2, 7):  # wK with wLR
                    self.setPieceAt(0, 7, "--")
                    self.setPieceAt(3, 7, "wR")
                    self.piecesMoved["wLR"] = True
                elif move.toSq == (6, 7):  # wK with wRR
                    self.setPieceAt(7, 7, "--")
                    self.setPieceAt(5, 7, "wR")
                    self.piecesMoved["wRR"] = True
                elif move.toSq == (2, 0):  # bK with bLR
                    self.setPieceAt(0, 0, "--")
                    self.setPieceAt(3, 0, "bR")
                    self.piecesMoved["bLR"] = True
                elif move.toSq == (6, 0):  # bK with bRR
                    self.setPieceAt(7, 0, "--")
                    self.setPieceAt(5, 0, "bR")
                    self.piecesMoved["bRR"] = True
            else:
                if move.toSq == (2, 7):  # wK with wLR
                    self.setPieceAt(0, 7, "wR")
                    self.setPieceAt(3, 7, "--")
                    self.piecesMoved["wLR"] = False
                    self.piecesMoved["wK"] = False
                elif move.toSq == (6, 7):  # wK with wRR
                    self.setPieceAt(7, 7, "wR")
                    self.setPieceAt(5, 7, "--")
                    self.piecesMoved["wRR"] = False
                    self.piecesMoved["wK"] = False
                elif move.toSq == (2, 0):  # bK with bLR
                    self.setPieceAt(0, 0, "bR")
                    self.setPieceAt(3, 0, "--")
                    self.piecesMoved["bLR"] = False
                    self.piecesMoved["bK"] = False
                elif move.toSq == (6, 0):  # bK with bRR
                    self.setPieceAt(7, 0, "bR")
                    self.setPieceAt(5, 0, "--")
                    self.piecesMoved["bRR"] = False
                    self.piecesMoved["bK"] = False

    def handlePawnPromotion(self):
        for c in range(8):
            if self.getPieceAt(c, 0) == "wp":
                self.setPieceAt(c, 0, "wQ")
            if self.getPieceAt(c, 7) == "bp":
                self.setPieceAt(c, 7, "bQ")

    def getAttackingMoves(self, pieceType=None, currentPlayer=None, square=None):
        """
        Returns all the moves by current player (or opponent) attacking the other one's piece(s) of specified type.
        Especially useful to check if someone is in check.
        :param: piece: the piece to check for if it is under attack. If None, any piece will be considered
        :param: currentPlayer: the player which could attack. If None, any player
        :return: list of moves by current player (or opponent) attacking the other one's piece(s) of specified type.
        Empty list if not checked.
        :rtype: list
        """
        checking_moves = []
        # look at possible moves to see if we are checked
        for move in self.possibleMoves:
            if square is not None and square != move.toSq:
                continue
            # filter for the color of the piece
            allyColor, oppoColor = ('w', 'b') if self.whiteToMove else ('b', 'w')
            if currentPlayer is None or (move.pieceMoved[0] == (allyColor if currentPlayer else oppoColor)):
                # see if given piece is under attack
                if pieceType is None or move.pieceCaptured[1] == pieceType:
                    checking_moves.append(move)
        return checking_moves

    def isUnderAttack(self, square, currentPlayer=False):
        return len(self.getAttackingMoves(square=square, currentPlayer=currentPlayer)) != 0

    def isCheck(self, currentPlayer=True):
        """
        :param currentPlayer: True by default, if set to False the function will look for check
        in the other player instead
        :return: True if current player is checking the other player, else False.
        :rtype: bool
        """
        return len(self.getAttackingMoves(currentPlayer=not currentPlayer, pieceType='K')) != 0

    def isStalemate(self):
        return len(self.validMoves) == 0 and not self.isCheck()

    def isCheckmate(self):
        return len(self.validMoves) == 0 and self.isCheck()

    def printMoveLog(self):
        for move in self.moveLog:
            formation = ""
            for row in move.board:
                for field in row:
                    formation += field + " "
                formation += "\n"
            print(formation)
            print(move, "\n")

    def setBoard(self, board):
        self.board = board
        self.updatePossibleMoves()
        self.updateValidMoves()

    def setWhiteToMove(self, whiteToMove):
        self.whiteToMove = whiteToMove
        self.updatePossibleMoves()
        self.updateValidMoves()


class Move:
    """
    This Class should store all the information about a certain move. The attribute board is the state of the board
    before the move is executed.
    """

    def __init__(self, fromSq, toSq, gameState, enPassant=False, castling=False):
        self.fromSq = fromSq
        self.fromCol = fromSq[0]
        self.fromRow = fromSq[1]
        self.toSq = toSq
        self.toCol = toSq[0]
        self.toRow = toSq[1]
        self.pieceMoved = gameState.board[self.fromRow][self.fromCol]
        # copy the gameState's boad by value - represents the board before the move was made
        self.board = copy.deepcopy(gameState.board)
        self.enPassant = enPassant
        self.pieceCaptured = gameState.board[self.toRow][self.toCol]
        self.enPassantSquare = gameState.enPassantSquare  # the e.p. square before the move was made
        self.castling = castling
        self.isFirstMoveWithBlackLeftRook = self.fromSq == (0, 0) and not gameState.piecesMoved["bLR"]
        self.isFirstMoveWithBlackRightRook = self.fromSq == (7, 0) and not gameState.piecesMoved["bRR"]
        self.isFirstMoveWithBlackKing = self.fromSq == (4, 0) and not gameState.piecesMoved["bK"]
        self.isFirstMoveWithWhiteLeftRook = self.fromSq == (0, 7) and not gameState.piecesMoved["wLR"]
        self.isFirstMoveWithWhiteRightRook = self.fromSq == (7, 7) and not gameState.piecesMoved["wRR"]
        self.isFirstMoveWithWhiteKing = self.fromSq == (4, 7) and not gameState.piecesMoved["wK"]

    def __str__(self):
        """
        :return: the algebraic notation of this move
        :rtype: str
        """
        msg = ""
        # the type of the piece is not displayed if it is a pawn
        if self.pieceMoved[1] != "p":
            msg += self.pieceMoved[1]
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == 'p':
                # if a pawn captured a piece, the file from which the
                # pawn departed before capturing identifies the pawn.
                msg += indexToChessNotation(self.fromSq)[0]
            msg += 'x'  # x means a piece was captured
        msg += indexToChessNotation(self.toSq)  # destination square e.g. f3
        if self.enPassant:
            msg += " e.p."
        return msg

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.fromSq == other.fromSq and self.toSq == other.toSq
        elif isinstance(other, Iterable) and len(other) == 2:
            return self.fromSq == other[0] and self.toSq == other[1]
        return False

    def pawnMadeTwoSteps(self):
        return self.pieceMoved[1] == "p" and abs(self.fromRow - self.toRow) == 2

    # def getCapturedSquare(self):
    #     if not self.enPassant:
    #         return self.toSq
    #     else:
    #         return self.toCol, self.toRow + (1 if self.pieceMoved[0] == 'w' else - 1)


def indexToChessNotation(square):
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = range(8, 0, -1)
    return files[square[0]] + str(ranks[square[1]])
