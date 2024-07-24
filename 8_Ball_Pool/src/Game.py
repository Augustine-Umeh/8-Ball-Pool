from Database import Database
import math
from Physics import StillBall, RollingBall

FRAME_INTERVAL = 0.01

class Game:
    def __init__(self, accountID: int, shotTaker: str = None, gameID: int = None, gameName: str = None, 
                 player1Name: str = None, player2Name: str = None, play1balls: set = None, play2balls: set = None):
        self.db = Database()
        self.db.createDB()
        self.accountID = accountID
        self.ballNumbers = None

        if self.is_existing_game(gameID, accountID, shotTaker, gameName, player1Name, player2Name):
            self.setup_existing_game(gameID, accountID, shotTaker, play1balls, play2balls)
        elif self.is_new_game(gameID, shotTaker, accountID, gameName, player1Name, player2Name):
            self.setup_new_game(accountID, gameName, player1Name, player2Name)
        else:
            raise TypeError("Invalid constructor usage.")
    
    def is_existing_game(self, gameID, accountID, shotTaker, gameName, player1Name, player2Name):
        return isinstance(gameID, int) and gameID >= 0 and accountID >= 0 and shotTaker and gameName is None and player1Name is None and player2Name is None

    def setup_existing_game(self, gameID, accountID, shotTaker, play1balls, play2balls):
        self.gameID = gameID
        try:
            gameInfo = self.db.getGame(accountID, gameID)
            if gameInfo:
                self.gameName = gameInfo[0]
                self.player1Name = gameInfo[1]
                self.player2Name = gameInfo[2]
                self.player1Category = gameInfo[3]
                self.player2Category = gameInfo[4]
                self.currentPlayer = shotTaker
                self.play1balls = play1balls
                self.play2balls = play2balls
                self.winner = gameInfo[5]
                self.scratch = False
                self.first_ball_hit = None
            else:
                raise ValueError(f"No game found for accountID {accountID + 1} and gameID {gameID + 1}")
        except Exception as e:
            raise ValueError(f"Error retrieving game: {e}")

    def is_new_game(self, gameID, shotTaker, accountID, gameName, player1Name, player2Name):
        return gameID is None and shotTaker is None and accountID >= 0 and isinstance(gameName, str) and isinstance(player1Name, str) and isinstance(player2Name, str)

    def setup_new_game(self, accountID, gameName, player1Name, player2Name):
        self.gameName = gameName
        self.player1Name = player1Name
        self.player2Name = player2Name
        self.currentPlayer = None
        self.player1Category = None
        self.player2Category = None
        self.play1balls = set()
        self.play2balls = set()
        self.winner = ''
        try:
            self.gameID = self.db.createGame(accountID, gameName, player1Name, player2Name)
        except Exception as e:
            raise ValueError(f"Error setting game: {e}")
        
    def shoot(self, playerName, table, xvel, yvel):
        try:
            # Use accountID and gameID to log a new shot
            shotID = self.db.createShot(self.accountID, self.gameID, playerName)
            current_table = table.cueBall(table, xvel, yvel)
            
            while True:
                segment_end_table = current_table.segment()

                if segment_end_table is None:
                    break

                segment_duration = segment_end_table.time - current_table.time
                num_frames = math.floor((segment_duration / FRAME_INTERVAL) + 1)

                # print("number of frames: ", num_frames)
                for frame in range(1, num_frames, 2):
                    frame_time = (frame * FRAME_INTERVAL) + 0.036
                    frame_table = current_table.roll(frame_time)
                    frame_table.time = (frame_time + current_table.time)
                    
                    if self.player1Category and not self.first_ball_hit:
                        self.checkfirstball(current_table, frame_table)
                        
                    # print(self.ballNumbers)
                    # Record the current state of the table and the shot
                    tableID = self.db.writeTable(self.accountID, self.gameID, frame_table, self.ballNumbers, self.player1Category)
                    self.db.writeTableShot(self.accountID, self.gameID, tableID, shotID)

                current_table = segment_end_table

        except Exception as e:
            print(f"An error occurred during shooting: {e}")

    def setPlayerCategory(self):
        name, numbers = self.db.getPlayerAndMadeHole(self.accountID, self.gameID)
        
        if isinstance(numbers, list) and numbers and numbers[0] > 0:
            if 1 <= numbers[0] < 8:
                if name == self.player1Name:
                    self.player1Category = "solid"
                    self.player2Category = "stripe"
                else:
                    self.player1Category = "stripe"
                    self.player2Category = "solid"
            elif 8 < numbers[0] <= 15:
                if name == self.player1Name:
                    self.player1Category = "stripe"
                    self.player2Category = "solid"
                else:
                    self.player1Category = "solid"
                    self.player2Category = "stripe"
                    
            self.db.updateCategory(self.accountID, self.gameID, self.player1Category, self.player2Category)

    def playerTurn(self, isOnTable):
        if self.first_ball_hit:
            if self.first_ball_hit == "False":
                self.currentPlayer = self.player1Name if self.currentPlayer != self.player1Name else self.player2Name
                self.scratch = True
                return
            
        name, numbers = self.db.getPlayerAndMadeHole(self.accountID, self.gameID)
        
        if isinstance(numbers, list):
            for ball in numbers:
                self.play1balls.discard(ball)     
                self.play2balls.discard(ball)
                
        if not isOnTable:
            self.currentPlayer = self.player1Name if self.currentPlayer != self.player1Name else self.player2Name
            self.scratch = True
            return

        if isinstance(numbers, list):
            if not numbers:
                self.currentPlayer = self.player1Name if self.currentPlayer == self.player2Name else self.player2Name
                return
                          
            for ball in numbers:          
                if self.currentPlayer == self.player1Name:
                    if self.player1Category == 'solid' and ball > 8 or self.player1Category == 'stripe' and 1 <= ball < 8:
                        self.currentPlayer = self.player2Name
                elif self.currentPlayer == self.player2Name:
                    if self.player2Category == 'solid' and ball > 8 or self.player2Category == 'stripe' and 1 <= ball < 8:
                        self.currentPlayer = self.player1Name
            
    def setPlayerBalls(self):
        if self.player1Category == 'solid':
            self.play1balls = set([1, 2, 3, 4, 5, 6, 7])
        elif self.player2Category == 'solid':
            self.play2balls = set([1, 2, 3, 4, 5, 6, 7])
        
        if self.player1Category == 'stripe':
            self.play1balls = set([9, 10, 11, 12, 13, 14, 15])
        elif self.player2Category == 'stripe':
            self.play2balls = set([9, 10, 11, 12, 13, 14, 15])
        
    def isGameEnd(self):
        name, numbers = self.db.getPlayerAndMadeHole(self.accountID, self.gameID)
        
        if isinstance(numbers, list):
            for ball in numbers:
                if ball == 8:
                    self.db.markGameStatus(self.accountID, self.gameID, 2)
                    self.winner = 'winner'
                    if name == self.player1Name:
                        if not self.play1balls:
                            return self.player1Name, self.winner
                        else:
                            return self.player2Name, self.winner
                    elif name == self.player2Name:
                        if not self.play2balls:
                            return self.player2Name, self.winner
                        else:
                            return self.player2Name, self.winner
        elif numbers == -1:
            return name, self.winner
        
    def checkfirstball(self, prevTable, currTable):
        curr_dict = {}

        for ball in currTable:
            if isinstance(ball, RollingBall) and ball.obj.rolling_ball.number > 0:
                num = ball.obj.rolling_ball.number
                curr_dict[num] = (ball.obj.rolling_ball.pos.x, ball.obj.rolling_ball.pos.y)

        if not curr_dict:
            return
        
        for ball in prevTable:
            if isinstance(ball, RollingBall):
                num = ball.obj.rolling_ball.number
                if num in curr_dict:
                    if self.currentPlayer == self.player1Name:
                        if (num > 8 and self.player1Category == 'solid') or (num < 8 and self.player1Category == 'stripe'):
                            self.first_ball_hit = "False"
                            return
                        else:
                            self.first_ball_hit = "True"
                            return
                    elif self.currentPlayer == self.player2Name:
                        if (num > 8 and self.player2Category == 'solid') or (num < 8 and self.player2Category == 'stripe'):
                            self.first_ball_hit = "False"
                            return
                        else:
                            self.first_ball_hit = "True"
                            return   
        return

    def close(self):
        self.db.close()
