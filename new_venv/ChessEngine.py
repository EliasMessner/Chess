from numpy import mean


class GameState:
    """
    This class is responsible for storing all the information about the current state of a chess game and for
    determining the valid moves at the current state. It will also keep a move log.
    """

    # The terms "field" and "piece" are often used synonymously here. A square is always
    # a tuple if two integers between 0 and 7 and a piece or field is always a two character string
    # representation of a piece

    def __init__(self):
        # board is 8x8 2d list, each element has 2 chars
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
        self.whiteToMove = True
        self.moveLog = []
        self.enPassantSquare = None  # here a tuple should be stored representing the square a pawn omitted so that an
        # opponent's pawn can capture this pawn via en passant by checking if this variable is set
        # it is reset to None in the very next move because en passant is only allowed immediately

    def getValidMoves(self, fromSq):
        """
        This function determines all valid moves from a given square on this board with regards to the current state of
        the board. If the from-square is a vacant field it returns an empty list.
        :param fromSq: given square, e.g. (4, 5)
        :type fromSq: tuple
        :return: a list of ChessEngine.Move Objects which are valid moves from the
        given square on this board
        :rtype: list
        """
        validMoves = []
        fromCol = fromSq[0]
        fromRow = fromSq[1]
        pieceMoved = self.board[fromRow][fromCol]

        # opponent's piece or vacant
        if pieceMoved[0] != ('w' if self.whiteToMove else 'b'):
            return validMoves

        # Pawn
        elif pieceMoved[1] == 'p':
            # check if pawn is not on the finish row
            if fromRow != (0 if pieceMoved[0] == 'w' else 7):
                # add the field in front of the pawn if it is vacant
                rowInFrontOfPawn = fromRow - 1 if pieceMoved[0] == 'w' else fromRow + 1
                pieceInFrontOfPawn = self.board[rowInFrontOfPawn][fromCol]
                if pieceInFrontOfPawn == "--":
                    validMoves.append(Move(fromSq, (fromCol, rowInFrontOfPawn), self.board))
                # add the two fields diagonally in front of the pawn if they have an opponent's piece on it
                # or if they are vacant and an en passant is possible
                for direction in (-1, 1):
                    if fromCol + direction not in range(8):
                        continue
                    # check if they have an opponent's piece on it
                    if self.board[rowInFrontOfPawn][fromCol + direction][0][0] not in (pieceMoved[0], '-'):
                        validMoves.append(Move(fromSq, (fromCol + direction, rowInFrontOfPawn), self.board))
                    # check if an en passant is possible
                    if self.board[rowInFrontOfPawn][fromCol + direction] == "--" and \
                            (fromCol + direction, rowInFrontOfPawn) == self.enPassantSquare:
                        validMoves.append(Move(fromSq, (fromCol + direction, rowInFrontOfPawn),
                                               self.board, enPassant=True))
                # if the pawn is on the start row, add the field two steps ahead of it, if the two fields in front of
                # the pawn are vacant
                if fromRow == (6 if pieceMoved[0] == 'w' else 1):
                    rowTwoAheadOfPawn = fromRow - 2 if pieceMoved[0] == 'w' else fromRow + 2
                    pieceTwoAheadOfPawn = self.board[rowTwoAheadOfPawn][fromCol]
                    if pieceInFrontOfPawn == pieceTwoAheadOfPawn == "--":
                        validMoves.append(Move(fromSq, (fromCol, rowTwoAheadOfPawn), self.board))

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
                    if self.board[checkSq[1]][checkSq[0]][0] == pieceMoved[0]:
                        break
                    validMoves.append(Move(fromSq, (checkSq[0], checkSq[1]), self.board))
                    # check if collision with opponent's piece
                    if self.board[checkSq[1]][checkSq[0]][0] not in (pieceMoved[0], '-'):
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
                    if self.board[row][col][0] != pieceMoved[0]:
                        validMoves.append(Move(fromSq, (col, row), self.board))

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
                        if self.board[checkSq[1]][checkSq[0]][0] == pieceMoved[0]:
                            break
                        validMoves.append(Move(fromSq, (checkSq[0], checkSq[1]), self.board))
                        # check if collision with opponent's piece
                        if self.board[checkSq[1]][checkSq[0]][0] not in (pieceMoved[0], '-'):
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
                        if self.board[checkSq[1]][checkSq[0]][0] == pieceMoved[0]:
                            break
                        validMoves.append(Move(fromSq, (checkSq[0], checkSq[1]), self.board))
                        # check if collision with opponent's piece
                        if self.board[checkSq[1]][checkSq[0]][0] not in (pieceMoved[0], '-'):
                            break

        # King
        elif pieceMoved[1] == 'K':
            # each field next to the King if it doesn't have a piece from the same color as the King on it
            # TODO: the King cannot move himself into check
            for col_step in (-1, 0, 1):  # Here we are iterating the fields neighboring the piece
                for row_step in (-1, 0, 1):
                    if col_step == row_step == 0:
                        continue
                    checkSq = (fromSq[0] + col_step, fromSq[1] + row_step)
                    # check if field is out of the board
                    if not (checkSq[0] in range(8) and checkSq[1] in range(8)):
                        continue
                    # check if there is a piece from the same color as the King
                    if self.board[checkSq[1]][checkSq[0]][0] == pieceMoved[0]:
                        continue
                    validMoves.append(Move(fromSq, (checkSq[0], checkSq[1]), self.board))

        return validMoves

    def makeMove(self, move):
        """
        Executes a move and logs it, and changes which player's turn it is.
        It also keeps track the enPassant variable.
        :param move: a Move object that should be executed
        :type : ChessEngine.Move
        :return:
        :rtype:
        """
        if move.enPassant:
            squareCapturedByEnpassant = move.toCol, move.toRow + (1 if move.pieceMoved[0] == 'w' else - 1)
            self.board[squareCapturedByEnpassant[1]][squareCapturedByEnpassant[0]] = "--"
        self.board[move.toRow][move.toCol] = move.pieceMoved
        self.board[move.fromRow][move.fromCol] = "--"
        self.whiteToMove = not self.whiteToMove
        self.enPassantSquare = None
        if move.pawnMadeTwoSteps():
            omittedRow = mean((move.fromRow, move.toRow))
            self.enPassantSquare = (move.fromCol, omittedRow)
        self.moveLog.append(move)

    def undoMove(self):
        """
        undoes the last move and deletes it from the log, thus allowing to undo all the moves
        """
        if len(self.moveLog) == 0:
            return
        move = self.moveLog.pop()
        self.board[move.fromRow][move.fromCol] = move.pieceMoved
        self.board[move.toRow][move.toCol] = move.pieceCaptured
        self.whiteToMove = not self.whiteToMove
        # taking care of en passant
        if move.enPassant:
            if move.pieceMoved[0] == 'w':
                squareCapturedByEnpassant = move.toCol, move.toRow + 1
                self.board[squareCapturedByEnpassant[1]][squareCapturedByEnpassant[0]] = "bp"
            else:
                squareCapturedByEnpassant = move.toCol, move.toRow - 1
                self.board[squareCapturedByEnpassant[1]][squareCapturedByEnpassant[0]] = "wp"


class Move:
    """
    This Class should store all the information about a certain move. The attribute board is the state of the board
    before the move is executed.
    """

    def __init__(self, fromSq, toSq, board, enPassant=False):
        self.fromSq = fromSq
        self.fromCol = fromSq[0]
        self.fromRow = fromSq[1]
        self.toSq = toSq
        self.toCol = toSq[0]
        self.toRow = toSq[1]
        self.pieceMoved = board[self.fromRow][self.fromCol]
        self.board = board
        self.enPassant = enPassant
        self.pieceCaptured = board[self.toRow][self.toCol]

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
    ranks = range(1, 9)
    return files[square[0]] + str(ranks[square[1]])
