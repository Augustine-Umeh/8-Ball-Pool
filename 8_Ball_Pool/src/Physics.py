import phylib
import math

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg id="table" width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />"""

FOOTER = """</svg>\n"""

################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER

HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH

SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON

DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME

MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS

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
    ]



################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass


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
                                       0.0, 0.0 )
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall

    # add an svg method here
    def svg(self):
        if self.obj.still_ball.number < 9:
            return """ <circle class="ball" cx="%d" cy="%d" r="%d" fill="%s" />
                <circle cx="%d" cy="%d" r="%d" fill="%s" />
                <text x="%d" y="%d" font-family="Arial" font-size="23" fill="black" text-anchor="middle" dominant-baseline="middle">%d</text>/>\n""" % (
                self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number],
                self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS // 2,  BALL_COLOURS[0],
                self.obj.still_ball.pos.x, self.obj.still_ball.pos.y + 2, self.obj.still_ball.number
                )
        else:
            return """ <g class="ball">
                <circle cx="%d" cy="%d" r="%d" fill="%s" />
                <circle cx="%d" cy="%d" r="%d" fill="%s" />
                <rect x="%d" y="%d" width="56" height="16" fill="white" />
                <text x="%d" y="%d" font-family="Arial" font-size="23" fill="black" text-anchor="middle" dominant-baseline="middle">%d</text>
                </g>\n""" % (
                self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number], 
                self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, 15,  BALL_COLOURS[0],
                self.obj.still_ball.pos.x - 28, self.obj.still_ball.pos.y - 9, 
                self.obj.still_ball.pos.x, self.obj.still_ball.pos.y + 2, self.obj.still_ball.number
                )


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
                                       0.0, 0.0 )
      
        # this converts the phylib_object into a Rolling class
        self.__class__ = RollingBall

    # add an svg method here
    def svg(self):
        if self.obj.rolling_ball.number < 9:
            return """ <circle class="ball" cx="%d" cy="%d" r="%d" fill="%s" />
                <circle cx="%d" cy="%d" r="%d" fill="%s" />
                <text x="%d" y="%d" font-family="Arial" font-size="23" fill="black" text-anchor="middle" dominant-baseline="middle">%d</text>/>
                \n""" % (
                self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number],
                self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS // 2,  BALL_COLOURS[0],
                self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y + 2, self.obj.rolling_ball.number
                )
        else:
            return """ <g class="ball">
                <circle cx="%d" cy="%d" r="%d" fill="%s" />
                <circle cx="%d" cy="%d" r="%d" fill="%s" />
                <rect x="%d" y="%d" width="56" height="16" fill="white" />
                <text x="%d" y="%d" font-family="Arial" font-size="23" fill="black" text-anchor="middle" dominant-baseline="middle">%d</text>
                </g>\n""" % (
                self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number], 
                self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, 15,  BALL_COLOURS[0],
                self.obj.rolling_ball.pos.x - 28, self.obj.rolling_ball.pos.y - 9, 
                self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y + 2, self.obj.rolling_ball.number
                )


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
                                       0.0, 0.0 )
      
        # this converts the phylib_object into a Hole class
        self.__class__ = Hole


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
                                       None, None, None, 
                                       0.0, y)
      
        # this converts the phylib_object into a Rolling class
        self.__class__ = HCushion

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
                                       x, 0.0)
      
        # this converts the phylib_object into a Rolling class
        self.__class__ = VCushion

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
        phylib.phylib_table.__init__( self )
        self.current = -1

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other )
        return self

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ] # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1    # reset the index counter
        raise StopIteration  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ) 
        if result==None:
            return None
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion
        return result

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = ""    # create empty string
        result += "time = %6.1f\n" % self.time    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj)  # append object description
        return result  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self )
        if result:
            result.__class__ = Table
            result.current = -1
        return result

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
                new_ball = RollingBall(ball.obj.rolling_ball.number, Coordinate(0,0), Coordinate(0,0),
                                        Coordinate(0,0))
                
                phylib.phylib_roll(new_ball, ball, t)
                
                # Add ball to table
                new_table += new_ball
            if isinstance(ball, StillBall):
                # Create a new ball with the same number and pos as the old ball
                new_ball = StillBall(ball.obj.still_ball.number,
                                    Coordinate(ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y))
                # Add ball to table
                new_table += new_ball
                
        # Return table
        return new_table

    def cueBall(self, table, xvel, yvel):
        new = Table()
        
        for ball in table:
            if isinstance( ball, RollingBall ):
                new += ball
            elif isinstance( ball, StillBall ):
                if ball.obj.still_ball.number == 0:
                    # Turn this into rolling and calc acc
                    xpos, ypos = ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y
            
                    cue_ball_pos = Coordinate(xpos, ypos)
                    cue_ball_vel = Coordinate(xvel, yvel)

                    # Calculating acceleration
                    cue_ball_speed = math.sqrt((xvel * xvel) + (yvel * yvel))

                    if (cue_ball_speed > VEL_EPSILON):
                        x_cord = -((xvel/cue_ball_speed) * phylib.PHYLIB_DRAG)
                        y_cord = -((yvel/cue_ball_speed) * phylib.PHYLIB_DRAG)
                        
                        cue_ball_acc = Coordinate( x_cord, y_cord )
                    else:
                        cue_ball_acc = Coordinate ( 0.0, 0.0 )
                    
                    cue_ball = RollingBall( 0,
                        cue_ball_pos,
                        cue_ball_vel,
                        cue_ball_acc )

                    new += cue_ball
                else:
                    new += ball
        return new
    
    def initializeTable(self, table):
        table += StillBall(0, Coordinate(675, 2025))
        table += StillBall(1, Coordinate(675, 640))
        table += StillBall(2, Coordinate(645, 580))
        table += StillBall(3, Coordinate(705, 580))
        table += StillBall(4, Coordinate(615, 520))
        table += StillBall(5, Coordinate(675, 520))
        table += StillBall(6, Coordinate(735,520))
        table += StillBall(7, Coordinate(585,460))
        table += StillBall(8, Coordinate(645,460))
        table += StillBall(9, Coordinate(705, 460))
        table += StillBall(10, Coordinate(765, 460))
        table += StillBall(11, Coordinate(555, 400))
        table += StillBall(12, Coordinate(615, 400))
        table += StillBall(13, Coordinate(675, 400))
        table += StillBall(14, Coordinate(735, 400))
        table += StillBall(15, Coordinate(795, 400))
        # return table.custom_svg(table)
        return table

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

        svg_str += FOOTER
        return svg_str
