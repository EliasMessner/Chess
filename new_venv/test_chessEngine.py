import unittest
from ChessEngine import GameState, Move


class TestChessEngine(unittest.TestCase):

    def test_enPassant(self):
        gs = GameState()
        gs.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "--", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        # assert that white is at turn
        self.assertTrue(gs.whiteToMove)

        # assert that black may not do a two square pawn advance
        fromSq = (5, 1)
        toSq = (5, 3)
        blackPawnTwoSqAdvance = Move(fromSq, toSq, gs)
        self.assertFalse(any(move == blackPawnTwoSqAdvance for move in gs.getValidMoves(fromSq)))

        # give turn to black and assert that black may now do a two square pawn advance
        gs.whiteToMove = False
        gs.updateValidMoves()
        self.assertTrue(any(move == blackPawnTwoSqAdvance for move in gs.getValidMoves(fromSq)))

        # make the move and assert that turns have switched
        gs.makeMove(blackPawnTwoSqAdvance)
        self.assertTrue(gs.whiteToMove)

        # assert that the game state has stored the correct en passant square
        enPassantSquare = (5, 2)
        self.assertEquals(enPassantSquare, gs.enPassantSquare)

        # assert that white may now do an en passant capture
        fromSq = (4, 3)
        toSq = (5, 2)
        whitePawnEnPassant = Move(fromSq, toSq, gs, enPassant=True)
        self.assertTrue(any(move == whitePawnEnPassant for move in gs.getValidMoves(fromSq)))

        # make the e.p. move and assert that the formation on the board is correct afterwards,
        # especially that white has captured the black pawn via e.p.
        gs.makeMove(whitePawnEnPassant)
        self.assertEquals(gs.board, [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "--", "--", "bp", "bp"],
            ["--", "--", "--", "--", "bp", "wp", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])

        # assert that the enpassant square is cleared
        self.assertIsNone(gs.enPassantSquare)

        # undo the move and assert that the board is back to the previous formation
        gs.undoMove()
        self.assertEquals(gs.board, [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "--", "--", "bp", "bp"],
            ["--", "--", "--", "--", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "bp", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])


        # assert that the en passant variable is restored
        self.assertEquals(enPassantSquare, gs.enPassantSquare)

        # assert that white may do the e.p. again
        self.assertTrue(any(move == whitePawnEnPassant for move in gs.getValidMoves(fromSq)))

        # make a different move with white and assert that the enpassant variable is cleared
        fromSq = (4, 7)
        toSq = (4, 6)
        whiteSomeDifferentMove = Move(fromSq, toSq, gs)
        self.assertTrue(any(move == whiteSomeDifferentMove for move in gs.getValidMoves(fromSq)))
        gs.makeMove(whiteSomeDifferentMove)
        self.assertIsNone(gs.enPassantSquare)

        # assert that the en passant is no longer valid
        self.assertFalse(any(move == whitePawnEnPassant for move in gs.getValidMoves(whitePawnEnPassant.fromSq)))

        # undo the move and assert that the en passant variable is restored
        gs.undoMove()
        self.assertEquals(enPassantSquare, gs.enPassantSquare)

        # assert that white may do the e.p. again
        self.assertTrue(gs.whiteToMove)
        self.assertTrue(any(move == whitePawnEnPassant for move in gs.getValidMoves(whitePawnEnPassant.fromSq)))

    def test_pawnPromotion(self):
        gs = GameState()
        gs.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        # TODO


if __name__ == '__main__':
    unittest.main()