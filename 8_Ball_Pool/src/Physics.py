import phylib;
import os;
import sqlite3;
import math;

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";

FOOTER = """</svg>\n""";

################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS;
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER;

HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS;
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH;
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH;

SIM_RATE = phylib.PHYLIB_SIM_RATE;
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON;

DRAG = phylib.PHYLIB_DRAG;
MAX_TIME = phylib.PHYLIB_MAX_TIME;

MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS;

# Assignement 3 constants
FRAME_INTERVAL = 0.01

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
    ];



################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass;


################################################################################
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall;


    # add an svg method here
    def svg(self):
        return """ <circle class="ball" cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (
            self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number])


################################################################################
class RollingBall( phylib.phylib_object ):
    """
    Python RollingBall class.
    """

    def __init__( self, number, pos, vel, acc):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_ROLLING_BALL, 
                                       number, 
                                       pos, vel, acc, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a Rolling class
        self.__class__ = RollingBall;


    # add an svg method here
    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (
            self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number])


################################################################################
class Hole( phylib.phylib_object ):
    """
    Python Hole class.
    """

    def __init__( self, pos):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HOLE, 
                                       0, 
                                       pos, None, None , 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a Hole class
        self.__class__ = Hole;


    # add an svg method here
    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (
            self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS)

################################################################################
class HCushion( phylib.phylib_object ):
    """
    Python HCushion class.
    """

    def __init__( self, y):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HCUSHION,
                                       0, 
                                       None, None, None , 
                                       0.0, y);
      
        # this converts the phylib_object into a Rolling class
        self.__class__ = HCushion;


    # add an svg method here
    def svg(self):
        y = -25 if self.obj.hcushion.y == 0 else 2700
        return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % (y)


################################################################################
class VCushion( phylib.phylib_object ):
    """
    Python VCushion class.
    """

    def __init__( self, x):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_VCUSHION, 
                                       0, 
                                       None, None, None , 
                                       x, 0.0);
      
        # this converts the phylib_object into a Rolling class
        self.__class__ = VCushion;


    # add an svg method here
    def svg(self):
        x = -25 if self.obj.hcushion.y == 0 else 1350
        return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % (x)


################################################################################

class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self;

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;

    # add svg method here
    def svg(self):
        svg_str = HEADER

        for obj in self:
            if obj is not None:
                svg_str += obj.svg()
        svg_str += FOOTER
        return svg_str
    
    # Roll Method
    def roll(self, t):
            new_table = Table()
            for ball in self:
                if isinstance(ball, RollingBall):
                    # Create a new ball with the same number as the old ball
                    new_ball = RollingBall(ball.obj.rolling_ball.number,
                                        Coordinate(0,0), Coordinate(0,0),
                                        Coordinate(0,0))
                    # Compute where it rolls to (assuming phylib_roll is a placeholder for the actual calculation)
                    phylib.phylib_roll(new_ball, ball, t)
                    # Add ball to table
                    new_table += new_ball
                if isinstance(ball, StillBall):
                    # Create a new ball with the same number and pos as the old ball
                    new_ball = StillBall(ball.obj.still_ball.number,
                                        Coordinate(ball.obj.still_ball.pos.x,
                                                    ball.obj.still_ball.pos.y))
                    # Add ball to table
                    new_table += new_ball
            # Return table
            return new_table

    def cueBall(self, table, xvel, yvel):
        new = Table()
        for ball in table:
            if isinstance( ball, RollingBall ):
                new += ball;
            elif isinstance( ball, StillBall ):
                if ball.obj.still_ball.number == 0:
                    # Turn this into rolling and calc acc
                    xpos, ypos = ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y
            
                    cue_ball_pos = Coordinate(xpos, ypos)
                    cue_ball_vel = Coordinate(xvel, yvel)

                    # Calculating acceleration
                    cue_ball_speed = math.sqrt((xvel * xvel) + (yvel * yvel))

                    if (cue_ball_speed > VEL_EPSILON):
                        cue_ball_acc = Coordinate((-xvel/cue_ball_speed) * phylib.PHYLIB_DRAG, (-yvel/cue_ball_speed) * phylib.PHYLIB_DRAG)
                    else:
                        cue_ball_acc = Coordinate(0.0, 0.0)
                    
                    cue_ball = RollingBall( 0,
                        cue_ball_pos,
                        cue_ball_vel,
                        cue_ball_acc );

                    new += cue_ball
                else:
                    new += ball
        return new
    def initializeTable(self, table):
        table += StillBall(0, Coordinate(675, 2025))
        table += StillBall(1, Coordinate(675, 400))
        table += StillBall(2, Coordinate(735, 400))
        table += StillBall(3, Coordinate(795, 400))
        table += StillBall(4, Coordinate(615, 400))
        table += StillBall(5, Coordinate(555, 400))
        table += StillBall(6, Coordinate(705,460))
        table += StillBall(7, Coordinate(765,460))
        table += StillBall(8, Coordinate(645,460))
        table += StillBall(9, Coordinate(585, 460))
        table += StillBall(10, Coordinate(675, 520))
        table += StillBall(11, Coordinate(735, 520))
        table += StillBall(12, Coordinate(615, 520))
        table += StillBall(13, Coordinate(705, 580))
        table += StillBall(14, Coordinate(645, 580))
        table += StillBall(15, Coordinate(675, 640))

        return table.custom_svg(table)

    def custom_svg(self, table):
        # Making svg with cue_ball having id
        svg_str = HEADER

        for obj in table:
            if obj is not None:
                if isinstance(obj, StillBall):
                    if obj.obj.still_ball.number == 0:
                        svg_str += """ <circle cx="%d" cy="%d" r="%d" fill="%s" id="cue_ball" />\n""" % (
                            obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[obj.obj.still_ball.number])
                    else:
                        svg_str += obj.svg()
                elif isinstance(obj, RollingBall):
                    if obj.obj.rolling_ball.number == 0:
                        svg_str += """ <circle cx="%d" cy="%d" r="%d" fill="%s" id="cue_ball" />\n""" % (
                            obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[obj.obj.still_ball.number])
                    else:
                        svg_str += obj.svg()
                else:
                    svg_str += obj.svg()

        # svg_str += "<line id='cue_line' x1='675' y1='2025' x2='900' y2='2025' stroke='black' stroke-width='2' visibility='hidden' />"
        svg_str += FOOTER

        return svg_str

        
        
################################################################################
# Assignment 3: Creating SQL Database

class Database():
    def __init__(self, reset=False):
        self.db_path = "phylib.db"
        
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
            """CREATE TABLE IF NOT EXISTS TTable (
                TABLEID INTEGER PRIMARY KEY AUTOINCREMENT,
                TIME FLOAT NOT NULL
            );""",
            """CREATE TABLE IF NOT EXISTS Ball (
                BALLID  INTEGER PRIMARY KEY AUTOINCREMENT,
                BALLNO  INTEGER NOT NULL,
                XPOS    FLOAT NOT NULL,
                YPOS    FLOAT NOT NULL,
                XVEL    FLOAT,
                YVEL    FLOAT
            );""",
            """CREATE TABLE IF NOT EXISTS BallTable (
                TABLEID INTEGER NOT NULL,
                BALLID INTEGER NOT NULL,
                FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
                FOREIGN KEY (BALLID) REFERENCES Ball(BALLID)
            );""",
            """CREATE TABLE IF NOT EXISTS Shot (
                SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
                PLAYERID INTEGER NOT NULL,
                GAMEID INTEGER NOT NULL,
                FOREIGN KEY (PLAYERID) REFERENCES Player(PlayerID),
                FOREIGN KEY (GAMEID) REFERENCES Game(GameID)
            );""",
            """CREATE TABLE IF NOT EXISTS TableShot (
                TABLEID INTEGER NOT NULL,
                SHOTID INTEGER NOT NULL,
                FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
                FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID)
            );""",
            """CREATE TABLE IF NOT EXISTS Game (
                GAMEID INTEGER PRIMARY KEY AUTOINCREMENT,
                GAMENAME VARCHAR(64) NOT NULL
            );""",
            """CREATE TABLE IF NOT EXISTS Player (
                PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT,
                GAMEID INTEGER NOT NULL,
                PLAYERNAME VARCHAR(64) NOT NULL,
                FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
            );"""
        ]

        # Executing all commands
        for command in tables:
            cursor.execute(command)
        
        # Commit changes and close cursor
        self.conn.commit()
        cursor.close()
    
    def readTable(self, tableID):
        cursor = self.conn.cursor()
        
        # Increment tableID by 1 to match the SQL IDs
        new_tableID = tableID + 1

        # SQL query to retrieve Balls and Table time for a given tableID
        query = """
        SELECT b.BALLID, b.BALLNO, b.XPOS, b.YPOS, b.XVEL, b.YVEL, t.TIME
        FROM BallTable bt
        JOIN Ball b ON bt.BALLID = b.BALLID
        JOIN TTable t ON bt.TABLEID = t.TABLEID
        WHERE bt.TABLEID = ?
        """
        cursor.execute(query, (new_tableID,))
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
        self.conn.commit()
        return new_table
    def writeTable(self, table):
        # Step 1: Insert the time into TTable and get the new TABLEID
        self.conn.execute("INSERT INTO TTable (TIME) VALUES (?)", (table.time,))
        tableID = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Step 2: For ea ball on the table, insert into Ball and then into BallTable
        for ball in table:
            if isinstance(ball, StillBall): # StillBall condition
                xvel, yvel = 0, 0

                self.conn.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)",
                            (ball.obj.still_ball.number, ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y, xvel, yvel))

            elif isinstance(ball, RollingBall): # RollingBall condition
                xvel, yvel = ball.obj.rolling_ball.vel.x, ball.obj.rolling_ball.vel.y

                self.conn.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)",
                    (ball.obj.rolling_ball.number, ball.obj.rolling_ball.pos.x, ball.obj.rolling_ball.pos.y, xvel, yvel))

            else: # Skip if not a ball
                continue
            # # Insert the ball into Ball table
            ballID = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            
            # Link the ball to the table in BallTable
            self.conn.execute("INSERT INTO BallTable (TABLEID, BALLID) VALUES (?, ?)", (tableID, ballID))


        # Commit changes and return the adjusted TABLEID
        self.conn.commit()
        return tableID - 1  # Adjusting because SQL IDs start at 1, but we want to start at 0
    
    def getGame(self, gameID):
        
        # Ensure connection to the database is established
        conn = self.conn()
        cursor = conn.cursor()

        # SQL query to fetch gameName, and player names based on gameID
        # We assume that the two players for each game are the two lowest PLAYERID values associated with that GAMEID
        query = """
        SELECT g.GAMENAME, p1.PLAYERNAME as player1Name, p2.PLAYERNAME as player2Name
        FROM Game g
        JOIN Player p1 ON g.GAMEID = p1.GAMEID
        JOIN Player p2 ON g.GAMEID = p2.GAMEID AND p1.PLAYERID < p2.PLAYERID
        WHERE g.GAMEID = ?
        LIMIT 1;
        """

        try:
            cursor.execute(query, (gameID,))
            gameInfo = cursor.fetchone()
            if gameInfo:
                cursor.close()
                conn.commit()
                return gameInfo  # This returns a tuple: (gameName, player1Name, player2Name)
            else:
                cursor.close()
                conn.commit()
                return None
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            cursor.close()
            conn.commit()
            return None

    def setGame(self, gameName, player1Name, player2Name):
        cursor = self.conn.cursor()

        # Insert into the Game table
        game_insert_query = "INSERT INTO Game (GAMENAME) VALUES (?);"
        cursor.execute(game_insert_query, (gameName,))
        game_id = cursor.lastrowid  # Fetch the newly created gameID


        # Insert the first player (Player 1) into the Player table
        player_insert_query = "INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?);"
        cursor.execute(player_insert_query, (game_id, player1Name))
       
        # Insert the second player (Player 2) into the Player table
        cursor.execute(player_insert_query, (game_id, player2Name))

        # Commit the transactions if all insertions were successful
        self.conn.commit()
        cursor.close()

        return game_id  # Return the gameID

    def newShot(self, gameID, playerName):
        cursor = self.conn.cursor()

        playerID = self.getPlayerIDByName(playerName)
        cursor.execute('''INSERT INTO Shot (GAMEID, PLAYERID) VALUES (?, ?)''', (gameID, playerID))
        shotID = cursor.lastrowid
        self.conn.commit()
        cursor.close()
        return shotID
    
    def getPlayerIDByName(self, playerName):
        cursor = self.conn.cursor()  # Create a cursor from the connection
        cursor.execute("SELECT PLAYERID FROM Player WHERE PLAYERNAME = ?", (playerName,))
        result = cursor.fetchone()  # Fetch the result using the cursor
        cursor.close()  
        if result:
            return result[0]  # Return the playerID
        else:
            return None  # Return None if the player was not found

    def writeTableShot(self, tableID, shotID):

        self.conn.execute("INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?)", (tableID, shotID))
        self.conn.commit()
    
    def getLatestTableID(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(TABLEID) FROM TTable")
        tableID = cursor.fetchone()[0]

        cursor.close()
        return tableID - 1  # Adjusting because SQL IDs start at 1, but we want to start at 0

    def close(self):
        # Commit any pending transaction and close the connection
        self.conn.commit()
        self.conn.close()

################################################################################
class Game():
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        self.db = Database()
        self.db.createDB()
        
        if isinstance(gameID, int) and gameName is None and player1Name is None and player2Name is None:
            self.gameID = gameID

            gameInfo = self.db.getGame(gameID + 1)

            self.gameName = gameInfo[0]

            self.player1Name = gameInfo[1]
            self.player2Name = gameInfo[2]

        elif gameID is None and isinstance(gameName, str) and isinstance(player1Name, str) and isinstance(player2Name, str):
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name

            self.gameID = (self.db.setGame(gameName, player1Name, player2Name)) - 1
        else:
            raise TypeError("Invalid constructor usage.")

    def shoot(self,gameName, playerName, table, xvel, yvel):
        shotID = self.db.newShot(self.gameID, playerName)
        new_table = table.cueBall(table, xvel, yvel)
        table = new_table


        # Segment simulation loop
        beginning_table = table

        while True:
            # Directly use the table for simulation, updating its state
            segment_end_table = beginning_table.segment()

            if segment_end_table is None:
                # tableID = self.db.writeTable(table)
                # self.db.writeTableShot(tableID, shotID)
                break

            segment_duration = segment_end_table.time - beginning_table.time
            num_frames = math.floor(segment_duration / FRAME_INTERVAL)
            
            for frame in range(num_frames):  # Include the endpoint to ensure we capture the final state
                frame_time = frame * FRAME_INTERVAL
                new_table = beginning_table.roll(frame_time)
                
                new_table.time = frame_time + beginning_table.time
                
                # Record the current state of the table and the shot
                tableID = self.db.writeTable(new_table)
                self.db.writeTableShot(tableID, shotID) 

            beginning_table = segment_end_table
    

    




