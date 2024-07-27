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

    def getGameStats(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1
        
        stats_query = 'SELECT Player2Name, Winner FROM Game WHERE AccountID = ?'
        cursor.execute(stats_query, (accountID,))
        res = cursor.fetchall()
        
        cursor.close()
        return res
    
    def addNotification(self, accountID, friendID, message):
        cursor = self.conn.cursor()
        accountID += 1
        fFriendID += 1
        
        check_friendQuery = "SELECT 1 FROM Friends WHERE AccountID = ? AND FriendID = ?"
        cursor.execute(check_friendQuery, (accountID, friendID))
        res = cursor.fetchall()
        
        if not res:
            print("They are not friends")
            return
        
        insert_query = "INSERT INTO Notifications (AccountID, FriendID, NotInfo) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (friendID, accountID, message))
        
        self.conn.commit()
        cursor.close()
        
    def getNotifications(self, accountID):
        cursor = self.conn.cursor()
        accountID += 1
        
        select_query = "SELECT NotificationID, FriendID, NotInfo FROM Notifications WHERE AccountID = ?"
        cursor.execute(select_query, (accountID,))
        notifications = cursor.fetchall()
        
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