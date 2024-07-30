import sqlite3
import phylib
import os
import math
import json
from collections import OrderedDict
from Physics import Coordinate, Table, StillBall, RollingBall

VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON

class Database:
    def __init__(self, reset=False):
        self.db_path = "8ball.db"
        self.madeHole = OrderedDict()
        
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
                AccountPassword VARCHAR(64) NOT NULL,
                Status INTEGER DEFAULT 0
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Notifications (
                NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
                AccountID INTEGER,
                FriendID INTEGER,
                NotInfo TEXT,
                NotInfoID INTEGER,
                isRead InTEGER,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (AccountID) REFERENCES account(AccountID),
                FOREIGN KEY (FriendID) REFERENCES account(AccountID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Friends (
                AccountID INTEGER,
                FriendID INTEGER,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (AccountID) REFERENCES Account(AccountID),
                FOREIGN KEY (FriendID) REFERENCES Account(AccountID),
                PRIMARY KEY (AccountID, FriendID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Game (
                GameID INTEGER PRIMARY KEY AUTOINCREMENT,
                AccountID INTEGER NOT NULL,
                GameName TEXT NOT NULL,
                Player1Name TEXT NOT NULL,
                Player2Name TEXT NOT NULL,
                Player1Category TEXT,
                Player2Category TEXT,
                GameUsed BOOLEAN NOT NULL DEFAULT 0,
                Winner TEXT,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
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
                ShotTaker TEXT NOT NULL,
                MadeHole TEXT,
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

    def firstwriteTable(self, accountID, gameID, table):
        cursor = self.conn.cursor()
        
        accountID += 1
        gameID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return -1  # GameID does not belong to the provided AccountID
        
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
        
        return tableID - 1 
    
    def writeTable(self, accountID, gameID, table, ballNumbers, player1Category):
        cursor = self.conn.cursor()
        
        accountID += 1
        gameID += 1
        
        ball_dict = {ball: 0 for ball in ballNumbers}
        ball_dict['0'] = 0
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return -1  # GameID does not belong to the provided AccountID
        
        
        # Step 1: Insert the time into TTable and get the new TABLEID
        cursor.execute("INSERT INTO TTable (GameID, Time) VALUES (?, ?)", (gameID, table.time))
        tableID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Step 2: For each ball on the table, insert into Ball and then into PositionsTable
        for ball in table:
            
            if isinstance(ball, StillBall):  # StillBall condition
                
                if not player1Category:
                    num = str(ball.obj.still_ball.number)
                    ball_dict[num] += 1
                
                xvel, yvel = 0, 0
                cursor.execute(
                    "INSERT INTO Ball (GameID, BallNo, XPos, YPos, XVel, YVel) VALUES (?, ?, ?, ?, ?, ?)",
                    (gameID, ball.obj.still_ball.number, ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y, xvel, yvel)
                )

            elif isinstance(ball, RollingBall):  # RollingBall condition
                
                if not player1Category:
                    num = str(ball.obj.rolling_ball.number)
                    ball_dict[num] += 1
                    
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

        if not player1Category:
            self.update_madeHole(ball_dict)
                
        
        # Commit changes and return the adjusted TABLEID
        self.conn.commit()
        cursor.close()
        return tableID - 1  # Adjusting because SQL IDs start at 1, but we want to start at 0
    
    def update_madeHole(self, ball_dict):
        for ball, val in ball_dict.items():
            if val == 0:
                self.madeHole[ball] = None
                
    def checkCueBall(self, accountID, gameID, new_table):
        accountID += 1
        gameID += 1

        # Calculate ball positions
        ball_pos = set(new_table)

        xpos = ypos = 999
        # Range of positions to check
        for x in range(500, 2500, 120):
            for y in range(1200, 300, -120):
                valid_position = True
                # Check if the position is not occupied
                if (x, y) not in ball_pos:
                    # Check if the distance is at least 56 units from any existing ball
                    for ball in new_table:
                        distance = math.sqrt((ball[1] - x) ** 2 + (ball[2] - y) ** 2)
                        if distance < 58:
                            valid_position = False
                            break
                    
                    if valid_position:
                        xpos, ypos = x, y
                        break  # Exit the y-loop if a valid position is found
            if xpos != 999 and ypos != 999:
                break  # Exit the x-loop if a valid position is found
            
        return (xpos, ypos)
    
    def updateCueBallPos(self, accountID, gameID, tableID, ballPos):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        tableID += 1

        print("first thing in updateCueBallPos")
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return -1  # GameID does not belong to the provided AccountID
        
        # Check if the cue ball already exists for this game
        check_cueball_query = """
        SELECT b.BallID 
        FROM Ball b
        JOIN PositionsTable pt ON b.BallID = pt.BallID
        JOIN TTable t ON pt.TableID = t.TableID
        WHERE t.GameID = ? AND t.TableID = ? AND b.BallNo = 0
        """
        cursor.execute(check_cueball_query, (gameID, tableID))
        result = cursor.fetchone()
        
        print("result: ", result)
        if result:
            # Cue ball exists, update its position
            cueball_id = result[0]
            update_cueball_query = "UPDATE Ball SET XPos = ?, YPos = ? WHERE BallID = ?"
            cursor.execute(update_cueball_query, (ballPos[0], ballPos[1], cueball_id))
        else:
            # Cue ball does not exist, insert it
            insert_ball_query = """
            INSERT INTO Ball (GameID, BallNo, XPos, YPos, XVel, YVel)
            VALUES (?, 0, ?, ?, 0, 0)
            """
            cursor.execute(insert_ball_query, (gameID, ballPos[0], ballPos[1]))
            cueball_id = cursor.lastrowid

            # Insert into PositionsTable
            table_id_query = "SELECT MAX(TableID) FROM TTable WHERE GameID = ?"
            cursor.execute(table_id_query, (gameID,))
            table_id = cursor.fetchone()[0]

            insert_position_query = "INSERT INTO PositionsTable (TableID, BallID) VALUES (?, ?)"
            cursor.execute(insert_position_query, (table_id, cueball_id))
            
        self.conn.commit()
        cursor.close()

    def updateTable(self, accountID, gameID, ballNumbers):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1

        isOntable = False
        cueBallPos = (999, 999)
        try:
            # Query to get balls and time in the latest table
            query = """
            SELECT b.BallID, b.BallNo, b.XPos, b.YPos, b.XVel, b.YVel, t.Time
            FROM Ball b
            JOIN PositionsTable pt ON b.BallID = pt.BallID
            JOIN TTable t ON pt.TableID = t.TableID
            WHERE t.GameID = ? AND t.TableID = (
                SELECT MAX(TableID)
                FROM TTable
                WHERE GameID = ?
            )
            """
            cursor.execute(query, (gameID, gameID))
            results = cursor.fetchall()

            if not results:
                raise ValueError("No results found for the given gameID.")

            # Extract time from the first result (all rows should have the same time)
            time = results[0][6]

            # Insert into TTable
            insert_ttable_query = """
            INSERT INTO TTable (GameID, Time)
            VALUES (?, ?)
            """
            cursor.execute(insert_ttable_query, (gameID, time))
            table_id = cursor.lastrowid

            new_table = []
            ball_dict = {ball: 0 for ball in ballNumbers}
            ball_dict['0'] = 0

            for result in results:
                ball_id, ball_no, x_pos, y_pos, x_vel, y_vel = result[0], result[1], result[2], result[3], result[4], result[5]
                valid = True
                for hole in [(0, 0), (1350, 0), (2700, 0), (0, 1350), (1350, 1350), (2700, 1350)]:
                    distance = math.sqrt((hole[0] - x_pos) ** 2 + (hole[1] - y_pos) ** 2)
                    if distance < 113:
                        valid = False
                        break
                if valid and (-53 < x_vel < 53 or -53 < y_vel < 53):

                    num = str(ball_no)
                    ball_dict[num] += 1

                    insert_ball_query = """
                    INSERT INTO Ball (GameID, BallNo, XPos, YPos, XVel, YVel)
                    VALUES (?, ?, ?, ?, 0, 0)
                    """
                    cursor.execute(insert_ball_query, (gameID, ball_no, x_pos, y_pos))

                    new_ball_id = cursor.lastrowid

                    insert_position_query = """
                    INSERT INTO PositionsTable (TableID, BallID)
                    VALUES (?, ?)
                    """
                    cursor.execute(insert_position_query, (table_id, new_ball_id))
                    new_table.append((ball_no, x_pos, y_pos))
                    if ball_no == 0:
                        cueBallPos = (x_pos, y_pos)
                        isOntable = True

            self.update_madeHole(ball_dict)

            print("Info about cueBall: ", isOntable, cueBallPos)
            # Insert into TableShot
            retrieve_shotID = """
            SELECT ShotID
            FROM TableShot
            ORDER BY TableID DESC
            LIMIT 1
            """
            cursor.execute(retrieve_shotID)
            shotID = cursor.fetchone()

            if not shotID:
                raise ValueError("No ShotID found.")

            insert_tableshot_query = """
            INSERT INTO TableShot (TableID, ShotID)
            VALUES (?, ?)
            """
            cursor.execute(insert_tableshot_query, (table_id, shotID[0]))

            if not isOntable:
                cueBallPos = self.checkCueBall(accountID - 1, gameID - 1, new_table)

            self.conn.commit()
            cursor.close()
            return isOntable, cueBallPos

        except Exception as e:
            self.conn.rollback()
            print(f"Error updating table: {e}")
            cursor.close()
            return isOntable, cueBallPos

    def getGame(self, accountID, gameID):
        cursor = self.conn.cursor()

        accountID += 1
        gameID += 1
        
        # SQL query to fetch gameName, and player names based on gameID
        query = """
        SELECT GameName, Player1Name, Player2Name, Player1Category, Player2Category, Winner
        FROM Game
        WHERE GameID = ? AND AccountID = ?
        LIMIT 1
        """

        try:
            cursor.execute(query, (gameID, accountID))
            gameInfo = cursor.fetchone()
            if gameInfo:
                return gameInfo  # This returns a tuple: (gameName, player1Name, player2Name, Player1Category, Player2Category, GameUsed)
            return None
        except Exception as e:
            print(f"An error occurred in getting game: {e}")
            return None
        finally:
            cursor.close()

    def createGame(self, accountID, gameName, player1Name, player2Name):
        cursor = self.conn.cursor()
        accountID += 1

        check_query = "SELECT 1 FROM Account WHERE AccountID = ?"
        cursor.execute(check_query, (accountID,))
        if cursor.fetchone() is None:
            cursor.close()
            return -1

        cursor.execute(
            "INSERT INTO Game (AccountID, GameName, Player1Name, Player2Name, GameUsed) VALUES (?, ?, ?, ?, ?)",
            (accountID, gameName, player1Name, player2Name, False)
        )
        
        self.updateUserStatus(accountID, 2)
        self.conn.commit()

        gameID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
        cursor.close()
        return gameID - 1

    def createAccount(self, accountName, accountPassword):
        
        if self.verifyAccount(accountName, accountPassword) >= 0:
            return -1
        
        cursor = self.conn.cursor()
        creation_query = "INSERT INTO ACCOUNT (ACCOUNTNAME, ACCOUNTPASSWORD) VALUES (?, ?)"
        
        cursor.execute(creation_query, (accountName, accountPassword))
        accountID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        self.updateUserStatus(accountID, 1)
        
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
        
        self.updateUserStatus(accountID, 1)
        
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
    
    def getLastTable(self, accountID, gameID):
        accountID += 1
        gameID += 1
        
        cursor = self.conn.cursor()
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return -1  # GameID does not belong to the provided AccountID
        
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

    def markGameStatus(self, accountID, gameID, status, winner):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        
        update_query = "UPDATE Game SET GameUsed = ? WHERE AccountID = ? AND GameID = ?"
        cursor.execute(update_query, (status, accountID, gameID))
        
        if winner:
            update_query = "UPDATE Game SET Winner = ? WHERE AccountID = ? AND GameID = ?"
            cursor.execute(update_query, (winner, accountID, gameID))
        
        self.conn.commit()
        cursor.close()

    def createShot(self, accountID, gameID, ShotTaker):
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
            insert_query = "INSERT INTO Shot (ShotTaker, GameID) VALUES (?, ?)"
            cursor.execute(insert_query, (ShotTaker, gameID))

            # Get the ID of the newly inserted shot
            shotID = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]

            self.conn.commit()
            return shotID - 1
        except Exception as e:
            print(f"An error occurred in creating shot: {e}")
            return None
        finally:
            cursor.close()

    def checkGamestatus(self, accountID, gameID):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None 

        # Check if there are no ShotIDs for the given GameID
        shot_query = "SELECT 1 FROM Shot WHERE GameID = ?"
        cursor.execute(shot_query, (gameID,))
        if cursor.fetchone() is None:
            cursor.close()
            return True

        cursor.close()
        return False
    
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
        
        cursor.execute(
            "INSERT INTO TableShot (TableID, ShotID) VALUES (?, ?)",
            (tableID, shotID)
        )
        
        self.conn.commit()

        cursor.close()
        return 0
    
    def updateShotTable(self, accountID, gameID):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None 
        
        shotID = self.getLastShotID(accountID - 1, gameID - 1)
            
        if shotID >= 1:
            # Convert OrderedDict keys to tuple of strings
            madeHole_str = ', '.join(str(key) for key in self.madeHole.keys())
            madeHole_tuple = f"({madeHole_str})"
            
            # Update the MadeHole column for the last shot
            insert_query = "UPDATE Shot SET MadeHole = ? WHERE ShotID = ? AND GameID = ?"
            print(madeHole_tuple)
            cursor.execute(insert_query, (madeHole_tuple, shotID, gameID))
            self.conn.commit()
        
        self.madeHole.clear()
        cursor.close()
        
    def getLastShotID(self, accountID, gameID):
        
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None 
        
        query = """
        SELECT ShotID
        FROM Shot
        WHERE GameID = ?
        ORDER BY ShotID DESC
        LIMIT 1;
        """
        cursor.execute(query, (gameID,))
        result = cursor.fetchone()
        
        cursor.close()
        return result[0] if result else -1
    
    def getPlayerAndMadeHole(self, accountID, gameID):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None 
        
        shotID = self.getLastShotID(accountID - 1, gameID - 1)
        if shotID < 1:
            return None, -1
        
        select_query = """
        SELECT ShotTaker, MadeHole
        FROM Shot
        WHERE ShotID = ? AND GameID = ?
        """
            
        cursor.execute(select_query, (shotID, gameID))
        name_cat = cursor.fetchone()
        
        if name_cat:
            player_name, made_hole = name_cat
            if made_hole:
                # Extract numbers from the MadeHole string
                made_hole = made_hole.strip("()")  # Remove parentheses
                if not made_hole:
                    cursor.close()
                    return player_name, []
                made_hole_numbers = [int(num.strip()) for num in made_hole.split(',')]
                if made_hole_numbers[0] == 0:
                    cursor.close()
                    return player_name, -1
                else:
                    cursor.close()
                    print(f"Player: {player_name}, MadeHole numbers: {made_hole_numbers}")
                    return player_name, made_hole_numbers    
            else:
                print(f"Player: {player_name}, No balls made in hole.")
        else:
            print("No shot found for the given ShotID and GameID.")
        
        cursor.close()
        return None, -1
        
    def updateCategory(self, accountID, gameID, player1Category, player2Category):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None 
        
        # Update the Player1Category and Player2Category for the specified GameID
        update_query = """
            UPDATE Game
            SET Player1Category = ?, Player2Category = ?
            WHERE GameID = ? AND AccountID = ?
        """
        cursor.execute(update_query, (player1Category, player2Category, gameID, accountID))
        self.conn.commit()
        cursor.close()
        
    def listGames(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1

        cursor.execute("SELECT GameID, GameName FROM Game WHERE AccountID = ? AND GameUsed = 0", (accountID,))
        results = cursor.fetchall()

        cursor.close()
        return [(gameID - 1, gameName) for gameID, gameName in results]

    def getBalls(self, gameID, tableID) -> list:
        cursor = self.conn.cursor()
        try:
            query = """
                SELECT BallNo, XPos, YPos 
                FROM Ball
                JOIN PositionsTable ON Ball.BallID = PositionsTable.BallID
                WHERE PositionsTable.TableID = ? AND Ball.GameID = ?
            """
            params = (tableID, gameID)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if rows:
                return [{'BallNo': row[0], 'XPos': row[1], 'YPos': row[2]} for row in rows]
            else:
                return None
        except Exception as e:
            print(f"An error occurred while retrieving balls: {e}")
            return None
        
    def compareTables(self, accountID, gameID, startTableID, endTableID):
        cursor = self.conn.cursor()
        accountID += 1
        gameID += 1
        startTableID += 1
        endTableID += 1
        
        # Check if the GameID belongs to the provided AccountID
        check_query = "SELECT 1 FROM Game WHERE GameID = ? AND AccountID = ?"
        cursor.execute(check_query, (gameID, accountID))
        if cursor.fetchone() is None:
            cursor.close()
            return None 
        
        try:
            startBalls = self.getBalls(gameID, startTableID)
            endBalls = self.getBalls(gameID, endTableID)
            
            if startBalls is None or endBalls is None:
                return False

            startPositions = {ball['BallNo']: (ball['XPos'], ball['YPos']) for ball in startBalls if ball['BallNo'] != 0}
            endPositions = {ball['BallNo']: (ball['XPos'], ball['YPos']) for ball in endBalls if ball['BallNo'] != 0}

            if startPositions.keys() != endPositions.keys():
                return False

            for ballNo in startPositions:
                if startPositions[ballNo] != endPositions[ballNo]:
                    return False

            return True

        except Exception as e:
            print(f"An error occurred while comparing tables: {e}")
            return False

    def addFriend(self, accountName, friendName):
        cursor = self.conn.cursor()

        try:
            # Check if both accounts exist and retrieve their IDs
            cursor.execute("SELECT AccountID FROM Account WHERE AccountName = ?", (accountName,))
            account = cursor.fetchone()

            cursor.execute("SELECT AccountID FROM Account WHERE AccountName = ?", (friendName,))
            friend = cursor.fetchone()

            if not account:
                print(f"{accountName} doesn't exist")
                return 

            if not friend:
                print(f"{friendName} doesn't exist")
                return 

            accountID = account[0]
            friendID = friend[0]

            # Add each other as friends
            cursor.execute("INSERT INTO Friends (AccountID, FriendID) VALUES (?, ?)", (accountID, friendID))
            cursor.execute("INSERT INTO Friends (AccountID, FriendID) VALUES (?, ?)", (friendID, accountID))

            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def getFriends(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1

        id_query = "SELECT FriendID FROM Friends WHERE AccountID = ?"
        cursor.execute(id_query, (accountID,))
        friend_ids = [row[0] for row in cursor.fetchall()]

        if not friend_ids:
            return []

        friends_query = "SELECT AccountName, Status FROM Account WHERE AccountID IN ({})".format(
            ",".join("?" for _ in friend_ids))
        cursor.execute(friends_query, friend_ids)

        return [row for row in cursor.fetchall()]

    def deleteFriend(self, accountName, friendName):
        cursor = self.conn.cursor()

        try:
            # Check if both accounts exist and retrieve their IDs
            cursor.execute("SELECT AccountID FROM Account WHERE AccountName = ?", (accountName,))
            account = cursor.fetchone()

            cursor.execute("SELECT AccountID FROM Account WHERE AccountName = ?", (friendName,))
            friend = cursor.fetchone()

            if not account:
                print(f"{accountName} doesn't exist")
                return 

            if not friend:
                print(f"{friendName} doesn't exist")
                return 

            accountID = account[0]
            friendID = friend[0]
            
            # Remove each other as friends
            cursor.execute("DELETE FROM Friends WHERE AccountID = ? AND FriendID = ?", (accountID, friendID))
            cursor.execute("DELETE FROM Friends WHERE AccountID = ? AND FriendID = ?", (friendID, accountID))

            self.conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def getGameStats(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1
        
        stats_query = 'SELECT Player2Name, Winner FROM Game WHERE AccountID = ?'
        cursor.execute(stats_query, (accountID,))
        res = cursor.fetchall()
        
        cursor.close()
        return res
    
    def getID(self, name):
        cursor = self.conn.cursor()
        
        id_query = "SELECT accountID FROM Account WHERE AccountName = ?"
        cursor.execute(id_query, (name,))
        res = cursor.fetchone()
        
        cursor.close() 
        if res:
            return res[0] - 1
        return -1
    
    def getName(self, ID):
        cursor = self.conn.cursor()
        ID += 1
        
        name_query = "SELECT accountName FROM Account WHERE AccountID = ?"
        cursor.execute(name_query, (ID,))
        res = cursor.fetchone()
        
        cursor.close() 
        if res:
            return res[0]
        return None
    
    def areFriends(self, accountID, friendID):
        cursor = self.conn.cursor()
        accountID += 1
        friendID += 1
        
        check_friendQuery = "SELECT 1 FROM Friends WHERE AccountID = ? AND FriendID = ?"
        cursor.execute(check_friendQuery, (accountID, friendID))
        res = cursor.fetchone()
        
        cursor.close()
        if res:
            return True
        return False
        
    def addNotification(self, accountID, friendID, message, notIfoID):
        cursor = self.conn.cursor()
        accountID += 1
        friendID += 1
        
        check_query = "SELECT 1 FROM Notifications WHERE AccountID = ? AND  FriendID = ? AND NotInfo = ?"
        cursor.execute(check_query, ((friendID, accountID, message)))
        res = cursor.fetchone()
        
        if res:
            return 
        
        insert_query = "INSERT INTO Notifications (AccountID, FriendID, NotInfo, NotInfoID, isRead) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (friendID, accountID, message, notIfoID, 0))
        
        self.conn.commit()
        cursor.close()
        
    def updateUserStatus(self, accountID, status):
        cursor = self.conn.cursor()
        accountID += 1
        
        update_query = "UPDATE Account SET Status = ?"
        cursor.execute(update_query, (status,))
        
        self.conn.commit()
        cursor.close()
        
    def getNotifications(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1
        
        select_query = """
            SELECT NotificationID, FriendID, NotInfo, NotInfoID, isRead
            FROM Notifications
            WHERE AccountID = ?
            ORDER BY NotificationID DESC
            LIMIT 10
        """
        cursor.execute(select_query, (accountID,))
        notifications = cursor.fetchall()
        
        if notifications:
            update_query = "UPDATE Notifications SET isRead = ? WHERE accountID = ?"
            cursor.execute(update_query, (1, accountID))
        
        self.conn.commit()
        cursor.close()
        return notifications
        
    def deleteNotification(self, notificationID):
        cursor = self.conn.cursor()
        
        delete_query = "DELETE FROM Notifications WHERE NotificationID = ?"
        cursor.execute(delete_query, (notificationID,))
        
        self.conn.commit()
        cursor.close()

    def clearNotifications(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1
        
        delete_query = "DELETE FROM Notifications WHERE AccountID = ?"
        cursor.execute(delete_query, (accountID,))
        
        self.conn.commit()
        cursor.close()

    def close(self):
        # Commit any pending transaction and close the connection
        self.conn.commit()
        self.conn.close()
        