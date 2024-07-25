from Database import Database

class playerProfile:
    def __init__(self):
        self.db = Database()
        self.db.createDB()
        self.conn = self.db.conn

    def listGames(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1

        cursor.execute("SELECT GameID, GameName FROM Game WHERE AccountID = ? AND GameUsed = 0", (accountID,))
        results = cursor.fetchall()

        cursor.close()
        return [(gameID - 1, gameName) for gameID, gameName in results]

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

        friends_query = "SELECT AccountName FROM Account WHERE AccountID IN ({})".format(
            ",".join("?" for _ in friend_ids))
        cursor.execute(friends_query, friend_ids)

        return [row[0] for row in cursor.fetchall()]

    def checkCreatedGame(self, accountID):
        accountID += 1
        cursor = self.conn.cursor()

        check_query = "SELECT GameID, GameName FROM Game WHERE AccountID = ? AND GameUsed = 0"

        cursor.execute(check_query, (accountID,))
        created_game = cursor.fetchone()

        cursor.close()
        return created_game if created_game else (-1, None)

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

    def getScore(self, gameID, playerName):
        cursor = self.conn.cursor()
        gameID += 1

        check_query = "SELECT 1 FROM Game WHERE GameID = ?"
        cursor.execute(check_query, (gameID,))
        if cursor.fetchone() is None:
            cursor.close()
            return -1

        query = """
        SELECT s.ShotID
        FROM Shot s
        WHERE s.PlayerName = ? AND s.GameID = ?
        """
        cursor.execute(query, (playerName, gameID))
        shots = cursor.fetchall()

        score = 0
        for shot in shots:
            shotID = shot[0]

            query = """
            SELECT t.TableID
            FROM TableShot ts
            JOIN TTable t ON ts.TableID = t.TableID
            WHERE ts.ShotID = ?
            """
            cursor.execute(query, (shotID,))
            tables = cursor.fetchall()

            for table in tables:
                tableID = table[0]
                query = """
                SELECT b.BallID
                FROM Ball b
                JOIN PositionsTable pt ON b.BallID = pt.BallID
                WHERE pt.TableID = ?
                """
                cursor.execute(query, (tableID,))
                balls = cursor.fetchall()

                score += len(balls)

    def getGameStats(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1
        
        stats_query = 'SELECT Player2Name, Winner FROM Game WHERE AccountID = ?'
        cursor.execute(stats_query, (accountID,))
        res = cursor.fetchall()
        
        return res
    
        cursor.close()
        return score