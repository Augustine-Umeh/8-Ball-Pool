from Database import Database
import math

FRAME_INTERVAL = 0.01

class Game:
    def __init__(self, accountID, gameID=None, gameName=None, player1Name=None, player2Name=None):
        self.db = Database()
        self.db.createDB()
        self.accountID = accountID

        # Case 1: Existing game, retrieve details
        if isinstance(gameID, int) and accountID and gameName is None and player1Name is None and player2Name is None:
            self.gameID = gameID

            try:
                gameInfo = self.db.getGame(accountID, gameID)  # Fetch game details using accountID and gameID
                if gameInfo:
                    self.gameName = gameInfo[0]
                    self.player1Name = gameInfo[1]
                    self.player2Name = gameInfo[2]
                else:
                    raise ValueError(f"No game found for accountID {accountID + 1} and gameID {gameID + 1}")
            except Exception as e:
                raise ValueError(f"Error retrieving game: {e}")

        # Case 2: New game, set details
        elif gameID is None and accountID >= 0  and isinstance(gameName, str) and isinstance(player1Name, str) and isinstance(player2Name, str):
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name

            try:
                self.gameID = self.db.setGame(accountID, gameName, player1Name, player2Name) # Create new game with accountID
            except Exception as e:
                raise ValueError(f"Error setting game: {e}")
        else:
            raise TypeError("Invalid constructor usage.")

    def shoot(self, gameName, playerName, table, xvel, yvel):
        
        try:
            # Use accountID and gameID to log a new shot
            shotID = self.db.newShot(self.accountID, self.gameID, playerName)
            new_table = table.cueBall(table, xvel, yvel)

            # Segment simulation loop
            current_table = new_table

            while True:
                segment_end_table = current_table.segment()

                if segment_end_table is None:
                    break

                segment_duration = segment_end_table.time - current_table.time
                num_frames = math.floor(segment_duration / FRAME_INTERVAL) + 1

                for frame in range(num_frames):  # Include the endpoint to ensure we capture the final state
                    frame_time = frame * FRAME_INTERVAL
                    frame_table = current_table.roll(frame_time)
                    frame_table.time = frame_time + current_table.time

                    # Record the current state of the table and the shot
                    tableID = self.db.writeTable(self.accountID, self.gameID, frame_table)
                    self.db.writeTableShot(self.accountID, self.gameID, tableID, shotID)

                current_table = segment_end_table

        except Exception as e:
            print(f"An error occurred during shooting: {e}")
         
    def close(self):
        self.db.close()

    