import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cgi
import Physics
from Game import Game
from Database import Database
import json
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

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'Account verified' if accountID >= 0 else 'Invalid account',
                'accountID': accountID
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
                    curGame = Game(accountID, gameName=gameName, player1Name=p1Name, player2Name=p2Name)
                    gameID = curGame.gameID
                    gameName = curGame.gameName
                    
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
            accountID = int(data.get('accountID'))
            gameID = int(data.get('gameID'))
        
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
                    
                    tableID = db.writeTable(accountID, gameID, initialized_table)
                    db.markGameStatus(accountID, gameID, 1)
                    
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
  
            print(f"Recieved data: {vectorData}")

            vx = vectorData['vx']
            vy = vectorData['vy']
    
            tableID = db.getLastTable(accountID, gameID)
            if tableID == -1:
                raise ValueError("This Game doesn't exist")
            
            currTable = db.readTable(accountID, gameID, tableID)

            curGame = Game(accountID, gameID=gameID)
            curGame.shoot(curGame.gameName, shotTaker, currTable, vx, vy)
            
            svg_dict = {}
            
            # Assuming db.readTable() doesn't modify the state of your database cursor or similar,
            # and you can freely call it with increasing IDs.
            while True:
                tempTable = db.readTable(accountID, gameID, tableID)
                # Break the loop if no more tables are found
                if tempTable is None:
                    break
                
                svg_dict[tableID] = tempTable.custom_svg(tempTable)
                tableID += 1
                
            print("\n", len(svg_dict), "\n")

            # Send a response back to the client
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'Success',
                'message': 'Data processed successfully',
                'svgData': svg_dict
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # Handle other POST paths or send an error
            self.send_error(404, f"Path {self.path} not found")

def calculate_velocity_components(x1, y1, x2, y2, d_max=2000):
    # Calculate the drag distance
    d = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Calculate the total velocity
    v = min((d / d_max) * 10000, 10000)
    
    # Calculate velocity components
    if d == 0:  # To avoid division by zero
        vx = 0
        vy = 0
    else:
        vx = v * (x2 - x1) / d
        vy = v * (y2 - y1) / d
        print(f"vx: {vx}, vy: {vy}")
    
    return vx, vy

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    httpd = HTTPServer(('localhost', port), MyHandler)
    print(f"Server listening on port: {port}")
    httpd.serve_forever()

# import sys
# import os
# import math
# from http.server import HTTPServer, BaseHTTPRequestHandler
# from urllib.parse import urlparse, parse_qs
# import cgi
# import phylib
# import Physics
# import json

# class MyHandler(BaseHTTPRequestHandler):

#     def create_svg_file(self, table, index):
#         # Name File appropriatley
#         filename = f"table-{index}.svg"
#         # Get table svg
#         svg_content = table.svg()
#         # Write svg as strign to file
#         with open(filename, 'w') as file:
#             file.write(svg_content)

#     def do_GET(self):
#         parsed = urlparse(self.path)

#         if parsed.path == '/index.html' or parsed.path.startswith('/table-') and parsed.path.endswith('.svg'):
#             # General handler for shoot.html and SVG files
#             file_path = '.' + parsed.path
#             if os.path.isfile(file_path):
#                 # Determine content type
#                 if parsed.path.endswith('.html'):
#                     content_type = "text/html"
#                 elif parsed.path.endswith('.svg'):
#                     content_type = "image/svg+xml"
                
#                 # Open and read the file content
#                 with open(file_path, 'r') as file:
#                     content = file.read()
                
#                 # Send response
#                 self.send_response(200)
#                 self.send_header("Content-type", content_type)
#                 self.send_header("Content-length", len(content))
#                 self.end_headers()
#                 self.wfile.write(bytes(content, "utf-8"))
#             else:
#                 # File not found, send 404
#                 self.send_error(404, f"{parsed.path} not found")
#         elif parsed.path == '/game.html':
#                 self.send_response(200)
#                 self.send_header("Content-type", "text/html")
#                 self.end_headers()

#         else:
#             # Path not recognized, send 404
#             self.send_error(404, f"{parsed.path} not found")


#     # def do_POST(self):
#     #     if self.path == '/start-game':
#     #         print("POST request received")
#     #         # Content length
#     #         content_length = int(self.headers['Content-Length'])
#     #         # Read the form data
#     #         post_data = self.rfile.read(content_length)
#     #         form_data = parse_qs(post_data.decode())

#     #         # Extract player names from the form data
#     #         player1_name = form_data.get('player1Name', [''])[0]
#     #         player2_name = form_data.get('player2Name', [''])[0]

#     #         # Prepare a simple JSON response with the path to game.html
#     #         response_data = {
#     #             'redirect': '/game.html'
#     #         }
#     #         response_json = json.dumps(response_data)

#     #         # Send the JSON response
#     #         self.send_response(303)
#     #         self.send_header('Content-type', 'application/json')
#     #         self.end_headers()
#     #         self.wfile.write(bytes(response_json, 'utf-8'))
#     #     else:
#     #         # Other POST paths or error handling
#     #         self.send_error(404, f"{self.path} not found")


# #     def do_POST(self):
# #         if self.path == '/display.html':
# #             # Content length
# #             content_length = int(self.headers['Content-Length'])
# #             # Read the form data
# #             post_data = self.rfile.read(content_length)
# #             form_data = parse_qs(post_data.decode())
        
# #             # Initialize variables
# #             sb_number = None
# #             sb_x = sb_y = rb_x = rb_y = rb_dx = rb_dy = 0.0
            
# #             # Extract form data
# #             sb_number = int(form_data.get('sb_number', [None])[0])
# #             sb_x = float(form_data.get('sb_x', [None])[0])
# #             rb_x = float(form_data.get('rb_x', [None])[0])
# #             sb_y = float(form_data.get('sb_y', [None])[0])
# #             rb_y = float(form_data.get('rb_y', [None])[0])
# #             rb_dx = float(form_data.get('rb_dx', [None])[0])
# #             rb_dy = float(form_data.get('rb_dy', [None])[0])

# #             # Delete existing SVG files
# #             for file in os.listdir('.'):
# #                 if file.startswith('table-') and file.endswith('.svg'):
# #                     os.remove(file)

# #             # Calculating Acceleration
                    
# #             rolling_ball_speed = math.sqrt((rb_dx * rb_dx) + (rb_dy * rb_dy))

# #             if (rolling_ball_speed > phylib.PHYLIB_VEL_EPSILON):
# #                 rolling_ball_acc = Physics.Coordinate((-rb_dx/rolling_ball_speed) * phylib.PHYLIB_DRAG, (-rb_dx/rolling_ball_speed) * phylib.PHYLIB_DRAG)
            
# #             rolling_ball_vel = Physics.Coordinate(rb_dx, rb_dy)
# #             rolling_ball_pos = Physics.Coordinate(rb_x, rb_y)

# #             still_ball_pos = Physics.Coordinate(sb_x, sb_y)
            
# #             # Creating Table
# #             table = Physics.Table()

# #             rollingBall = Physics.RollingBall(0, rolling_ball_pos, rolling_ball_vel, rolling_ball_acc)
# #             stillBall = Physics.StillBall(sb_number, still_ball_pos)

# #             table += rollingBall
# #             table += stillBall

# #             self.create_svg_file(table, 0)

# #             index = 1
# #             while True:
# #                 table = table.segment()
# #                 if table is None:
# #                     break
# #                 self.create_svg_file(table, index)
# #                 index += 1

# #             # Start constructing the response HTML
# #             response_html = """
# # <html>
# # <body>
# # <h2>Simulation Results</h2>
# # <p>Still Ball Number: {} at Position: ({}, {})</p>
# # <p>Rolling Ball Initial Position: ({}, {}), Velocity: ({}, {})</p>
# # <a href="/shoot.html">Back</a></body>
# # <hr>
# # </html>
# # """.format(sb_number, sb_x, sb_y, rb_x, rb_y, rb_dx, rb_dy)
            

# #             # Add img tags for each generated SVG file
# #             for file in sorted(os.listdir('.')):
# #                 if file.startswith('table-') and file.endswith('.svg'):
# #                     response_html += '<img src="{}" /><br>'.format(file)

# #             # Send the response
# #             self.send_response(200)
# #             self.send_header('Content-type', 'text/html')
# #             self.end_headers()
# #             self.wfile.write(bytes(response_html, 'utf-8'))
# #         else:
# #             self.send_error(404, f"{self.path} not found")

# if __name__ == "__main__":
#     port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
#     httpd = HTTPServer(('localhost', port), MyHandler)
#     print(f"Server listening on port: {port}")
#     httpd.serve_forever()

