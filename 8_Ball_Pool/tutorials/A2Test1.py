import math
import Physics

# Call the Physics.Table constructor and store the result in a variable table.
table = Physics.Table()


# Call the Physics.Coordinate constructor and store the result in a variable pos.
# Compute the x and y values.
pos = Physics.Coordinate(0.0, 0.0)  # Initialize with default values



# Update the x and y values.
pos.x = Physics.TABLE_WIDTH / 2.0 - math.sqrt(Physics.BALL_DIAMETER * Physics.BALL_DIAMETER / 2.0)
pos.y = Physics.TABLE_WIDTH / 2.0 - math.sqrt(Physics.BALL_DIAMETER * Physics.BALL_DIAMETER / 2.0)



# Call the StillBall constructor and store the result in a variable sb.
sb = Physics.StillBall(1, pos)



# Compute the values for a rolling ball.
pos = Physics.Coordinate(0.0, 0.0)  # Initialize with default values
vel = Physics.Coordinate(0.0, 0.0)  # Initialize with default values
acc = Physics.Coordinate(0.0, 0.0)  # Initialize with default values



# Update the x and y values for pos.
pos.x = Physics.TABLE_WIDTH / 2.0
pos.y = Physics.TABLE_LENGTH - Physics.TABLE_WIDTH / 2.0



# Update the y value for vel.
vel.y = -1000.0  # 1m/s (medium speed)



# Update the y value for acc.
acc.y = 180.0



# Call the RollingBall constructor and store the result in a variable rb.
rb = Physics.RollingBall(0, pos, vel, acc)



# Add the StillBall to the table using "table += sb".
table += sb



# Add the RollingBall to the table using "table += rb".
table += rb



# Print the table.
print(table)



# Start a while loop conditioned on the value of table (it will run until table is None).
while table:
    # Inside the while loop set the value of table to be the return value of calling the segment method of table.
    table = table.segment()
    # Inside the while loop print the table.
    print(table)
