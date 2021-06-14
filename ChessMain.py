"""
This file will be responsiple for user's input and displaying the board
"""

import os
import pygame as pg
import ChessEngine

Width = Height = 512
FPS = 15
Dimention = 8  # the chess board is 8x8
SQ_size = Height//Dimention
Images = {}

# Initialize a global dictionary images.


def LoadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK",
              "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    current_path = os.path.dirname(__file__)
    image_path = os.path.join(current_path, 'img')
    for piece in pieces:
        # Note: we can access an image by saying Images[type]
        Images[piece] = pg.transform.scale(pg.image.load(
            os.path.join(image_path, piece + ".png")), (SQ_size, SQ_size))

 # Main driver for our code


def main():
    pg.init()
    screen = pg.display.set_mode((Width, Height))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    GameState = ChessEngine.GameState()
    LoadImages()  # Do this once before starting loop
    running = True
    sqSelected = ()  # no square is selected, keep track of the last click of ther user
    playerClicks = []  # keep track of player clicks
    ValidMoves = GameState.GetValidMoves()
    moveMade = False  # Piece move on board
    animateMade = False  # Animate when we move or undo
    GameOver = False  # Checkmate or Stalemate

    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:  # Quit command
                running = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if not GameOver:
                    location = pg.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_size
                    row = location[1] // SQ_size
                    if sqSelected == (row, col):  # click the same square to deselect
                        sqSelected = ()
                        playerClicks = []  # clear player click
                    else:
                        sqSelected = (row, col)
                        # append 1st and 2nd clicks
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:  # time to move the piece
                        move = ChessEngine.Move(
                            playerClicks[0], playerClicks[1], GameState.board)
                        print(move.GetChessNotation())
                        for i in range(len(ValidMoves)):
                            if move == ValidMoves[i]:
                                if ValidMoves[i].IsPawnPromotion:
                                    Turn = "w" if GameState.WhiteToMove else "b"
                                    Piece = ChoosePawnPromotion(screen, Turn)
                                    GameState.MakeMove(ValidMoves[i], Piece)
                                else:
                                    GameState.MakeMove(ValidMoves[i])
                                moveMade = True
                                animateMade = True
                                sqSelected = ()
                                playerClicks = []  # clear player click
                        if not moveMade:
                            # To save the last click if we miss click
                            playerClicks = [sqSelected]
            elif e.type == pg.KEYDOWN:
                # undo the move when we press 'z'
                if e.key == pg.K_z and len(GameState.MoveLog) != 0:
                    AnimateTheMove(
                        screen, GameState.MoveLog[-1], GameState.board, clock, animateMade)
                    GameState.UndoMove()
                    moveMade = True

                elif e.key == pg.K_r:  # Reset the board when we press 'r'
                    GameState = ChessEngine.GameState()
                    ValidMoves = GameState.GetAllPossibleMoves()
                    sqSelected = ()  # no square is selected, keep track of the last click of ther user
                    playerClicks = []  # keep track of player clicks
                    moveMade = False  # Piece move on board
                    animateMade = False  # Animate when we move or undo

        if moveMade:  # to reset the valid move after we moved
            if animateMade:
                AnimateTheMove(
                    screen, GameState.MoveLog[-1], GameState.board, clock, animateMade)
            ValidMoves = GameState.GetValidMoves()
            moveMade = False
            animateMade = False

        drawGameState(screen, GameState, ValidMoves, sqSelected)

        if GameState.CheckMate:
            GameOver = True
            if GameState.WhiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif GameState.StaleMate:
            GameOver = True
            drawText(screen, "Stalemate")
        else:
            GameOver = False

        clock.tick(FPS)
        pg.display.flip()

# Choose which piece to be promo


def ChoosePawnPromotion(screen, side):
    running = True
    while running:
        s = pg.Surface((SQ_size*2+20, SQ_size*2+20))
        s.set_alpha(150)
        s.fill(pg.Color("pink"))
        screen.blit(s, (Width*3//8-10, Width*3//8-10))
        SpecialColor = (15*16+14, 5*16+10, 5)
        pg.draw.line(screen, SpecialColor, (Width*3//8-10,
                     Width//2), (Width*5//8+10, Width//2), 2)
        pg.draw.line(screen, SpecialColor, (Width*3//8-10, Width *
                     3//8-10), (Width*5//8+10, Width*3//8-10), 2)
        pg.draw.line(screen, SpecialColor, (Width*3//8-10, Width *
                     5//8+10), (Width*5//8+10, Width*5//8+10), 2)
        pg.draw.line(screen, SpecialColor, (Width//2, Width *
                     3//8-10), (Width//2, Width*5//8+10), 2)
        pg.draw.line(screen, SpecialColor, (Width*3//8-10, Width *
                     3//8-10), (Width*3//8-10, Width*5//8+10), 2)
        pg.draw.line(screen, SpecialColor, (Width*5//8+10, Width *
                     3//8-10), (Width*5//8+10, Width*5//8+10), 2)
        StartPos = (Width*3//8, Width*3//8)
        Pieces = ["Q", "R", "N", "B"]
        Pos = [(StartPos[0] + SQ_size*0 - 5, StartPos[1] + SQ_size*0 - 5), (StartPos[0] + SQ_size*0 - 5, StartPos[1] + SQ_size*1 + 5),
               (StartPos[0] + SQ_size*1 + 5, StartPos[1] + SQ_size*0 - 5), (StartPos[0] + SQ_size*1 + 5, StartPos[1] + SQ_size*1 + 5)]
        for i in range(4):
            piece = side + Pieces[i]
            screen.blit(Images[piece], Pos[i])
        pg.display.flip()
        Pos = [((StartPos[0] + SQ_size*0)//SQ_size, (StartPos[1] + SQ_size*0)//SQ_size), ((StartPos[0] + SQ_size*0)//SQ_size, (StartPos[1] + SQ_size*1)//SQ_size),
               ((StartPos[0] + SQ_size*1)//SQ_size, (StartPos[1] + SQ_size*0)//SQ_size), ((StartPos[0] + SQ_size*1)//SQ_size, (StartPos[1] + SQ_size*1)//SQ_size)]
        for e in pg.event.get():
            if e.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()
                location = (location[0]//SQ_size, location[1]//SQ_size)
                if location in Pos:
                    running = False
    return Pieces[Pos.index(location)]

# Show the end game text


def drawText(screen, text):
    font = pg.font.SysFont("Helvitca", 32, True, False)
    TextObject = font.render(text, 0, pg.Color("black"))
    TextBox = pg.Surface((Width//2+200, Height//2))
    TextBox.set_alpha(150)
    TextBox.fill(pg.Color("pink"))
    screen.blit(TextBox, (Width//4-100, Height//4))
    TextLocation = pg.Rect(0, 0, Width, Height).move(
        Width//2 - TextObject.get_width()//2, Height//2 - TextObject.get_height()//2)
    screen.blit(TextObject, TextLocation)


def drawGameState(screen, GameState, ValidMoves, sqSelected):
    drawBoard(screen)  # Draw squares on the board
    # drawWoodenBoard(screen) # Draw the wooden board on the screen
    highlightSquares(screen, GameState, ValidMoves,
                     sqSelected)  # Highlight the squares
    drawPieces(screen, GameState.board)  # Draw pieces on each square

# Highlight the square box that we want to move


def highlightSquares(screen, GameState, ValidMoves, sqSelected):
    # Highlight the king with red if got checked
    CheckBox = pg.Surface((SQ_size, SQ_size))
    # Tranparency value -> 0 == transparent , 255 = solid
    CheckBox.set_alpha(150)
    CheckBox.fill(pg.Color("red"))
    if GameState.InCheck:
        if GameState.WhiteToMove:
            screen.blit(
                CheckBox, (GameState.WhiteKingLocation[1]*SQ_size, GameState.WhiteKingLocation[0]*SQ_size))
        else:
            screen.blit(
                CheckBox, (GameState.BlackKingLocation[1]*SQ_size, GameState.BlackKingLocation[0]*SQ_size))

    if sqSelected != ():
        row, col = sqSelected
        # The selected squares is the correct turn
        if GameState.board[row][col][0] == ("w" if GameState.WhiteToMove else "b"):
            # Highlight selected square
            s = pg.Surface((SQ_size, SQ_size))
            # Tranparency value -> 0 == transparent , 255 = solid
            s.set_alpha(100)
            s.fill(pg.Color("brown"))
            screen.blit(s, (col*SQ_size, row*SQ_size))
            s.fill(pg.Color("yellow"))
            for move in ValidMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol*SQ_size, move.endRow*SQ_size))

# Draw the board. The top left square is always light.


def drawBoard(screen):
    global Colors
    current_path = os.path.dirname(__file__)
    image_path = os.path.join(current_path, 'img')
    WhiteWooden = pg.transform.scale(pg.image.load(os.path.join(
        image_path, "WhiteWooden.png")).convert_alpha(), (SQ_size, SQ_size))
    BrownWooden = pg.transform.scale(pg.image.load(os.path.join(
        image_path, "BrownWooden.png")).convert_alpha(), (SQ_size, SQ_size))
    Colors = [WhiteWooden, BrownWooden]
    for row in range(Dimention):
        for col in range(Dimention):
            color = Colors[(row+col) % 2]
            screen.blit(color, pg.Rect(
                col*SQ_size, row*SQ_size, SQ_size, SQ_size))

# Draw the wooden board.


def drawWoodenBoard(screen):
    current_path = os.path.dirname(__file__)
    image_path = os.path.join(current_path, 'img')
    Background = pg.transform.scale(pg.image.load(os.path.join(
        image_path, "board.png")).convert_alpha(), (Width, Width))
    screen.blit(Background, pg.Rect(0, 0, Width, Height))


# Draw the pieces on the board using the current GameState.board
def drawPieces(screen, board):
    for row in range(Dimention):
        for col in range(Dimention):
            piece = board[row][col]
            if piece != "--":  # it means there is a piece
                screen.blit(Images[piece], pg.Rect(
                    col*SQ_size, row*SQ_size, SQ_size, SQ_size))

# Animate the move


def AnimateTheMove(screen, move, board, clock, animateMade):
    global Colors
    Cooardinates = []  # List of the coordinates that the animation will pass through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    FramesPerSQ = 10
    FramesCount = FramesPerSQ * int((dR**2 + dC**2) ** 0.5)
    for frame in range(FramesCount + 1):
        if animateMade:
            row, col = (move.startRow + dR*frame/FramesCount,
                        move.startCol + dC*frame/FramesCount)
            color = Colors[(move.endRow + move.endCol) % 2]
            EndSquare = pg.Rect(move.endCol*SQ_size,
                                move.endRow*SQ_size, SQ_size, SQ_size)
        else:
            row, col = (move.endRow - dR*frame/FramesCount,
                        move.endCol - dC*frame/FramesCount)
            color = Colors[(move.startRow + move.startCol) % 2]
            EndSquare = pg.Rect(move.startCol*SQ_size,
                                move.startRow*SQ_size, SQ_size, SQ_size)
            color2 = Colors[(move.endRow + move.endCol) % 2]
            EndSquare2 = pg.Rect(move.endCol*SQ_size,
                                 move.endRow*SQ_size, SQ_size, SQ_size)
        drawBoard(screen)
        drawPieces(screen, board)
        screen.blit(color, EndSquare)
        if animateMade:
            if move.pieceCaptured != "--":
                screen.blit(Images[move.pieceCaptured], EndSquare)
            screen.blit(Images[move.pieceMoved], pg.Rect(
                int(col*SQ_size), int(row*SQ_size), SQ_size, SQ_size))
        else:
            screen.blit(color2, EndSquare2)
            if move.pieceCaptured != "--":
                screen.blit(Images[move.pieceCaptured], EndSquare2)
            screen.blit(Images[move.pieceMoved], pg.Rect(
                int(col*SQ_size), int(row*SQ_size), SQ_size, SQ_size))
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
