from Database import Database
import math

FRAME_INTERVAL = 0.01

class Game:
    def __init__(self, accountID, shotTaker=None, gameID=None, gameName=None, player1Name=None, player2Name=None):
        self.db = Database()
        self.db.createDB()
        self.accountID = accountID
        self.ballNumbers = None

        # Case 1: Existing game, retrieve details
        if isinstance(gameID, int) and gameID >= 0 and accountID >= 0 and shotTaker and gameName is None and player1Name is None and player2Name is None:
            self.gameID = gameID

            try:
                gameInfo = self.db.getGame(accountID, gameID)  # Fetch game details using accountID and gameID
                if gameInfo:
                    self.gameName = gameInfo[0]
                    self.player1Name = gameInfo[1]
                    self.player2Name = gameInfo[2]
                    self.player1Category = gameInfo[3]
                    self.player2Category = gameInfo[4]
                    self.currentPlayer = shotTaker
                else:
                    raise ValueError(f"No game found for accountID {accountID + 1} and gameID {gameID + 1}")
            except Exception as e:
                raise ValueError(f"Error retrieving game: {e}")

        # Case 2: New game, set details
        elif gameID is None and shotTaker is None and accountID >= 0 and isinstance(gameName, str) and isinstance(player1Name, str) and isinstance(player2Name, str):
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name
            self.currentPlayer = None
            self.player1Category = None
            self.player2Category = None

            try:
                self.gameID = self.db.createGame(accountID, gameName, player1Name, player2Name)  # Create new game with accountID
            except Exception as e:
                raise ValueError(f"Error setting game: {e}")

        else:
            raise TypeError("Invalid constructor usage.")
        
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
            if 1 <= numbers[0] <= 8:
                if name == self.player1Name:
                    self.player1Category = "solid"
                    self.player2Category = "stripe"
                else:
                    self.player1Category = "stripe"
                    self.player2Category = "solid"
            elif 9 <= numbers[0] <= 15:
                if name == self.player1Name:
                    self.player1Category = "stripe"
                    self.player2Category = "solid"
                else:
                    self.player1Category = "solid"
                    self.player2Category = "stripe"
                
        self.db.updateCategory(self.accountID, self.gameID, self.player1Category, self.player2Category)
        # madeBall = self.db.checkIfBallPocketed(self.accountID, self.gameID, shotID)
        # if madeBall:
        #     if self.player1Category is None and self.player2Category is None:
        #         # Assign categories
        #         if 1 <= madeBall <= 7:
        #             self.player1Category = "solid" if playerName == self.player1Name else "stripe"
        #             self.player2Category = "stripe" if playerName == self.player1Name else "solid"
        #         elif 9 <= madeBall <= 15:
        #             self.player1Category = "stripe" if playerName == self.player1Name else "solid"
        #             self.player2Category = "solid" if playerName == self.player1Name else "stripe"
        #     # Determine if player continues or switches
        #     self.currentPlayer = playerName
        # else:
        #     # Switch player
        #     self.currentPlayer = self.player2Name if playerName == self.player1Name else self.player1Name
    
    def playerTurn(self, isOnTable):
        if not isOnTable:
            self.currentPlayer = self.player1Name if self.currentPlayer != self.player1Name else self.player2Name
            return
        
        name, numbers = self.db.getPlayerAndMadeHole(self.accountID, self.gameID)

        if isinstance(numbers, list):
            if not numbers:
                self.currentPlayer = self.player1Name if self.currentPlayer == self.player2Name else self.player2Name
                return
            for ball in numbers:
                if self.currentPlayer == self.player1Name:
                    if self.player1Category == 'solid' and ball > 8:
                        self.currentPlayer = self.player2Name
                        break 
                    elif self.player1Category == 'stripe' and 1 <= ball <= 8:
                        self.currentPlayer = self.player2Name
                        break 
                elif self.currentPlayer == self.player2Name:
                    if self.player2Category == 'solid' and ball > 8:
                        self.currentPlayer = self.player1Name
                        break 
                    elif self.player2Category == 'stripe' and 1 <= ball <= 8:
                        self.currentPlayer = self.player1Name
                        break 
            return
        
        # gameStatus = self.db.checkGamestatus(self.accountID, self.gameID)
        # if gameStatus is None:
        #     return None

        # lastShot = self.db.getLastShot(self.accountID, self.gameID)
        # if lastShot:
        #     player, category, madeBall = lastShot
        #     if madeBall:
        #         return player
        #     else:
        #         self.currentPlayer = self.player2Name if player == self.player1Name else self.player1Name
        #         return self.currentPlayer
        # else:
        #     return self.currentPlayer
            
    def gameEndResult(self):
        pass

    def close(self):
        self.db.close()

    