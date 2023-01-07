from cmu_112_graphics import *
import random
def appStarted(app):
    app.rows = 21
    app.cols = 21
    app.margin = 50
    app.highScore = 0
    app.leaderboard = [0, 0, 0, 0, 0]
    app.timerDelay = 60
    app.eatableGhostImage = app.loadImage('eatableghost.png')
    app.eatableGhostImage = app.scaleImage(app.eatableGhostImage, 1/12)
    redGhost = app.loadImage('redghost.png')
    orangeGhost = app.loadImage('orangeghost.png')
    blueGhost = app.loadImage('blueghost.png')
    app.spritesRed = []
    app.spritesOrange = []
    app.spritesBlue = []
    for i in range(2):
        sprite = redGhost.crop((20+300*i, 20, 320+300*i, 300))
        sprite = app.scaleImage(sprite, 1/12)
        app.spritesRed.append(sprite)
        sprite1 = orangeGhost.crop((20+310*i, 20, 300+310*i, 300))
        sprite1 = app.scaleImage(sprite1, 1/12)
        app.spritesOrange.append(sprite1)
        sprite2 = blueGhost.crop((20+310*i, 20, 300+310*i, 300))
        sprite2 = app.scaleImage(sprite2, 1/12)
        app.spritesBlue.append(sprite2)
    pacmanRight = app.loadImage('pacman.png')
    app.spritesRight = []
    app.spritesLeft = []
    app.spritesUp = []
    app.spritesDown = []
    for i in range(3):
        sprite = pacmanRight.crop((20+290*i, 20, 290+290*i, 310))
        spriteRight = app.scaleImage(sprite, 1/12)
        spriteLeft = spriteRight.rotate(180)
        spriteUp = spriteRight.rotate(90)
        spriteDown = spriteRight.rotate(270)
        app.spritesRight.append(spriteRight)
        app.spritesLeft.append(spriteLeft)
        app.spritesDown.append(spriteDown)
        app.spritesUp.append(spriteUp)
    app.spriteCounter = 0
    app.image1 = app.loadImage('pacmantitle.png') #https://play-lh.googleusercontent.com/l09RFdmrcZ1cpMrLNPtJocygyHqtIN1XQGJEy3kIvKoWP74lQI3609RfbD6-hBpQpg
    app.image2 = app.scaleImage(app.image1, 3)
    app.image3 = app.loadImage('cherry.jpg') #https://icon2.cleanpng.com/20180320/tqq/kisspng-pac-man-cherry-post-it-note-t-shirt-sticker-pacman-cherry-png-5ab143808aeae7.457123971521566592569.jpg
    app.image3 = app.scaleImage(app.image3, 1/12)
    resetGame(app)
    #Note: All the images outside the cherry and title screen are found here:
    #http://pixelartmaker-data-78746291193.nyc3.digitaloceanspaces.com/image/43f4f2b80d92eea.png
def resetGame(app):
    grabLeaderboard(app)
    app.score = 0
    app.lives = 2
    app.startScreen = True
    app.instructionScreen = False
    app.leaderboardScreen = False
    app.placeBlocks = False
    app.placeGhosts = False
    app.gameOver = False
    app.play = False
    app.startGame = False
    resetRound(app)
def resetRound(app): #if game just starts
    app.oldPMRow = 12
    app.oldPMCol = 10
    app.pacmanRow = 12
    app.pacmanCol = 10
    app.DFSGhostRow = 10
    app.DFSGhostCol = 9
    app.chaseGhostRow = 10
    app.chaseGhostCol = 11
    app.eatGhosts = False
    createBoard(app)
    app.dir = (0,0)
    app.time = 0
    app.oldDir = (0,0)
    app.randomGhosts = [Ghost(8,11), Ghost(8,9)]
    app.path = None
    app.path1 = None
    app.eatTime = 1
    app.scoreMultiplier = 1
    app.fruitPos = None
    app.writtenScore = False
def resetLife(app): #if pacman dies mid round
    app.oldPMRow = 12
    app.oldPMCol = 10
    app.pacmanRow = 12
    app.pacmanCol = 10
    app.DFSGhostRow = 10
    app.DFSGhostCol = 9
    app.chaseGhostRow = 10
    app.chaseGhostCol = 11
    app.eatGhosts = False
    app.dir = (0,0)
    app.time = 0
    app.oldDir = (0,0)
    app.randomGhosts = [Ghost(8,11), Ghost(8,9)]
    app.path = None
    app.path1 = None
    app.eatTime = 1
    app.scoreMultiplier = 1
    app.fruitPos = None
    app.writtenScore = False

class Ghost: #randomly moving ghost class
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.color = 'blue'
        self.dir = (0,0)
    
    def redraw(self, app, canvas):
        (x0, y0, x1, y1) = getCellBounds(app, self.row, self.col)
        x = (x1+x0) // 2
        y = (y1+y0) // 2
        if app.eatGhosts:
            canvas.create_image(x, y, image=ImageTk.PhotoImage(app.eatableGhostImage))
        else:
            sprite = app.spritesBlue[app.spriteCounter % 2]
            canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))
    
    def timerFired(self, app): #find pathfinding algo
        if (app.eatGhosts and 
           (self.row, self.col) == (app.pacmanRow, app.pacmanCol)):
            app.score += (200 * app.scoreMultiplier)
            app.scoreMultiplier *= 2
            (self.row, self.col) = (8,10)
        if (not app.eatGhosts and 
           (self.row, self.col) == (app.pacmanRow, app.pacmanCol)):
            app.lives -= 1
            resetLife(app)
        app.time += 1
        if app.time % 2 == 0:
            moveGhost(self, app)
def moveGhost(self, app): #moves randomly moving ghosts
    if not app.startGame:
        return
    oldRow = self.row
    oldCol = self.col
    isLegal = False
    (drow, dcol) = self.dir
    newRow = oldRow + drow
    newCol = oldCol + dcol
    if newCol >= app.cols:
        newCol = 1
    if newCol < 0:
        newCol = app.cols - 1
    if checkMove2(app, newRow, newCol) and self.dir != (0,0):
        self.row = newRow
        self.col = newCol
    else:
        while not isLegal:
            move = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
            (drow2, dcol2) = move
            self.dir = move
            newRow2 = oldRow + drow2
            newCol2 = oldCol + dcol2
            if newCol2 >= app.cols:
                newCol2 = 0
            if newCol2 < 0:
                newCol2 = app.cols - 1
            if checkMove2(app, newRow2, newCol2):
                self.row = newRow2
                self.col = newCol2
                isLegal = True

def createBoard(app): #creates hardcoded board for top left quadrant
    app.board = [['-'] * app.cols for row in range(app.rows)]
    app.board[1][4] = 0
    app.board[2][4] = 0
    app.board[3][4] = 0
    app.board[4][4] = 0
    app.board[5][4] = 0
    app.board[6][4] = 0
    app.board[7][4] = 0
    app.board[8][4] = 0
    app.board[9][4] = 0
    app.board[10][9] = 'X'
    app.board[10][10] = 'X'
    app.board[8][9] = 0
    app.board[12][4] = 0
    app.board[13][4] = 0
    app.board[14][4] = 0
    app.board[15][4] = 0
    app.board[16][4] = 0
    app.board[18][4] = 0
    app.board[1][3] = 0
    app.board[1][2] = 0
    app.board[1][1] = 0
    app.board[2][1] = 0
    app.board[3][1] = 0
    app.board[3][2] = 0
    app.board[3][3] = 0
    app.board[3][4] = 0
    app.board[3][5] = 0
    app.board[3][6] = 0
    app.board[3][7] = 0
    app.board[3][8] = 0
    app.board[3][9] = 0
    app.board[3][10] = 0
    app.board[2][7] = 0
    app.board[1][7] = 0
    app.board[1][6] = 0
    app.board[1][4] = 0
    app.board[1][5] = 0
    app.board[4][6] = 0
    app.board[5][6] = 0
    app.board[5][7] = 0
    app.board[5][8] = 0
    app.board[6][8] = 0
    app.board[7][8] = 0
    app.board[8][9] = 0
    app.board[8][10] = 0
    app.board[8][8] = 0
    app.board[8][7] = 0
    app.board[9][7] = 0
    app.board[10][6] = 0
    app.board[10][5] = 0
    app.board[10][0] = 0
    app.board[10][1] = 0
    app.board[10][2] = 0
    app.board[10][3] = 0
    app.board[10][4] = 0
    app.board[10][7] = 0
    app.board[2][1] = 'Power'
    mirrorBoard(app)
    app.board[9][10] = 'X'
    app.board[app.pacmanRow][app.pacmanCol] = 'P'
def mirrorBoard(app): #mirrors top right quadrant to other 3 quadrants
    for row in range(len(app.board)// 2 + 1):
        for col in range(len(app.board[0]) // 2 + 1):
                app.board[row][(app.cols - col) - 1] = app.board[row][col]
                app.board[(app.rows - row) - 1][col] = app.board[row][col]
                app.board[(app.rows - row) - 1][(app.cols - col) - 1] = app.board[row][col]
def grabLeaderboard(app): #uses local file to gather highest scores
    text = readFile("leaderboard.txt")
    text = text.split(" ")
    highScore = []
    for score in text:
        if score.isdigit():
            highScore.append(int(score))
    highScore.sort()
    highScore.reverse()
    app.leaderboard = highScore[:5]

def getCellBounds(app, row, col): #grabs cell bounds from 112 animations lecture
    gridWidth = app.width - 2 * app.margin
    gridHeight = app.height - 2 * app.margin
    columnWidth = gridWidth // app.cols
    rowHeight = gridHeight // app.rows
    x0 = app.margin + col * columnWidth
    x1 = app.margin + (col+1) * columnWidth
    y0 = app.margin  + row * rowHeight
    y1 = app.margin + (row+1) * rowHeight
    return (x0, y0, x1, y1)
def inGrid(app, x, y): #checks if mouseclicks in grid from 112 animations lecture
    return ((app.margin <= x <= app.width - app.margin) and
            (app.margin <= y <= app.height - app.margin))
def getCell(app, x, y): #grabs cell from 112 animations lecture
    if not inGrid(app, x, y):
        return (-1, -1)
    gridWidth = app.width - 2 * app.margin
    gridHeight = app.height - 2* app.margin
    cellWidth = gridWidth // app.cols
    cellHeight = gridHeight // app.rows
    row = int((y - app.margin) // cellHeight)
    col = int((x - app.margin) // cellWidth)
    return (row, col)

def mousePressed(app, event):
    if app.startScreen:
        x = event.x
        y = event.y
        if (app.width//8 <= x <= 3*app.width//8 and 
           3*app.height//4 <= y <= 7*app.height//8):
           app.startScreen = False
           app.leaderboardScreen = True
        if (5*app.width//8 <= x <= 7*app.width//8 and 
           3*app.height//4 <= y <= 7*app.height//8):
           app.startScreen = False
           app.instructionScreen = True
    if app.placeBlocks:
            (row, col) = getCell(app, event.x, event.y)
            if app.board[row][col] == 0:
                app.board[row][col] = '-'
            elif app.board[row][col] == '-':
                app.board[row][col] = 0
    if app.placeGhosts:
        (newRow, newCol) = getCell(app, event.x, event.y)
        if app.board[newRow][newCol] != 0:
            return
        newGhost = Ghost(row = newRow, col = newCol)
        if Ghost(newRow, newCol) in app.randomGhosts:
            app.randomGhosts.remove(newGhost)
        else:
            app.randomGhosts.append(newGhost)
def keyPressed(app, event):
    if event.key == 'Delete':
        app.startScreen = True
        app.leaderboardScreen = False
        app.instructionScreen = False
    if event.key == 'r':
        resetGame(app)
    elif event.key == 'Up':
        app.dir = (-1, 0)
    elif event.key == 'Down':
        app.dir = (1, 0)
    elif event.key == 'Right':
        app.dir = (0, 1)
    elif event.key == 'Left':
        app.dir = (0, -1)
    elif event.key == '1':
        if app.play:
            return
        app.placeBlocks = True
        app.placeGhosts = False
    elif event.key == '2':
        if app.play:
            return
        app.placeGhosts = True
        app.placeBlocks = False
    elif app.startScreen and event.key == 'Space':
        app.startScreen = False
        app.play = not app.play
        app.startGame = True
    elif not app.startScreen and event.key == 'p':
        app.play = not app.play
        app.placeBlocks = False
        app.placeGhosts = False
    elif event.key == 'q':
        app.gameOver = True     
def timerFired(app): #regulates whether ghosts eat Pacman, vice versa, 
#moves DFS ghosts, calculates paths for DFS ghosts, drops fruit, calculates high score, moves sprites
    checkGameOver(app)
    app.time += 1
    if app.scoreMultiplier > 8:
        app.eatGhosts = False
    if app.gameOver:
        return
    if not app.play:
        return
    if app.score > app.highScore:
        app.highScore = app.score
    if app.eatGhosts:
        app.eatTime += 1
        if app.eatTime % 150 == 0:
            app.eatGhosts = False
        if (app.pacmanRow, app.pacmanCol) == (app.DFSGhostRow, app.DFSGhostCol):
            app.score += (200 * app.scoreMultiplier)
            app.scoreMultiplier *= 2
            (app.DFSGhostRow, app.DFSGhostCol) = (10, 9)
            app.path = pathDFSGhost(app)
        if (app.pacmanRow, app.pacmanCol) == (app.chaseGhostRow, app.chaseGhostCol):
            app.score += (200 * app.scoreMultiplier)
            app.scoreMultiplier *= 2
            (app.chaseGhostRow, app.chaseGhostCol) = (10, 11)
            app.path1 = pathChaseGhost(app)
    if (app.DFSGhostRow, app.DFSGhostCol) == (app.pacmanRow, app.pacmanCol):
        app.lives -= 1  
        resetLife(app)
    elif (app.chaseGhostRow, app.chaseGhostCol) == (app.pacmanRow, app.pacmanCol):
        app.lives -= 1
        resetLife(app)
    movePacman(app)
    for ghost in app.randomGhosts:
        ghost.timerFired(app)
    if app.time % 2 == 0: 
        moveDFSGhost(app)
        moveChaseGhost(app)
    if app.time == 100:
        app.path = pathDFSGhost(app)
        app.path1 = pathChaseGhost(app)
    if app.time > 100 and app.time % 50 == 0:
        app.path = pathDFSGhost(app)
        app.path1 = pathChaseGhost(app)
    if app.time % 200 == 0:
        dropFruit(app)
    if app.time % 2 == 0:
        app.spriteCounter = (1 + app.spriteCounter) % len(app.spritesRight)
            
def checkMove(app, row, col): #checks DFS ghosts moves
    if ((row < 0 or row > app.rows -1) or
       (col < 0 or col > app.cols -1)):
       return False
    elif app.board[row][col] == '-':
        return False
    return True
def checkMove2(app, row, col): #checks randomly moving ghosts moves
    if ((row < 0 or row > app.rows -1) or
       (col < 0 or col > app.cols -1)):
       return False
    elif app.board[row][col] == '-' or app.board[row][col] == 'X':
        return False
    return True
def checkPacmanMove(app, row, col): #checks legality of Pacman's moves
    if ((row < 0 or row > app.rows -1) or
       (col < 0 or col > app.cols -1)):
       return False
    elif app.board[row][col] == '-' or app.board[row][col] == 'X':
        return False
    return True

def movePacman(app): #moves Pacman to legal positions
    if not app.play:
        return
    (row, col) = app.dir
    (currRow, currCol) = (app.pacmanRow, app.pacmanCol)
    (app.oldPMRow, app.oldPMCol) = (currRow, currCol)
    (app.pacmanRow, app.pacmanCol) = (currRow + row, currCol + col)
    if app.pacmanRow >= app.rows:
        app.pacmanRow = 0
    elif app.pacmanRow < 0:
        app.pacmanRow = app.rows - 1
    elif app.pacmanCol >= app.cols:
        app.pacmanCol = 0
    elif app.pacmanCol < 0:
        app.pacmanCol = app.cols - 1
    if checkPacmanMove(app, app.pacmanRow, app.pacmanCol):
        app.oldDir = app.dir
    else:
        (app.pacmanRow, app.pacmanCol) = (currRow, currCol)
        (oldDrow, oldDcol) = app.oldDir
        if checkMove(app, currRow + oldDrow, currCol + oldDcol):
            (app.pacmanRow, app.pacmanCol) = (currRow + oldDrow, currCol + oldDcol)
    eatPellet(app)
    eatFruit(app)

def pathDFSGhost(app, path = None): #from maze-solver notes (Recursion Pt. 2)
    if path == None:
        path = []
    def solve(row, col):
        if (row, col) in path:
            return False
        path.append((row, col))
        if (row, col) == (app.pacmanRow, app.pacmanCol):
            return True
        for (drow, dcol) in [(0, 1), (-1, 0), (1, 0), (0, -1)]:
            if checkMove(app, row + drow, col + dcol):
                if solve(row + drow, col + dcol):
                    return True
        path.pop()
        return False
    if solve(app.DFSGhostRow, app.DFSGhostCol):
        return path
def moveDFSGhost(app): #moves the ghost that tracks Pacman's current position
    if not app.play:
        return
    if app.path != None:
        if len(app.path) > 2:
            (app.DFSGhostRow, app.DFSGhostCol) = app.path[1]
            app.path.pop(1)
        elif len(app.path) == 2:
            (app.DFSGhostRow, app.DFSGhostCol) = app.path[1]
        else:
            isLegal = False
            while not isLegal:
                move = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                (drow, dcol) = move
                newRow = app.DFSGhostRow + drow
                newCol = app.DFSGhostCol + dcol
                if newCol >= app.cols:
                    newCol = 0
                if newCol < 0:
                    newCol = app.cols - 1
                if checkMove(app, newRow, newCol):
                    app.DFSGhostRow = newRow
                    app.DFSGhostCol = newCol
                    isLegal = True

def pathChaseGhost(app, path = None): #from maze-solver notes (Recursion Pt. 2)
    if path == None:
        path = []
    def solve(row, col):
        if (row, col) in path:
            return False
        path.append((row, col))
        if (row, col) == (app.oldPMRow, app.oldPMCol):
            return True
        for (drow, dcol) in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            if checkMove(app, row + drow, col + dcol):
                if solve(row + drow, col + dcol):
                    return True
        path.pop()
        return False
    if solve(app.chaseGhostRow, app.chaseGhostCol):
        return path
def moveChaseGhost(app): #moves the ghost that tracks Pacman's previous position
    if not app.play:
        return
    if app.path1 != None:
        if len(app.path1) > 2:
            (app.chaseGhostRow, app.chaseGhostCol) = app.path1[1]
            app.path1.pop(1)
        else:
            isLegal = False
            while not isLegal:
                move = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                (drow, dcol) = move
                newRow = app.chaseGhostRow + drow
                newCol = app.chaseGhostCol + dcol
                if newCol >= app.cols:
                    newCol = 0
                if newCol < 0:
                    newCol = app.cols - 1
                if checkMove(app, newRow, newCol):
                    app.chaseGhostRow = newRow
                    app.chaseGhostCol = newCol
                    isLegal = True

def eatPellet(app): #checks if Pacman has eaten a pellet
    if app.board[app.pacmanRow][app.pacmanCol] == 0:
        app.board[app.pacmanRow][app.pacmanCol] = 'Empty'
        app.score += 10
    if app.board[app.pacmanRow][app.pacmanCol] == 'Power':
        app.board[app.pacmanRow][app.pacmanCol] = 'Empty'
        app.eatGhosts = True
        app.eatTime = 1
        app.scoreMultiplier = 1
    if not checkPellet(app):
        resetRound(app)
def dropFruit(app): #randomly drops fruit
    if app.fruitPos != None:
        (oldRow, oldCol) = app.fruitPos
        app.board[oldRow][oldCol] = "Empty"
    while True:
        row = random.randint(0, app.rows-1)
        col = random.randint(0, app.cols-1)
        if app.board[row][col] == 'Empty':
            app.fruitPos = (row, col)
            app.board[row][col] = 'Fruit'
            return
def eatFruit(app): #checks if Pacman has eaten fruit
    if app.board[app.pacmanRow][app.pacmanCol] == 'Fruit':
        app.board[app.pacmanRow][app.pacmanCol] = 'Empty'
        app.score += 100
def checkPellet(app): #checks if board has no pellets
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col] == 0:
                return True
    return False

def checkGameOver(app): #checks if game is over
    if app.lives < 0:
        app.gameOver = True
        app.startGame = False
        if not app.writtenScore:
            writeHighScore(app)
            app.writtenScore = True

def writeHighScore(app): #adds high scores to local file
    if not app.gameOver:
        return
    writeFile("leaderboard.txt", (str(app.score)+" "))

def readFile(path): #copied from Strings 112 lecture
    with open(path, "rt") as f:
        return f.read()
def writeFile(path, contents): #copied from Strings 112 lecture
    with open(path, "a") as f:
        f.write(contents)

def drawMap(app, canvas):
    if not app.startGame:
        return
    if app.board == None:
        return
    canvas.create_rectangle(0, 0, app.width, app.width, fill = 'black')
    for row in range(len(app.board)):
        for col in range(len(app.board[row])):
            if app.board[row][col] == '-':
                (x0, y0, x1, y1) = getCellBounds(app, row, col)
                canvas.create_rectangle(x0, y0, x1, y1, 
                                        fill = 'black', outline = 'dark blue',
                                        width = 1)
def drawPacman(app, canvas):
    if not app.startGame:
        return
    (x0, y0, x1, y1) = getCellBounds(app, app.pacmanRow, app.pacmanCol)
    x = (x1+x0) // 2
    y = (y1+y0) // 2
    if app.oldDir == (0, 1):
        sprite = app.spritesRight[-app.spriteCounter]
        canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))
    elif app.oldDir == (0, -1):
        sprite = app.spritesLeft[-app.spriteCounter]
        canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))
    elif app.oldDir == (1, 0):
        sprite = app.spritesDown[-app.spriteCounter]
        canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))
    elif app.oldDir == (-1, 0):
        sprite = app.spritesUp[-app.spriteCounter]
        canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))
    else:
        sprite = app.spritesRight[0]
        canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))
def drawGhosts(app, canvas):
    if not app.startGame:
        return
    for ghost in app.randomGhosts:
        ghost.redraw(app, canvas)
def drawDFSGhost(app, canvas):
    if not app.startGame:
        return
    (x0, y0, x1, y1) = getCellBounds(app, app.DFSGhostRow, app.DFSGhostCol)
    x = (x1+x0) // 2
    y = (y1+y0) // 2
    if app.eatGhosts:
        canvas.create_image(x, y, image=ImageTk.PhotoImage(app.eatableGhostImage))
    else:
        sprite = app.spritesRed[app.spriteCounter % 2]
        canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))
def drawChaseGhost(app, canvas):
    if not app.startGame:
        return
    (x0, y0, x1, y1) = getCellBounds(app, app.chaseGhostRow, app.chaseGhostCol)
    x = (x1+x0) // 2
    y = (y1+y0) // 2
    if app.eatGhosts:
        canvas.create_image(x, y, image=ImageTk.PhotoImage(app.eatableGhostImage))
    else:
        sprite = app.spritesOrange[app.spriteCounter % 2]
        canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))
def drawPellet(app, canvas):
    if not app.startGame:
        return
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col] == 0:
                (x0, y0, x1, y1) = getCellBounds(app, row, col)
                xMargin = (x1-x0) // 3
                yMargin = (y1-y0) // 3
                canvas.create_oval(x0+xMargin, y0+yMargin, x1-xMargin, 
                                   y1-yMargin, fill = 'light yellow', 
                                   outline = 'black')
def drawPowerPellet(app, canvas):
    if not app.startGame:
        return
    if app.time % 4 == 0:
        return
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col] == 'Power':
                (x0, y0, x1, y1) = getCellBounds(app, row, col)
                xMargin = (x1-x0) // 4
                yMargin = (y1-y0) // 4
                canvas.create_oval(x0+xMargin, y0+yMargin, x1-xMargin, 
                                   y1-yMargin, fill = 'light yellow', outline = 'black')
def drawFruit(app, canvas):
    if not app.startGame:
        return
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col] == 'Fruit':
                (x0, y0, x1, y1) = getCellBounds(app, row, col)
                x = (x1+x0) // 2
                y = (y1+y0) // 2
                canvas.create_image(x, y, image=ImageTk.PhotoImage(app.image3))
def drawScore(app, canvas):
    if not app.startGame:
        return
    if app.time % 8 != 0:
        canvas.create_text(20, 0, text = '1UP', font = 'Courier 26 bold', 
                           fill = 'white', anchor = 'nw')
    canvas.create_text(50, 20, text = f'{app.score}', 
                      font = "Courier 20 bold", anchor = 'nw',
                      fill = 'white')
    canvas.create_text(app.width // 2, 0, text = 'HIGH SCORE',
                       font = "Courier 20 bold", anchor = 'n',
                       fill = 'white')
    canvas.create_text(app.width // 2 + 20, 20, text = f'{app.highScore}',
                       font = "Courier 20 bold", anchor = 'n',
                       fill = 'white')
def drawPause(app, canvas):
    if app.startGame and not app.play:
        canvas.create_text(app.width//2, app.height//2, text = 'PAUSED',
                           font = "Courier 96 bold", fill = 'white')
def drawLives(app, canvas):
    if not app.startGame:
        return
    lives = 'ᗧ ' * app.lives
    canvas.create_text(0, app.height - app.height//50, 
        text = f'  {lives}', font = 'Courier 18 bold', 
        fill = 'white', anchor = 'sw')
def drawMode(app, canvas):
    if not app.startGame:
        return
    if app.time % 8 == 0:
        return
    if app.placeBlocks:
        canvas.create_text(app.width - app.width//50, app.height - app.height//50, 
            text = 'Creative Mode: Place/Remove Blocks', font = 'Courier 18 bold', 
            fill = 'white', anchor = 'se')
    if app.placeGhosts:
        canvas.create_text(app.width - app.width//50, app.height - app.height//50, 
            text = 'Creative Mode: Place Ghosts', font = 'Courier 18 bold', 
            fill = 'white', anchor = 'se')
def drawGameOver(app, canvas):
    if not app.gameOver:
        return
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
    radius = app.width // 8
    canvas.create_oval(app.width//2 - radius, app.height//2 - radius,
                        app.width//2 + radius, app.height//2 + radius,
                        fill = 'yellow', outline = 'black')
    canvas.create_polygon(app.width//2, app.height//2, 
                            app.width // 4, 0,
                            3* app.width//4, 0, fill = 'black')
    if app.time % 15 == 0:
        canvas.create_rectangle(0, 0, app.width, app.height//2, fill = 'black')
        canvas.create_polygon(app.width//2, app.height//2, 
                                0, app.height // 4,
                                0, 3* app.height//4, fill = 'black')
        canvas.create_polygon(app.width//2, app.height//2, 
                        app.height, app.height // 4,
                        app.height, 3* app.height//4, fill = 'black')
    else:
        canvas.create_text(app.width//2 - radius//2, app.height//2 - radius//4,
                           text = 'X', fill = 'black', font = 'Arial 76 bold')
        canvas.create_text(app.width//2 - radius//2, app.height//2 - radius//4,
                           text = 'X', fill = 'white', font = 'Arial 64 bold')
    if app.time % 8 == 0:
        return
    text = [f'Score: {app.score}', 'Press "R" to restart']
    increment = 30
    for i in range(len(text)):
        canvas.create_text(app.width // 2, 3* app.height // 4 + increment*(i-1), 
        text = text[i], font = 'Courier 32 bold', fill = 'white')
    canvas.create_text(app.width // 2, app.height // 4, 
        text = "Game Over", font = 'Courier 96 bold', fill = 'white')
def drawStartScreen(app, canvas):
    if not app.startScreen:
        return
    canvas.create_image(app.width//2, app.height//2, image=ImageTk.PhotoImage(app.image2))
    canvas.create_rectangle(app.width//8, 3*app.height//4, 
                        3*app.width//8, 7*app.height//8, fill = "blue",
                        outline = 'black')
    canvas.create_text(app.width//4, 13*app.height//16, text = "Leaderboard",
                       font = 'Courier 24 bold', fill = 'white')
    canvas.create_rectangle(5*app.width//8, 3*app.height//4, 
                        7*app.width//8, 7*app.height//8, fill = "blue",
                        outline = 'black')
    canvas.create_text(3*app.width//4, 13*app.height//16, text = "Instructions",
                       font = 'Courier 24 bold', fill = 'white')
    if app.time % 20 == 0:
        return
    canvas.create_text(app.width // 2 , app.height // 2, 
                        text = "Press 'Space' to Start", 
                        font = 'Courier 48 bold', 
                        fill = 'white')
def drawInstruction(app, canvas):
    if not app.instructionScreen:
        return
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
    canvas.create_rectangle(app.width//8, app.height//8, 
                            7*app.width//8, 7*app.height//8, fill = 'black',
                            outline = 'blue', width = 15)
    text = ['Instructions:',
            'Score as many point as possible',
            'by eating pellets and fruit.',
            'You have three lives.',
            'Avoid ghosts, but eat them if',
            'you eat a power pellet.',
            'Controls:',
            'Up, Down, Right, Left: moves Pacman',
            '1: enables obstacles to be removed',
            '2: enables more ghosts to be placed',
            'Space: starts game',
            'P: pauses game',
            'Q: ends game'
            ]
    increment = 30
    for i in range(len(text)):
        canvas.create_text(app.width//2, 3* app.height//16 + i*increment,
                           text = text[i], font = 'Courier 24 bold', 
                           fill = 'white', anchor = 'n')
    if app.time % 10 != 0:
        canvas.create_text(app.width//2, 13*app.height//16,
                            text = "Press 'Delete' to Return to Start Screen", 
                            font = 'Courier 20 bold', 
                            fill = 'white', anchor = 's')
def drawLeaderboard(app, canvas):
    if not app.leaderboardScreen:
        return
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
    increment = 3*app.height//20
    for i in range(5):
        canvas.create_text(app.width//2, app.height//16, text = 'Leaderboard', fill = 'white',
                           anchor = 'n', font = 'Courier 48 bold')
        canvas.create_rectangle(app.width//8, app.height//8+ increment*i, 
                            7*app.width//8, app.height//8+ increment*(i+1),
                            fill = 'black',
                            outline = 'blue', width = 5)
        canvas.create_line(app.width//4, app.height//8, 
                            app.width//4, 7*app.height//8, fill = 'blue',
                            width = 5)
        canvas.create_text(5*app.width//32, 3* app.height//16+ increment*i,
                           text = f' {i+1}  {app.leaderboard[i]}', fill = 'white',
                           anchor = 'nw', font = 'Courier 36 bold')
    if app.time % 10 != 0:
        canvas.create_text(app.width//2, 15*app.height//16,
                            text = "Press 'Delete' to Return to Start Screen", 
                            font = 'Courier 20 bold', 
                            fill = 'white', anchor = 's')
def redrawAll(app, canvas):
    drawStartScreen(app, canvas)
    drawInstruction(app, canvas)
    drawLeaderboard(app, canvas)
    drawMap(app, canvas)
    drawPellet(app, canvas)
    drawPowerPellet(app, canvas)
    drawPacman(app, canvas)
    drawDFSGhost(app, canvas)
    drawChaseGhost(app, canvas)
    drawGhosts(app, canvas)
    drawFruit(app, canvas)
    drawScore(app, canvas)
    drawPause(app, canvas)
    drawLives(app, canvas)
    drawMode(app, canvas)
    drawGameOver(app, canvas)

def main():
    runApp(width=750, height=750)

if __name__ == '__main__':
    main()