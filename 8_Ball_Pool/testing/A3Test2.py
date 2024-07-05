import Physics;

def write_svg( table_id, table ):
    with open( "table%02d.svg" % table_id, "w" ) as fp:
        fp.write( table.svg() );

db = Physics.Database();

table_id = 0;
table = db.readTable( table_id );

write_svg( table_id, table );

while table:
    table_id += 1;
    table = db.readTable( table_id );
    if not table:
        break;
    write_svg( table_id, table );

db.close();
