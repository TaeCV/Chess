"""
This file is responsible for determining the possible move
"""

class GameState():
    def __init__(self):
        # the board is 8x8 contains  characters 
        # the first character refers to the color 'b' or 'w'
        # the second character refers to the type 'R' ,'N' ,'B', 'Q', 'K'
        # -- represents blank space
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],]

        self.MoveFunctions = {"p" : self.GetPawnMoves, "R" : self.GetRookMoves, "N" : self.GetKnightMoves,
                              "B" : self.GetBishopMoves, "Q" : self.GetQueenMoves, "K" : self.GetKingMoves}
        self.WhiteToMove = True
        self.MoveLog = []
        self.WhiteKingLocation = (7, 4)
        self.BlackKingLocation = (0, 4)
        self.InCheck = False
        self.pins = []
        self.checks = []
        self.CheckMate = False
        self.StaleMate = False
        self.CurrentCastlingRight = CastleSide(True, True, True, True)
        self.CastleRightsLog = []
    
    def MakeMove(self, move, PawmPromotion = ''):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.MoveLog.append(move) # log the move so we can undo the move
        # Update the king's location if moved
        if move.pieceMoved == "wK":
            self.WhiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.BlackKingLocation = (move.endRow, move.endCol)  

        # Pawn promotion
        if move.IsPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + PawmPromotion
        
        # En passant
        if move.IsEnPassant:
            self.board[move.PossibleEnPassant[0]][move.PossibleEnPassant[1]] = "--"

        # Castling - when the rook or king move
        self.UpdateCastleRight(move)
        self.CastleRightsLog.append(CastleSide(self.CurrentCastlingRight.wK, self.CurrentCastlingRight.wQ,
                                                self.CurrentCastlingRight.bK, self.CurrentCastlingRight.bQ))
        
        
        #print(move.CastleKingSide, move.CastleQueenSide)
        if move.CastleKingSide:
            if self.WhiteToMove:
                self.board[move.startRow][move.startCol + 3] = "--" # Replace Rook Position to be blank
                self.board[move.startRow][move.startCol + 1] = "wR"
            else:
                self.board[move.startRow][move.startCol + 3] = "--" # Replace Rook Position to be blank
                self.board[move.startRow][move.startCol + 1] = "bR"
        
        if move.CastleQueenSide:
            if self.WhiteToMove:
                self.board[move.startRow][move.startCol - 4] = "--" # Replace Rook Position to be blank
                self.board[move.startRow][move.startCol - 1] = "wR"
            else:
                self.board[move.startRow][move.startCol - 4] = "--" # Replace Rook Position to be blank
                self.board[move.startRow][move.startCol - 1] = "bR"
        self.WhiteToMove = not self.WhiteToMove #swap players


    def UndoMove(self):
        if len(self.MoveLog) != 0:
            move =self.MoveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.WhiteToMove = not self.WhiteToMove # swap turn back
            # Update the king's location if moved
            if move.pieceMoved == "wK":
                self.WhiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.BlackKingLocation = (move.startRow, move.startCol)
            # Returning En Passant Captured
            if move.IsEnPassant:
                self.board[move.PossibleEnPassant[0]][move.PossibleEnPassant[1]] = move.PossibleEnPassant[2]
            
            # Returning Castling Properties
            self.CastleRightsLog.pop() # get rid of the log that we undo
            if len(self.CastleRightsLog) != 0:
                TempCastle = self.CastleRightsLog[-1]
                self.CurrentCastlingRight = CastleSide(TempCastle.wK, TempCastle.wQ, TempCastle.bK, TempCastle.bQ)# set the castle right to the last move 

            # Returning Rook after we undo castle move
            if move.CastleKingSide:
                if self.WhiteToMove:
                    self.board[move.startRow][move.startCol + 3] = "wR" # Replace Rook Position to be blank
                    self.board[move.startRow][move.startCol + 1] = "--"
                else:
                    self.board[move.startRow][move.startCol + 3] = "bR" # Replace Rook Position to be blank
                    self.board[move.startRow][move.startCol + 1] = "--"
            
            if move.CastleQueenSide:
                if self.WhiteToMove:
                    self.board[move.startRow][move.startCol - 4] = "wR" # Replace Rook Position to be blank
                    self.board[move.startRow][move.startCol - 1] = "--"
                else:
                    self.board[move.startRow][move.startCol - 4] = "bR" # Replace Rook Position to be blank
                    self.board[move.startRow][move.startCol - 1] = "--"
            

    def UpdateCastleRight(self, move):
        if move.pieceMoved == "wK":
            self.CurrentCastlingRight.wK = False
            self.CurrentCastlingRight.wQ = False
        elif move.pieceMoved == "bK":
            self.CurrentCastlingRight.bK = False
            self.CurrentCastlingRight.bQ = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: # Left Rook
                    self.CurrentCastlingRight.wQ = False
                elif move.startCol == 7: # Right Rook
                    self.CurrentCastlingRight.wK = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: # Left Rook
                    self.CurrentCastlingRight.bQ = False
                elif move.startCol == 7: # Right Rook
                    self.CurrentCastlingRight.bK = False

    # All moves considering checks
    def GetValidMoves(self):
        moves = []
        self.InCheck, self.pins, self.checks = self.CheckForPinsAndChecks()
        if self.WhiteToMove:
            KingRow, KingCol = self.WhiteKingLocation
        else:
            KingRow, KingCol = self.BlackKingLocation
        if self.InCheck:
            if len(self.checks) == 1: # King needs to move or piece move to block
                moves = self.GetAllPossibleMoves()
                check = self.checks[0] # Checking information
                CheckRow = check[0]
                CheckCol = check[1]
                PieceCheck = self.board[CheckRow][CheckCol] # Which enermy cause the check
                ValidSquares = []
                if PieceCheck[1] == "N": # If the checker is knight, we should capture it
                    ValidSquares = [(CheckRow, CheckCol)]
                else:
                    for i in range (1,8):
                        ValidSquare = (KingRow + check[2]*i, KingCol + check[3]*i) # (check[2], check[3]) is the direction of checking
                        ValidSquares.append(ValidSquare)
                        if ValidSquare == (CheckRow, CheckCol): # We get all the squares until we capture that's piece
                            break
                # Get rid of the moves that don't block check or move king        
                for i in range (len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K": # If it's not a king, it should block or capture the piece
                        if not (moves[i].endRow, moves[i].endCol) in ValidSquares:
                            moves.remove(moves[i])
            else: # King needs to move himself
                self.GetKingMoves(KingRow, KingCol, moves)
        else:
            moves = self.GetAllPossibleMoves()

        # Check is it checkmate or stalemate
        if len(moves) == 0:
            if self.InCheck:
                self.CheckMate = True
            else:
                self.StaleMate = True
        else:
            self.CheckMate = False
            self.StaleMate = False

        return moves

    def CheckForPinsAndChecks(self):
        pins = [] # Squares where the allied pinned piece is and direction pinned from
        checks = [] # Squares where enermy is applying a check
        InChecks = False
        if self.WhiteToMove:
            EnermyColor = "b"
            AllyColor = "w"
            StartRow, StartCol = self.WhiteKingLocation
        else:
            EnermyColor = "w"
            AllyColor = "b"
            StartRow, StartCol = self.BlackKingLocation
        # Checking outward from king for pins and checks
        AllDirections = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, -1), (-1, 1)]
        for j in range (len(AllDirections)):
            direction = AllDirections[j]
            PossiblePin = ()
            for i in range (1,8):
                EndRow = StartRow + direction[0] *i
                EndCol = StartCol + direction[1] *i
                if 0 <= EndRow < 8 and 0 <= EndCol < 8:
                    EndPiece = self.board[EndRow][EndCol]
                    if EndPiece[0] == AllyColor and EndPiece[1] != "K":
                        if PossiblePin == (): # First ally from King Position
                            PossiblePin = (EndRow, EndCol, direction[0], direction[1])
                        else: # Second ally shouldn't be a pin
                            break
                    elif EndPiece[0] == EnermyColor:
                        TypePiece = EndPiece[1]
                        if (0 <= j <= 3 and TypePiece == "R") or\
                           (4 <= j <= 7 and TypePiece == "B") or\
                           ((i == 1 and TypePiece == "p") and ((EnermyColor == "w" and (4 <= j <= 5)) or (EnermyColor == "b" and (6 <= j <= 7)))) or\
                           (TypePiece == "Q") or (i == 1 and TypePiece == "K"):
                            if PossiblePin == (): # There is no block
                               InChecks =True
                               checks.append((EndRow, EndCol, direction[0], direction[1]))
                               break
                            else:
                                pins.append(PossiblePin)
                                break
                        else: # Enermy doesn't check
                            break
                else: # Off board
                    break

        # Checking the possible check from Knight
        KnightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2)]
        for move in KnightMoves:
            EndRow = StartRow + move[0]
            EndCol = StartCol + move[1]
            if 0 <= EndRow < 8 and 0 <= EndCol < 8:
                EndPiece = self.board[EndRow][EndCol]
                if EndPiece[0] == EnermyColor and EndPiece[1] == "N":
                    InChecks = True
                    checks.append((EndRow, EndCol, move[0], move[1]))
        return InChecks, pins, checks
    
    # All moves without considering checks
    def GetAllPossibleMoves(self):
        moves = []
        for row in range (len(self.board)):
            for col in range (len(self.board[row])):
                color = self.board[row][col][0]
                if (self.WhiteToMove and color == 'w') or (color == 'b' and not self.WhiteToMove):
                    piece = self.board[row][col][1]
                    self.MoveFunctions[piece](row, col, moves) # Call the function on each piece
        return moves

    # Get all the pawn moves for the pawn located at row, col and add these moves to the list
    def GetPawnMoves(self, row, col, moves):
        # Check pin
        PiecePinned, PinDirection = self.CheckPin(row, col)
        if self.WhiteToMove:
            EnermyColor = "b"
            EnermyPawn = "bp"
            BackRank = 0
            StartRow = 6
            MoveDirection = (-1, 0)
            CaptureLeft = (-1, -1)
            CaptureRight = (-1, 1)
        else:
            EnermyColor = "w"
            EnermyPawn = "wp"
            BackRank = 7
            StartRow = 1
            MoveDirection = (1, 0)
            CaptureLeft = (1, -1)
            CaptureRight = (1, 1)

        # Check the enermy piece on the left diagonal
        if col > 0 and self.board[row + CaptureLeft[0]][col + CaptureLeft[1]][0] == EnermyColor:
            if not PiecePinned or PinDirection == CaptureLeft:
                moves.append(Move((row, col), (row + CaptureLeft[0], col + CaptureLeft[1]), self.board))

        # Check the enermy piece in the right diagonal
        if col < len(self.board[row])-1 and self.board[row + CaptureRight[0]][col + CaptureRight[1]][0] == EnermyColor: 
            if not PiecePinned or PinDirection == CaptureRight:
                moves.append(Move((row, col), (row + CaptureRight[0], col + CaptureRight[1]), self.board))

        # Check for normal move
        if self.board[row + MoveDirection[0]][col] == "--": # Check the obstacle
            if not PiecePinned or PinDirection == MoveDirection:
                if row == StartRow and self.board[row + MoveDirection[0]*2][col] == "--": # Check the double move obstacle
                    moves.append(Move((row, col), (row + MoveDirection[0]*2, col), self.board))
                moves.append(Move((row, col), (row + MoveDirection[0], col), self.board))

        # Check En Passant move
        if len(self.MoveLog) != 0: # En passant
            PrevMove = self.MoveLog[-1] # Get the previous play
            PrevPiece = PrevMove.pieceMoved # Get the previous piece
            # Checking the possible En Passant
            if PrevPiece == EnermyPawn and abs(PrevMove.startRow-PrevMove.endRow) == 2 and abs(PrevMove.startCol-col)==1 and row == StartRow + MoveDirection[0]*3 and not PiecePinned:
                EnPassantMove = Move((row,col), (PrevMove.startRow - MoveDirection[0],PrevMove.startCol), self.board)
                EnPassantMove.IsEnPassant = True
                EnPassantMove.PossibleEnPassant = (PrevMove.endRow, PrevMove.endCol, EnermyPawn)
                moves.append(EnPassantMove)           
    
    # Get all the rook moves for the rook located at row, col and add these moves to the list
    def GetRookMoves(self, row, col, moves):
        # Checking the possible row and column
        self.AddLineMove(row, col, moves)

    # Get all the knight moves for the knight located at row, col and add these moves to the list
    def GetKnightMoves(self, row, col, moves):
        # Check pin
        PiecePinned, PinDirection = self.CheckPin(row, col)
        AllyColor = "w" if self.WhiteToMove else "b"
        MoveChoices = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2)]
        for move in MoveChoices:
            if not PiecePinned:
                EndRow = row + move[0]
                EndCol = col + move[1]
                if 0 <= EndRow < 8 and 0 <= EndCol < 8: # Check on board
                    EndPiece = self.board[EndRow][EndCol]
                    if EndPiece[0] != AllyColor: # Not a teammate
                        moves.append(Move((row, col), (EndRow, EndCol), self.board))

    # Get all the bishop moves for the bishop located at row, col and add these moves to the list
    def GetBishopMoves(self, row, col, moves):
        #Checking the possible diagonal moves
        self.AddDiagonalMove(row, col, moves)

    # Get all the queen moves for the queen located at row, col and add these moves to the list
    def GetQueenMoves(self, row, col, moves):
        # Checking the possible row and column
        self.AddLineMove(row, col, moves)
        #Checking the possible diagonal moves
        self.AddDiagonalMove(row, col, moves)

    # Get all the king moves for the king located at row, col and add these moves to the list
    def GetKingMoves(self, row, col, moves):
        AllyColor = "w" if self.WhiteToMove else "b"        
        MoveChoices = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for move in MoveChoices:
            EndRow = row + move[0]
            EndCol = col + move[1]
            if 0 <= EndRow < 8 and 0 <= EndCol < 8: # Check on board
                EndPiece = self.board[EndRow][EndCol]
                if EndPiece[0] != AllyColor: # Not a teammate
                    # Simulating the king moves
                    if self.WhiteToMove:
                        self.WhiteKingLocation = (EndRow, EndCol)
                    else:
                        self.BlackKingLocation = (EndRow, EndCol)
                    # Checking is it move to get check or not
                    Incheck, pins, checks = self.CheckForPinsAndChecks()
                    if not Incheck:
                        moves.append(Move((row, col), (EndRow, EndCol), self.board))
                    # Reset the king's postion
                    if self.WhiteToMove:
                        self.WhiteKingLocation = (row, col)
                    else:
                        self.BlackKingLocation = (row, col)
        self.GetCastleMoves(row, col, moves)

    def GetCastleMoves(self, row, col, moves):
        InCheck, pins, checks= self.CheckForPinsAndChecks()
        if InCheck: # Can't castle while we got check
            return
        if (self.WhiteToMove and self.CurrentCastlingRight.wK) or (not self.WhiteToMove and self.CurrentCastlingRight.bK):
            self.GetKingSideCastleMove(row, col, moves)
        if (self.WhiteToMove and self.CurrentCastlingRight.wQ) or (not self.WhiteToMove and self.CurrentCastlingRight.bQ):
            self.GetQueenSideCastleMove(row, col, moves)

    def GetKingSideCastleMove(self, row, col, moves):
        FailToMove = False
        for i in range (1,3):
            if self.WhiteToMove:
                self.WhiteKingLocation = (row, col + i)
            else:
                self.BlackKingLocation = (row, col + i)
            # Checking is it move to get check or not
            Incheck, pins, checks = self.CheckForPinsAndChecks()
            # Reset the king's postion
            if self.WhiteToMove:
                self.WhiteKingLocation = (row, col)
            else:
                self.BlackKingLocation = (row, col)

            if self.board[row][col+i] != "--" or Incheck:
                FailToMove = True
        if not FailToMove:
            CastleKingSide = Move((row, col), (row, col+2), self.board)
            CastleKingSide.CastleKingSide = True
            moves.append(CastleKingSide)
 
    def GetQueenSideCastleMove(self, row, col, moves):
        FailToMove = False
        for i in range (1,4):
            if self.WhiteToMove:
                self.WhiteKingLocation = (row, col - i)
            else:
                self.BlackKingLocation = (row, col - i)
            # Checking is it move to get check or not
            Incheck, pins, checks = self.CheckForPinsAndChecks()
            # Reset the king's postion
            if self.WhiteToMove:
                self.WhiteKingLocation = (row, col)
            else:
                self.BlackKingLocation = (row, col)

            if self.board[row][col-i] != "--" or (i != 3 and Incheck):
                    FailToMove = True
        if not FailToMove:
            CastleQueenSide = Move((row, col), (row, col-2), self.board)
            CastleQueenSide.CastleQueenSide = True
            moves.append(CastleQueenSide)

    # Check the possible square in one column and one row
    def AddLineMove(self, row, col, moves):
        # Check pin
        PiecePinned, PinDirection = self.CheckPin(row, col)

        EnermyColor = "b" if self.WhiteToMove else "w"
        MoveChoices = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for move in MoveChoices:
            if not PiecePinned or move == PinDirection or PinDirection == (-move[0], -move[1]):
                for i in range (1,8):
                    EndRow = row + move[0]*i
                    EndCol = col + move[1]*i
                    if 0 <= EndRow < 8 and 0 <= EndCol < 8: # Check on board
                        EndPiece = self.board[EndRow][EndCol]
                        if EndPiece == "--": # Free space
                            moves.append(Move((row, col), (EndRow, EndCol), self.board))
                        elif EndPiece[0] == EnermyColor: # Capture the enermy
                            moves.append(Move((row, col), (EndRow, EndCol), self.board))
                            break
                        else: # Teammate
                            break
                    else: # Check off board
                        break           

    # Check the possible square in diagonal
    def AddDiagonalMove(self, row, col, moves): 
        # Check pin
        PiecePinned, PinDirection = self.CheckPin(row, col)
        
        EnermyColor = "b" if self.WhiteToMove else "w"
        MoveChoices = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for move in MoveChoices:
            if not PiecePinned or move == PinDirection or PinDirection == (-move[0], -move[1]):
                for i in range (1,8):
                    EndRow = row + move[0]*i
                    EndCol = col + move[1]*i
                    if 0 <= EndRow < 8 and 0 <= EndCol < 8: # Check on board
                        EndPiece = self.board[EndRow][EndCol]
                        if EndPiece == "--": # Free space
                            moves.append(Move((row, col), (EndRow, EndCol), self.board))
                        elif EndPiece[0] == EnermyColor: # Capture the enermy
                            moves.append(Move((row, col), (EndRow, EndCol), self.board))
                            break
                        else: # Teammate
                            break
                    else: # Check off board
                        break  
    
    # Checking pinned piece
    def CheckPin(self, row, col):
        PiecePinned = False
        PinDirection = ()
        for i in range (len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                PiecePinned = True
                PinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        return PiecePinned, PinDirection

class CastleSide():
    def __init__(self, wK, wQ, bK, bQ):
        self.wK = wK
        self.wQ = wQ
        self.bK = bK
        self.bQ = bQ

class Move():
    RanksToRows ={"1" : 7, "2" : 6, "3" : 5, "4" : 4, "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    RowsToRanks = {v:k for k,v in RanksToRows.items()}
    FilesToCols ={"h" : 7, "g" : 6, "f" : 5, "e" : 4, "d" : 3, "c" : 2, "b" : 1, "a" : 0}
    ColsToFiles = {v:k for k,v in FilesToCols.items()}
    def __init__(self, start, end, board):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

        # Pawn Promotion Stuff
        self.IsPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)

        # En Passant Stuff
        self.IsEnPassant = False
        self.PossibleEnPassant = () # The coordinate for possible en passant move and the piece captured

        # Castling Stuff
        self.CastleKingSide = False
        self.CastleQueenSide = False
 
    def __eq__(self, rhs):
        if isinstance(rhs, Move):
            return self.moveID == rhs.moveID
        return False

    def GetChessNotation(self):
        # you can add to make this like real chess notation
        return self.GetFileRank(self.startRow, self.startCol) + self.GetFileRank(self.endRow, self.endCol)

    def GetFileRank(self, r, c):
        return self.ColsToFiles[c] + self.RowsToRanks[r]

    def __str__(self):
        return self.GetChessNotation()