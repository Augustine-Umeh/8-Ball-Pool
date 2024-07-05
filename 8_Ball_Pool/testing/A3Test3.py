import math;
import random;

import Physics;

def nudge():
    return random.uniform( -1.5, 1.5 );

table = Physics.Table();

# 1 ball
pos = Physics.Coordinate( 
                Physics.TABLE_WIDTH / 2.0,
                Physics.TABLE_WIDTH / 2.0,
                );

sb = Physics.StillBall( 1, pos );
table += sb;

# 2 ball
pos = Physics.Coordinate(
                Physics.TABLE_WIDTH/2.0 - (Physics.BALL_DIAMETER+4.0)/2.0 +
                nudge(),
                Physics.TABLE_WIDTH/2.0 - 
                math.sqrt(3.0)/2.0*(Physics.BALL_DIAMETER+4.0) +
                nudge()
                );
sb = Physics.StillBall( 2, pos );
table += sb;

# 3 ball
pos = Physics.Coordinate(
                Physics.TABLE_WIDTH/2.0 + (Physics.BALL_DIAMETER+4.0)/2.0 +
                nudge(),
                Physics.TABLE_WIDTH/2.0 - 
                math.sqrt(3.0)/2.0*(Physics.BALL_DIAMETER+4.0) +
                nudge()
                );
sb = Physics.StillBall( 3, pos );
table += sb;

# cue ball also still
pos = Physics.Coordinate( Physics.TABLE_WIDTH/2.0 + random.uniform( -3.0, 3.0 ),
                          Physics.TABLE_LENGTH - Physics.TABLE_WIDTH/2.0 );
sb  = Physics.StillBall( 0, pos );

table += sb;


game = Physics.Game( gameName="Game 01", player1Name="Stefan", player2Name="Efren Reyes" );

game.shoot( "Game 01", "Stefan", table, 0.0, -1000.0 );
