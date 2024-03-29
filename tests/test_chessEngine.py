import unittest
from src.ChessEngine import GameState, Move


class TestChessEngine(unittest.TestCase):

    def setUp(self):
        self.gs = GameState()

    def test_enPassant(self):
        self.gs.setBoard([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "--", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])

        # assert that white is at turn
        self.assertTrue(self.gs.whiteToMove)

        # assert that black may not do a two square pawn advance
        fromSq = (5, 1)
        toSq = (5, 3)
        blackPawnTwoSqAdvance = Move(fromSq, toSq, self.gs)
        self.assertFalse(any(move == blackPawnTwoSqAdvance for move in self.gs.getValidMoves(fromSq)))

        # give turn to black and assert that black may now do a two square pawn advance
        self.gs.setWhiteToMove(False)
        self.assertTrue(any(move == blackPawnTwoSqAdvance for move in self.gs.getValidMoves(fromSq)))

        # make the move and assert that turns have switched
        self.gs.makeMove(blackPawnTwoSqAdvance)
        self.assertTrue(self.gs.whiteToMove)

        # assert that the game state has stored the correct en passant square
        enPassantSquare = (5, 2)
        self.assertEquals(enPassantSquare, self.gs.enPassantSquare)

        # assert that white may now do an en passant capture
        fromSq = (4, 3)
        toSq = (5, 2)
        whitePawnEnPassant = Move(fromSq, toSq, self.gs, enPassant=True)
        self.assertTrue(any(move == whitePawnEnPassant for move in self.gs.getValidMoves(fromSq)))

        # make the e.p. move and assert that the formation on the board is correct afterwards,
        # especially that white has captured the black pawn via e.p.
        self.gs.makeMove(whitePawnEnPassant)
        self.assertEquals(self.gs.board, [
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
        self.assertIsNone(self.gs.enPassantSquare)

        # undo the move and assert that the board is back to the previous formation
        self.gs.undoMove()
        self.assertEquals(self.gs.board, [
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
        self.assertEquals(enPassantSquare, self.gs.enPassantSquare)

        # assert that white may do the e.p. again
        self.assertTrue(any(move == whitePawnEnPassant for move in self.gs.getValidMoves(fromSq)))

        # make a different move with white and assert that the enpassant variable is cleared
        fromSq = (4, 7)
        toSq = (4, 6)
        whiteSomeDifferentMove = Move(fromSq, toSq, self.gs)
        self.assertTrue(any(move == whiteSomeDifferentMove for move in self.gs.getValidMoves(fromSq)))
        self.gs.makeMove(whiteSomeDifferentMove)
        self.assertIsNone(self.gs.enPassantSquare)

        # assert that the en passant is no longer valid
        self.assertFalse(any(move == whitePawnEnPassant for move in self.gs.getValidMoves(whitePawnEnPassant.fromSq)))

        # undo the move and assert that the en passant variable is restored
        self.gs.undoMove()
        self.assertEquals(enPassantSquare, self.gs.enPassantSquare)

        # assert that white may do the e.p. again
        self.assertTrue(self.gs.whiteToMove)
        self.assertTrue(any(move == whitePawnEnPassant for move in self.gs.getValidMoves(whitePawnEnPassant.fromSq)))

    @unittest.skip("To be implemented")
    def test_pawnPromotion(self):
        self.gs.board = [
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

    @unittest.skip("To be implemented")
    def test_getAttackingMoves(self):
        self.gs.setBoard([
            ["--", "--", "bK", "bR", "--", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "--", "--", "--", "bp", "bp"],
            ["--", "--", "--", "--", "--", "bp", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["bB", "--", "bN", "wB", "--", "--", "--", "--"],
            ["wp", "--", "wp", "--", "--", "wN", "--", "--"],
            ["--", "--", "--", "--", "--", "wp", "wp", "wp"],
            ["wR", "wQ", "--", "--", "--", "wR", "wK", "--"]
        ])
        self.assertEqual(self.gs.getAttackingMoves(currentPlayer=True, pieceType='K'), [])
        self.assertEqual(self.gs.getAttackingMoves(currentPlayer=False, pieceType='K'), [])

        moveWhiteQueenSetBlackKingCheck = Move((1, 7), (5, 3), self.gs)
        self.gs.makeMove(moveWhiteQueenSetBlackKingCheck)
        self.assertEqual(self.gs.getAttackingMoves(currentPlayer=True, pieceType='K'), [])
        self.assertEqual(self.gs.getAttackingMoves(currentPlayer=False, pieceType='K'), [])  # TODO

    def test_castling(self):
        self.gs.setBoard([
            ["bR", "--", "bB", "--", "bK", "bB", "--", "bR"],
            ["bp", "bp", "bp", "--", "--", "bp", "bp", "bp"],
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "--", "--", "wp", "wp", "wp"],
            ["wR", "--", "wB", "--", "wK", "wB", "--", "wR"]
        ])
        whiteLeftRookCastling = Move((4, 7), (2, 7), self.gs, castling=True)
        whiteRightRookCastling = Move((4, 7), (6, 7), self.gs, castling=True)
        blackLeftRookCastling = Move((4, 0), (2, 0), self.gs, castling=True)
        blackRightRookCastling = Move((4, 0), (6, 0), self.gs, castling=True)
        self.assertEqual([
            ["bR", "--", "bB", "--", "bK", "bB", "--", "bR"],
            ["bp", "bp", "bp", "--", "--", "bp", "bp", "bp"],
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "--", "--", "wp", "wp", "wp"],
            ["wR", "--", "wB", "--", "wK", "wB", "--", "wR"]
        ], self.gs.board)
        self.assertNotIn(whiteLeftRookCastling, self.gs.possibleMoves)
        self.assertNotIn(whiteRightRookCastling, self.gs.possibleMoves)
        self.assertNotIn(blackLeftRookCastling, self.gs.possibleMoves)
        self.assertNotIn(blackRightRookCastling, self.gs.possibleMoves)

        self.assertTrue(self.gs.whiteToMove)

        whiteLeftBishopMakeSpace = Move((2, 7), (3, 6), self.gs)
        self.assertIn(whiteLeftBishopMakeSpace, self.gs.validMoves)
        self.gs.makeMove(whiteLeftBishopMakeSpace)
        self.assertEqual([
            ["bR", "--", "bB", "--", "bK", "bB", "--", "bR"],
            ["bp", "bp", "bp", "--", "--", "bp", "bp", "bp"],
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "wB", "--", "wp", "wp", "wp"],
            ["wR", "--", "--", "--", "wK", "wB", "--", "wR"]
        ], self.gs.board)
        self.assertFalse(self.gs.whiteToMove)

        self.gs.setWhiteToMove(True)
        self.assertIn(whiteLeftRookCastling, self.gs.validMoves)
        self.assertNotIn(whiteRightRookCastling, self.gs.validMoves)

        self.gs.setWhiteToMove(False)
        self.assertNotIn(blackRightRookCastling, self.gs.validMoves)
        self.assertNotIn(blackLeftRookCastling, self.gs.validMoves)
        self.gs.setWhiteToMove(True)

        whiteRightBishopMakeSpace = Move((5, 7), (4, 6), self.gs)
        self.assertIn(whiteRightBishopMakeSpace, self.gs.validMoves)
        self.gs.makeMove(whiteRightBishopMakeSpace)
        self.assertEqual([
            ["bR", "--", "bB", "--", "bK", "bB", "--", "bR"],
            ["bp", "bp", "bp", "--", "--", "bp", "bp", "bp"],
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "wB", "wB", "wp", "wp", "wp"],
            ["wR", "--", "--", "--", "wK", "--", "--", "wR"]
        ], self.gs.board)
        self.assertFalse(self.gs.whiteToMove)

        self.gs.setWhiteToMove(True)
        self.assertIn(whiteLeftRookCastling, self.gs.validMoves)
        self.assertIn(whiteRightRookCastling, self.gs.validMoves)

        self.gs.setWhiteToMove(False)
        self.assertNotIn(blackRightRookCastling, self.gs.validMoves)
        self.assertNotIn(blackLeftRookCastling, self.gs.validMoves)

        blackLeftBishopMakeSpace = Move((2, 0), (3, 1), self.gs)
        self.assertIn(blackLeftBishopMakeSpace, self.gs.validMoves)
        self.gs.makeMove(blackLeftBishopMakeSpace)
        self.assertEqual(self.gs.board, [
            ["bR", "--", "--", "--", "bK", "bB", "--", "bR"],
            ["bp", "bp", "bp", "bB", "--", "bp", "bp", "bp"],
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "wB", "wB", "wp", "wp", "wp"],
            ["wR", "--", "--", "--", "wK", "--", "--", "wR"]
        ])
        self.assertTrue(self.gs.whiteToMove)

        self.gs.setWhiteToMove(True)
        self.assertIn(whiteLeftRookCastling, self.gs.validMoves)
        self.assertIn(whiteRightRookCastling, self.gs.validMoves)

        self.gs.setWhiteToMove(False)
        self.assertNotIn(blackRightRookCastling, self.gs.validMoves)
        self.assertIn(blackLeftRookCastling, self.gs.validMoves)

        blackRightBishopMakeSpace = Move((5, 0), (4, 1), self.gs)
        self.assertIn(blackRightBishopMakeSpace, self.gs.validMoves)
        self.gs.makeMove(blackRightBishopMakeSpace)
        self.assertEqual(self.gs.board, [
            ["bR", "--", "--", "--", "bK", "--", "--", "bR"],
            ["bp", "bp", "bp", "bB", "bB", "bp", "bp", "bp"],
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "wB", "wB", "wp", "wp", "wp"],
            ["wR", "--", "--", "--", "wK", "--", "--", "wR"]
        ])
        self.assertTrue(self.gs.whiteToMove)

        self.assertIn(whiteLeftRookCastling, self.gs.validMoves)
        self.assertIn(whiteRightRookCastling, self.gs.validMoves)

        self.gs.setWhiteToMove(False)
        self.assertIn(blackRightRookCastling, self.gs.validMoves)
        self.assertIn(blackLeftRookCastling, self.gs.validMoves)

        # now we put some of the fields between rook and king under attack -> castling should no longer be allowed
        self.gs.setBoard([
            ["bR", "--", "--", "--", "bK", "--", "--", "bR"],
            ["bp", "bp", "bp", "bB", "bB", "bp", "bp", "bp"],
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "bp", "wB", "wB", "wp", "wp", "wp"], # col 2: changed wp to bp
            ["wR", "--", "--", "--", "wK", "--", "--", "wR"]
        ])
        self.gs.setWhiteToMove(True)
        self.assertNotIn(whiteLeftRookCastling, self.gs.validMoves)
        self.assertIn(whiteRightRookCastling, self.gs.validMoves)

        self.gs.setWhiteToMove(False)
        self.assertIn(blackRightRookCastling, self.gs.validMoves)
        self.assertIn(blackLeftRookCastling, self.gs.validMoves)

        self.gs.setBoard([
            ["bR", "--", "--", "--", "bK", "--", "--", "bR"],
            ["bp", "bp", "bp", "bB", "bB", "bp", "bp", "bp"],
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "wB", "wB", "bp", "wp", "wp"],  # col 5: changed wp to bp
            ["wR", "--", "--", "--", "wK", "--", "--", "wR"]
        ])
        self.gs.setWhiteToMove(True)
        self.assertNotIn(whiteLeftRookCastling, self.gs.validMoves)  # wK is under attack
        self.assertNotIn(whiteRightRookCastling, self.gs.validMoves)

        self.gs.setWhiteToMove(False)
        self.assertIn(blackRightRookCastling, self.gs.validMoves)
        self.assertIn(blackLeftRookCastling, self.gs.validMoves)

        self.gs.setBoard([
            ["bR", "--", "--", "--", "bK", "--", "--", "bR"],
            ["bp", "bp", "bp", "bB", "bB", "bp", "bp", "wR"], # col 7: wp changed to wR
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "wB", "wB", "wp", "wp", "wp"],
            ["wR", "--", "--", "--", "wK", "--", "--", "wR"]
        ])
        self.gs.setWhiteToMove(True)
        self.assertIn(whiteLeftRookCastling, self.gs.validMoves)
        self.assertIn(whiteRightRookCastling, self.gs.validMoves)

        self.gs.setWhiteToMove(False)
        self.assertNotIn(blackRightRookCastling, self.gs.validMoves)
        self.assertIn(blackLeftRookCastling, self.gs.validMoves)


        self.gs.setBoard([
            ["bR", "--", "--", "--", "bK", "--", "--", "bR"],
            ["bp", "bp", "wp", "bB", "bB", "bp", "bp", "bp"], # col 2: bp changed to wp
            ["bN", "--", "--", "--", "--", "bN", "--", "--"],
            ["--", "--", "bQ", "bp", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "wN", "wp", "--", "wQ", "--", "wN"],
            ["wp", "wp", "wp", "wB", "wB", "wp", "wp", "wp"],
            ["wR", "--", "--", "--", "wK", "--", "--", "wR"]
        ])
        self.gs.setWhiteToMove(True)
        self.assertIn(whiteLeftRookCastling, self.gs.validMoves)
        self.assertIn(whiteRightRookCastling, self.gs.validMoves)

        self.gs.setWhiteToMove(False)
        self.assertIn(blackRightRookCastling, self.gs.validMoves)
        self.assertNotIn(blackLeftRookCastling, self.gs.validMoves)



if __name__ == '__main__':
    unittest.main()