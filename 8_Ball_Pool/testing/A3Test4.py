import Physics;

def write_svg( table_id, table ):
    with open( "table%4.2f.svg" % table.time, "w" ) as fp:
        fp.write( table.svg() );

db = Physics.Database();

cur = db.conn.cursor();

# retreive all tables (regardless of shot)
cur.execute( """\
SELECT TABLEID FROM TableShot;""");
tableIDs = cur.fetchall();

# this should print a few hundered table IDs
print( len(tableIDs) );

# this should print the first 10 frames of the shot
# the cue ball starts at pos.y=2025.0, with a starting vel.y=-1000.0
# and moves about 10mm upwards each 0.01s while gradually slowing down
for i in range( 10 ):
    print( i, db.readTable( i ) );

# this should print 10 frames of the shot as the cue ball hits the racked balls
for i in range( 143, 153 ):
    print( i, db.readTable( i ) );

cur.close();
db.conn.commit();
db.conn.close();
