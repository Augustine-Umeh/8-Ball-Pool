import sqlite3
import phylib
import os
import math
import json
from Physics import Coordinate, Table, StillBall, RollingBall

VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON

class Database:
    def __init__(self, reset=False):
        self.db_path = "8ball.db"
        
        if reset:
            # Delete existing database if reset True
            try:
                os.remove(self.db_path)
            except FileNotFoundError:
                # If file does not exist, do nothing
                pass
        
        # Create database connection
        self.conn = sqlite3.connect(self.db_path)
    
    def createDB(self):
        cursor = self.conn.cursor()
        
        # List of SQL commands to create the tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS Account (
                AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
                AccountName TEXT(64) NOT NULL,
                AccountPassword VARCHAR(64) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Game (
                GameID INTEGER PRIMARY KEY AUTOINCREMENT,
                AccountID INTEGER NOT NULL,
                GameName TEXT NOT NULL,
                Player1Name TEXT NOT NULL,
                Player2Name TEXT NOT NULL,
                GameUsed BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (AccountID) REFERENCES Account(AccountID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS TTable (
                TableID INTEGER PRIMARY KEY AUTOINCREMENT,
                GameID INTEGER NOT NULL,
                Time REAL NOT NULL,
                FOREIGN KEY (GameID) REFERENCES Game(GameID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Ball (
                BallID INTEGER PRIMARY KEY AUTOINCREMENT,
                GameID INTEGER NOT NULL,
                BallNo INTEGER NOT NULL,
                XPos REAL NOT NULL,
                YPos REAL NOT NULL,
                XVel REAL,
                YVel REAL,
                FOREIGN KEY (GameID) REFERENCES Game(GameID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS PositionsTable (
                TableID INTEGER NOT NULL,
                BallID INTEGER NOT NULL,
                FOREIGN KEY (TableID) REFERENCES TTable(TableID),
                FOREIGN KEY (BallID) REFERENCES Ball(BallID),
                PRIMARY KEY (TableID, BallID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Shot (
                ShotID INTEGER PRIMARY KEY AUTOINCREMENT,
                PlayerName TEXT NOT NULL,
                GameID INTEGER NOT NULL,
                FOREIGN KEY (GameID) REFERENCES Game(GameID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS TableShot (
                TableID INTEGER NOT NULL,
                ShotID INTEGER NOT NULL,
                FOREIGN KEY (TableID) REFERENCES TTable(TableID),
                FOREIGN KEY (ShotID) REFERENCES Shot(ShotID),
                PRIMARY KEY (TableID, ShotID)
            );
            """
        ]

        # Executing all commands
        for command in tables:
            cursor.execute(command)
        
        # Commit changes and close cursor
        self.conn.commit()
        cursor.close()
    
    def readTable(self, accountID, gameID, tableID):
        cursor = self.conn.cursor()
        
        accountID += 1
        gameID += 1
        tableID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None  # GameID does not belong to the provided AccountID

        # SQL query to retrieve Balls and Table time for a given gameID and tableID
        query = """
        SELECT b.BALLID, b.BALLNO, b.XPOS, b.YPOS, b.XVEL, b.YVEL, t.TIME
        FROM PositionsTable pt
        JOIN Ball b ON pt.BALLID = b.BALLID
        JOIN TTable t ON pt.TABLEID = t.TABLEID
        WHERE pt.TABLEID = ? AND t.GAMEID = ?
        """
        cursor.execute(query, (tableID, gameID))
        rows = cursor.fetchall()
        
        # Check if TABLEID exists in the BallTable
        if not rows:
            return None  # No Balls found for the given TABLEID
        
        # Instantiate a new Table object
        new_table = Table()
        new_table.time = rows[0][-1]  # Set table's time using the last column from the first row
        
        # Process each ball
        for row in rows:
            ballID, ballNO, xPos, yPos, xVel, yVel, _ = row # Unpack the row
            
            # Determine if the ball is still or rolling and add accordingly
            if xVel == 0 and yVel == 0:  # StillBall condition
                new_ball = StillBall(ballNO, Coordinate(xPos, yPos))
            else:  # RollingBall condition
                
                rolling_ball_speed = math.sqrt((xVel * xVel) + (yVel * yVel))

                if (rolling_ball_speed > VEL_EPSILON):
                    rolling_ball_acc = Coordinate((-xVel/rolling_ball_speed) * phylib.PHYLIB_DRAG, (-yVel/rolling_ball_speed) * phylib.PHYLIB_DRAG)
                else:
                    rolling_ball_acc = Coordinate(0, 0)

                rolling_ball_vel = Coordinate(xVel, yVel)
                rolling_ball_pos = Coordinate(xPos, yPos)

                new_ball = RollingBall(ballNO, rolling_ball_pos, rolling_ball_vel, rolling_ball_acc)
                
            new_table += new_ball  
        
        cursor.close()
        
        return new_table

    def writeTable(self, accountID, gameID, table):
        cursor = self.conn.cursor()
        
        accountID += 1
        gameID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None  # GameID does not belong to the provided AccountID
        
        # Step 1: Insert the time into TTable and get the new TABLEID
        cursor.execute("INSERT INTO TTable (GameID, Time) VALUES (?, ?)", (gameID, table.time))
        tableID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Step 2: For each ball on the table, insert into Ball and then into PositionsTable
        for ball in table:
            if isinstance(ball, StillBall):  # StillBall condition
                xvel, yvel = 0, 0
                cursor.execute(
                    "INSERT INTO Ball (GameID, BallNo, XPos, YPos, XVel, YVel) VALUES (?, ?, ?, ?, ?, ?)",
                    (gameID, ball.obj.still_ball.number, ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y, xvel, yvel)
                )

            elif isinstance(ball, RollingBall):  # RollingBall condition
                xvel, yvel = ball.obj.rolling_ball.vel.x, ball.obj.rolling_ball.vel.y
                cursor.execute(
                    "INSERT INTO Ball (GameID, BallNo, XPos, YPos, XVel, YVel) VALUES (?, ?, ?, ?, ?, ?)",
                    (gameID, ball.obj.rolling_ball.number, ball.obj.rolling_ball.pos.x, ball.obj.rolling_ball.pos.y, xvel, yvel)
                )
            else:  # Skip if not a ball
                continue

            # Insert the ball into Ball table and link the ball to the table in PositionsTable
            ballID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
            cursor.execute("INSERT INTO PositionsTable (TableID, BallID) VALUES (?, ?)", (tableID, ballID))

        # Commit changes and return the adjusted TABLEID
        self.conn.commit()
        cursor.close()
        
        return tableID - 1  # Adjusting because SQL IDs start at 1, but we want to start at 0
    
    def getGame(self, accountID, gameID):
        cursor = self.conn.cursor()

        accountID += 1
        gameID += 1
        
        # SQL query to fetch gameName, and player names based on gameID
        query = """
        SELECT GameName, Player1Name, Player2Name
        FROM Game
        WHERE GameID = ? AND AccountID = ?
        LIMIT 1
        """

        try:
            cursor.execute(query, (gameID, accountID))
            gameInfo = cursor.fetchone()
            if gameInfo:
                return gameInfo  # This returns a tuple: (gameName, player1Name, player2Name)
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cursor.close()

    def setGame(self, accountID, gameName, player1Name, player2Name):
        cursor = self.conn.cursor()
        
        accountID += 1
        # SQL query to insert a new game into the Game table
        query = """
        INSERT INTO Game (AccountID, GameName, Player1Name, Player2Name)
        VALUES (?, ?, ?, ?)
        """
        
        try:
            cursor.execute(query, (accountID, gameName, player1Name, player2Name))
            self.conn.commit()
            
            # Get the GameID of the newly inserted game
            gameID = cursor.lastrowid
            return gameID - 1
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    def createAccount(self, accountName, accountPassword):
        
        if self.verifyAccount(accountName, accountPassword) >= 0:
            return -1
        
        cursor = self.conn.cursor()
        creation_query = "INSERT INTO ACCOUNT (ACCOUNTNAME, ACCOUNTPASSWORD) VALUES (?, ?)"
        
        cursor.execute(creation_query, (accountName, accountPassword))
        accountID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        self.conn.commit()
        cursor.close()
        return accountID - 1
    
    def verifyAccount(self, accountName, accountPassword):
        
        cursor = self.conn.cursor()
        verification_query = "SELECT AccountID FROM Account WHERE AccountName = ? AND AccountPassword = ?"
        
        cursor.execute(verification_query, (accountName, accountPassword))
        row = cursor.fetchone()
        if not row:
            return -1
        
        accountID = row[0]
        
        cursor.close()
        return accountID - 1
    
    def checkCreatedGame(self, accountID):
        accountID += 1
        cursor = self.conn.cursor()
        
        check_query = "SELECT GameID, GameName FROM Game WHERE AccountID = ? AND GameUsed = 0"
        
        cursor.execute(check_query, (accountID,))
        created_game = cursor.fetchone()
    
        cursor.close()
        return created_game if created_game else (-1, None)
        
    def checkUnfinishedGame(self, accountID, gameID):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        
        check_query = "SELECT 1 FROM Game WHERE AccountID = ? AND GameUsed = 1 AND GameID = ?"
        
        cursor.execute(check_query, (accountID, gameID))
        created_game = cursor.fetchone()
        
        cursor.close()
        return True if created_game else False
    
    def getLastTable(self, gameID):
        gameID += 1
        
        cursor = self.conn.cursor()
        
        last_table_query = """
        SELECT MAX(TableID) FROM TTable WHERE GameID = ?
        """
        
        cursor.execute(last_table_query, (gameID,))
        last_tableID = cursor.fetchone()[0]
        
        return last_tableID - 1
    
    def getSessionGames(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1
        
        # Step 1: Retrieve all unfinished games
        check_query = "SELECT GameID FROM Game WHERE AccountID = ? AND GameUsed = 1"
        cursor.execute(check_query, (accountID,))
        unfinished_games = cursor.fetchall()

        result = {}
        for game in unfinished_games:
            gameID = game[0]

            # Step 2: Find the last table state for the current gameID
            last_table_query = """
            SELECT MAX(TableID) FROM TTable WHERE GameID = ?
            """
            cursor.execute(last_table_query, (gameID,))
            last_tableID = cursor.fetchone()[0]

            if last_tableID is not None:
                # Step 3: Retrieve positions and velocities of the 16 balls from the last table state
                ball_query = """
                SELECT Ball.BallNo, Ball.XPos, Ball.YPos, Ball.XVel, Ball.YVel
                FROM Ball
                JOIN PositionsTable ON Ball.BallID = PositionsTable.BallID
                WHERE PositionsTable.TableID = ?
                """
                cursor.execute(ball_query, (last_tableID,))
                balls = cursor.fetchall()

                # Step 4: Create StillBall instances for each ball and add them to a table
                table = Table()
                for ball in balls:
                    ball_number, pos_x, pos_y, x_vel, y_vel = ball
                    still_ball = StillBall(ball_number, Coordinate(pos_x, pos_y))
                    table += still_ball

                # Step 5: Generate SVG for the table
                table_svg = table.custom_svg(table)
                result[gameID] = table_svg

        cursor.close()
        
        # Step 6: Return JSON
        return json.dumps(result)

    def markGameStatus(self, accountID, gameID, status):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        
        update_query = "UPDATE Game SET GameUsed = ? WHERE AccountID = ? AND GameID = ?"
        
        cursor.execute(update_query, (status, accountID, gameID))
        
        self.conn.commit()
        cursor.close()

    def newShot(self, accountID, gameID, playerName):
        cursor = self.conn.cursor()

        accountID += 1
        gameID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None  # GameID does not belong to the provided AccountID

        try:
            # Insert the new shot into the Shot table
            insert_query = "INSERT INTO Shot (PlayerName, GameID) VALUES (?, ?)"
            cursor.execute(insert_query, (playerName, gameID))

            # Get the ID of the newly inserted shot
            shotID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Commit the changes and return the shotID
            self.conn.commit()
            
            return shotID - 1
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cursor.close()

    def writeTableShot(self, accountID, gameID, tableID, shotID):
        cursor = self.conn.cursor()

        accountID += 1
        gameID += 1
        tableID += 1
        shotID += 1
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None  # GameID does not belong to the provided AccountID

        # Check if the tableID belongs to the provided gameID
        check_query = "SELECT 1 FROM TTable WHERE TableID = ? AND GameID = ?"
        cursor.execute(check_query, (tableID, gameID))
        if cursor.fetchone() is None:
            cursor.close()
            return None  # tableID does not belong to the provided gameID

        # Check if the shotID belongs to the provided gameID
        check_query = "SELECT 1 FROM Shot WHERE ShotID = ? AND GameID = ?"
        cursor.execute(check_query, (shotID, gameID))
        if cursor.fetchone() is None:
            cursor.close()
            return None  # shotID does not belong to the provided gameID

        try:
            # Insert the new table shot into the TableShot table
            insert_query = "INSERT INTO TableShot (TableID, ShotID) VALUES (?, ?)"
            cursor.execute(insert_query, (tableID, shotID))

            # Get the ID of the newly inserted table shot
            tableShotID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Commit the changes and return the tableShotID
            self.conn.commit()
            
            return tableShotID - 1
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cursor.close()

    def close(self):
        # Commit any pending transaction and close the connection
        self.conn.commit()
        self.conn.close()
        