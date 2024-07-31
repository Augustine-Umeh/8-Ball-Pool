import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cgi
import Physics
from Game import Game
from Database import Database
import json
import random
import phylib
import math


class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/' or parsed.path == '/index.html':
            self.path = '/index.html'

        file_path = '.' + self.path
        if os.path.isfile(file_path):
            # Default content type
            content_type = "application/octet-stream"

            # Determine specific content type
            if self.path.endswith('.html'):
                content_type = "text/html"
            elif self.path.endswith('.svg'):
                content_type = "image/svg+xml"
            elif self.path.endswith('.js'):
                content_type = "application/javascript"
            elif self.path.endswith('.css'):
                content_type = "text/css"

            # Open and read the file content
            with open(file_path, 'rb') as file:
                content = file.read()

            # Send response
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(content)
        else:
            # File not found, send 404
            self.send_error(404, f"{self.path} not found")

    def do_POST(self):
        db = Database()
        db.createDB()
        
        if self.path == '/createAccount':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountName = data.get('accountName')
            accountPassword = data.get('accountPassword')

            accountID = db.createAccount(accountName, accountPassword)

            db.updateUserStatus(accountID, 1)
            
            self.send_response(201)  
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'Account created successfully' if accountID >= 0 else  'Account already exists',
                'accountID': accountID
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/verifyAccount':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountName = data.get('accountName')
            accountPassword = data.get('accountPassword')

            accountID = db.verifyAccount(accountName, accountPassword)
            db.updateUserStatus(accountID, 1)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'Account verified' if accountID >= 0 else 'Invalid account',
                'accountID': accountID
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/friendsList':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = data['accountID']
            
            friends = db.getFriends(accountID)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'friends': friends
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/gameInvite':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = data['accountID']
            accountName = data['accountName']
            friendName = data['friendName']
            
            friendID = db.getID(friendName)
            if friendID < 0:
                raise ValueError("This friend doesn't exist")
            
            message = f"{accountName} invites you to a game"
            db.addNotification(accountID, friendID, message, 2)
        
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'message': 'Invite sent'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif self.path == '/friendInvite':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = data['accountID']
            accountName = data['accountName']
            friendName = data['friendName']
            
            friendID = db.getID(friendName)
            if friendID >= 0:
                res = db.areFriends(accountID, friendID)
                if res:
                    output = f"{friendName} is already a friend"
                else:
                    message = f"{accountName} wants to be friends"
                    db.addNotification(accountID, friendID, message, 2)
                    output = 'Invite sent'
            else:
                output = "This player doesn't exist"
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'message': output
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/removeFriend':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountName = data['accountName']
            friendName = data['friendName']
            
            db.deleteFriend(accountName, friendName)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'message': 'success'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif self.path == '/rejectGameInvite':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            notificationID = data['notificationID']
            senderID = data['accountID']
            friendName = data['friendName']
            message = f'{friendName} rejected your game invite'
            
            receiverID = db.getID(friendName)
            if receiverID < 0:
                raise ValueError("This friend doesn't exist")

            db.deleteNotification(notificationID)
            db.addNotification(senderID, receiverID, message, 3)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'Invite rejected and sender notified'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/acceptInvite':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = data['accountID']
            friendID = data['friendID']
            notificationID = data['notificationID']
            
            friendID -= 1
            accountName = db.getName(accountID)
            friendName = db.getName(friendID)
            
            if not accountName or not friendName:
                raise ValueError("Either account doesn't exist")
            
            db.addFriend(accountName, friendName)
            
            message = f'{accountName} accepted your friend invite'
            db.addNotification(accountID, friendID, message, 1)
            
            db.deleteNotification(notificationID)
            notifications = db.getNotifications(accountID)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'message': 'Invite accepted',
                'notifications': notifications
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/declineInvite':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = data['accountID']
            friendID = data['friendID']
            notificationID = data['notificationID']
            
            friendID -= 1
            accountName = db.getName(accountID)
            friendName = db.getName(friendID)
            
            if not accountName or not friendName:
                raise ValueError("Either account doesn't exist")
            
            message = f'{accountName} declined your friend invite'
            db.addNotification(accountID, friendID, message, 3)
            
            db.deleteNotification(notificationID)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'message': 'Invite declined'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
        elif self.path == '/notificationlist':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = data['accountID']
            
            notifications = db.getNotifications(accountID)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'notifications': notifications
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/stats':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = data['accountID']
            
            stats = db.getGameStats(accountID)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'stats': stats
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif self.path == '/logOut':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = data['accountID']
            
            db.updateUserStatus(accountID, 0)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'Logged out successfully'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/retrieveGames':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            accountID = int(data['accountID'])
            
            tables = db.retrieveGames(accountID)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'tables': tables
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif self.path == '/startGame':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            p1Name = data['p1Name']
            p2Name = data['p2Name']
            gameName = data['gameName']
            accountID = int(data['accountID'])
            
            try:
                created_game = db.checkCreatedGame(accountID)
                
                if created_game[0] >= 0:
                    gameID = created_game[0] - 1
                    gameName = created_game[1]
                else:
                    if not gameName:
                        gameName = p1Name + " vs " + p2Name
                    curGame = Game(accountID, shotTaker=None, gameName=gameName, player1Name=p1Name, player2Name=p2Name, play1balls=None, play2balls=None)
                    gameID = curGame.gameID
                    gameName = curGame.gameName
                    
                db.updateUserStatus(accountID, 2)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'Game Created successfully',
                    'gameID': gameID,
                    'gameName': gameName
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'Error',
                    'message': str(e)
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/initializeTable':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            data = json.loads(post_data.decode('utf-8'))
            accountID = int(data['accountID'])
            gameID = int(data['gameID'])
            
            try:
                unfinished_game = db.checkUnfinishedGame(accountID, gameID)
                
                if unfinished_game:
                    tableID = db.getLastTable(accountID, gameID)
                    
                    if tableID == -1:
                        raise ValueError("This Game doesn't exist")
                    
                    table = db.readTable(accountID, gameID, tableID)
                  
                    table_svg = table.custom_svg(table)
                    
                else:
                    table = Physics.Table()
                    table.time = 0.0
                    
                    initialized_table = table.initializeTable(table)
                    table_svg = initialized_table.custom_svg(initialized_table)
                    
                    tableID = db.firstwriteTable(accountID, gameID, initialized_table)

                    db.markGameStatus(accountID, gameID, 1, None)
                    
                    if tableID == -1:
                        raise ValueError("This Game doesn't exist")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'message': 'Table initialized successfully',
                    'svg': table_svg,
                    'tableID': tableID
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'error': str(e)
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif self.path == '/processDrag':
            
            content_length = int(self.headers['Content-Length'])  # Gets the size of data
            post_data = self.rfile.read(content_length)  # Gets the data itself

            # Parse the data from JSON
            data = json.loads(post_data.decode('utf-8'))
            vectorData = data['velocity']
            accountID = int(data["accountID"])
            gameID = int(data["gameID"])
            shotTaker = data['shotTaker']
            cueBallPos = data['cueBallPos']
            isOntable = data['isOntable']
            ballNumbers = data['ballNumbers']
            play1balls = data['play1balls']
            play2balls = data['play2balls']

            endResult = []
            tableID = db.getLastTable(accountID, gameID)
            
            vx = vectorData['vx']
            vy = vectorData['vy']
            
            startTableID = tableID
            
            print("tableID to read from ", tableID)
            if tableID == -1:
                raise ValueError("This Game doesn't exist")

            play1balls = set(play1balls)
            play2balls = set(play2balls)
            
            curGame = Game(accountID, shotTaker=shotTaker, gameID=gameID, play1balls=play1balls, play2balls=play2balls)   
            curGame.ballNumbers = ballNumbers
            
            if not isOntable:
                db.updateCueBallPos(accountID, gameID, tableID, (cueBallPos['x'], cueBallPos['y']))
            
            currTable = db.readTable(accountID, gameID, tableID)
            curGame.shoot(shotTaker, currTable, vx, vy)
            
            isOntable, cueBallPos = db.updateTable(accountID, gameID, ballNumbers)
            if not isOntable:
                endResult.append("cue ball went into the hole")
                curGame.scratch = True
                
            db.updateShotTable(accountID, gameID)
            
            svg_dict = {}
            tableID += 1
            
            print("start tableID: ", tableID)
            while True:
                tempTable = db.readTable(accountID, gameID, tableID)
                if tempTable is None:
                    break
                
                svg_dict[tableID] = tempTable.custom_svg(tempTable)
                tableID += 1
            print("end tableID: ", tableID)
            endTableID = tableID - 1
            print("\nLength of svg dict: ", len(svg_dict), "\n")
            
            winner = None
            name, decision = curGame.isGameEnd()
            if decision == 'winner':
                winner = name
                db.updateUserStatus(accountID, 1)
                
            if curGame.first_ball_hit == 'False':
                curGame.scratch = True
                endResult.append("Didn't make first contact with any of your team balls")
                
            if not curGame.player1Category:
                curGame.setPlayerCategory()
                if curGame.player1Category:
                    endResult.append(f"{curGame.player1Name} has {curGame.player1Category} and {curGame.player2Name} has {curGame.player2Category}")
                    curGame.setPlayerBalls()
            
            curGame.playerTurn(isOntable)
            shotTaker = curGame.currentPlayer
            print("player's Turn: ", shotTaker)
            
            play1balls = list(curGame.play1balls)
            play2balls = list(curGame.play2balls)

            res = db.compareTables(accountID, gameID, startTableID, endTableID)
            if res: 
                endResult.append('Cue ball made no contact with another ball')
                curGame.scratch = True
            
            if winner:
                endResult = []
            
            # Send a response back to the client
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'Success',
                'message': 'Data processed successfully',
                'svgData': svg_dict,
                'isOntable': isOntable,
                'cueBallPos': cueBallPos,
                'shotTaker': shotTaker,
                'play1balls': play1balls,
                'play2balls': play2balls,
                'sameTables': curGame.scratch,
                'endResult': endResult,
                'winner': winner
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # Handle other POST paths or send an error
            self.send_error(404, f"Path {self.path} not found")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    httpd = HTTPServer(('localhost', port), MyHandler)
    print(f"Server listening on port: {port}")
    httpd.serve_forever()
