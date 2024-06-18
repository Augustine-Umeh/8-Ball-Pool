import os;
import sqlite3;

# for testing only; remove this for real usage
if os.path.exists( 'test.db' ):
    os.remove( 'test.db' );

# create database file if it doesn't exist and connect to it
conn = sqlite3.connect( 'test.db' );

cur = conn.cursor();
#cur = conn.cursor( dictionary=True ); # MYSQL only

cur.execute( """CREATE TABLE S 
                 ( SNO     CHAR(5),
                   SNAME   CHAR(20),
                   STATUS  DECIMAL(3),
                   CITY    CHAR(15),
                   PRIMARY KEY (SNO) );""" );


cur.execute( """CREATE TABLE P
                 ( PNO     CHAR(5),
                   PNAME   CHAR(20),
                   COLOUR  CHAR(20),
                   WEIGHT  DECIMAL(3),
                   CITY    CHAR(15),
                   PRIMARY KEY (PNO) );""" );

cur.execute( """CREATE TABLE SP 
                 ( SNO     CHAR(5),
                   PNO     CHAR(5),
                   QTY     DECIMAL(5),
                   PRIMARY KEY (SNO,PNO),
                   FOREIGN KEY (SNO) REFERENCES S,
                   FOREIGN KEY (PNO) REFERENCES P );""" );


cur.execute( """INSERT
                 INTO   S  ( SNO,  SNAME,   STATUS, CITY     )
                 VALUES    ( 'S1', 'Smith', 20,     'London' );""" );

#cur.execute( """INSERT
#                 INTO   S  ( SNO,  SNAME,   STATUS, CITY     )
#                 VALUES    ( 'S1', 'Adams', 22,     'Guelph' );""" );

cur.execute( """INSERT
                 INTO   S  ( SNO,  SNAME,   STATUS, CITY    )
                 VALUES    ( 'S2', 'Jones', 10,     'Paris' );""" );

cur.execute( """INSERT
                 INTO   S  ( SNO,  SNAME,   STATUS, CITY    )
                 VALUES    ( 'S3', 'Blake', 30,     'Paris' );""" );

cur.execute( """INSERT
                 INTO   S  ( SNO,  SNAME,   STATUS, CITY    )
                 VALUES    ( 'S4', 'Clark', 20,     'Paris' );""" );

cur.execute( """INSERT
                 INTO   SP ( SNO,  PNO,  QTY )
                 VALUES    ( 'S4', 'P1', 1000 );""" );

#data = cur.execute( """SELECT * FROM S;""" );
#print( data.fetchone() );
#print( data.fetchone() );
#print( data.fetchone() );
#print( data.fetchone() );
#print( data.fetchone() );

#print( data.fetchall() );

#print( data.fetchone() );
#print( data.fetchone() );
#print( data.fetchone() );
#for row in data.fetchall():
#   print( row );

#print( data.fetchone() );
#print( data.fetchone() );
#print( data.fetchone() );
#print( data.fetchone() );
#print( data.fetchone() );


# see all the tables
#data = cur.execute( """SELECT name FROM sqlite_master WHERE type='table';""" );
#print( data.fetchall() );

data = cur.execute( """SELECT * FROM sqlite_master;""" );
print( data.fetchone() );
cur.close();
conn.commit();
conn.close();
