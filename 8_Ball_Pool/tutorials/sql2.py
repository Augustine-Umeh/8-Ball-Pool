import os;
import sqlite3;

def pp( listoftuples ):
    columns = len(listoftuples[0]);
    widths = [ max( [ len(str(item[col])) for item in listoftuples ] ) \
                                for col in range( columns ) ];

    fmt = " | ".join( ["%%-%ds"%width for width in widths] );
    for row in listoftuples:
        print( fmt % row );

# for testing only; remove this for real usage
if os.path.exists( 'test.db' ):
    os.remove( 'test.db' );

# create database file if it doesn't exist and connect to it
conn = sqlite3.connect( 'test.db' );

conn.execute( """CREATE TABLE AUTHORS ( 
             		AUTHORID   DECIMAL(3),
             		NAME       CHAR(40),
             		BIRTHYR    CHAR(4),
             		DEATHYR    CHAR(4),
             		PRIMARY KEY (AUTHORID) );""" );

conn.execute( """CREATE TABLE BOOKS ( 
           BOOKID       	DECIMAL(3),
           TITLE           	CHAR(30),
           AUTHORID  	DECIMAL(3),
           DATE            	CHAR(4),
           PAGES          	INTEGER,
           PRIMARY KEY (BOOKID),
           FOREIGN KEY (AUTHORID) REFERENCES AUTHORS );""" );


conn.execute( """INSERT INTO AUTHORS 
                    VALUES (100,'AUSTEN, JANE'    ,'1845','1880');""" );
conn.execute( """INSERT INTO AUTHORS 
                    VALUES (200,'BRONTE, EMILY'   ,'1830','1866');""" );
conn.execute( """INSERT INTO AUTHORS 
                    VALUES (300,'DICKENS, CHARLES','1840','1899');""" );

conn.execute( """INSERT INTO BOOKS
                    VALUES (123,'WUTHERING HEIGHTS'    ,200,'1865',550);""" );
conn.execute( """INSERT INTO BOOKS
                    VALUES (124,'OLIVER TWIST'         ,300,'1878',600);""" );
conn.execute( """INSERT INTO BOOKS
                    VALUES (220,'GREAT EXPECTATIONS'   ,300,'1880',900);""" );
conn.execute( """INSERT INTO BOOKS
                    VALUES (340,'MANSFIELD PARK'       ,100,'1875',1000);""" );
conn.execute( """INSERT INTO BOOKS
                    VALUES (490,'SENSE AND SENSIBILITY',100,'1873',980);""" );

#pp( conn.execute( """SELECT * FROM AUTHORS CROSS JOIN BOOKS;""" ).fetchall() );

print( 80*'*' );

pp( conn.execute( """SELECT * FROM AUTHORS INNER JOIN BOOKS
                        ON
                        BOOKS.AUTHORID=AUTHORS.AUTHORID;""" ).fetchall() );


print( 80*'*' );

pp( conn.execute( """SELECT AUTHORS.NAME,BOOKS.TITLE FROM AUTHORS,BOOKS 
                        WHERE (BOOKS.AUTHORID=AUTHORS.AUTHORID);""" ).fetchall() );

'''
print( 80*'*' );

pp( conn.execute( """SELECT * FROM AUTHORS, BOOKS
                        WHERE
                        ( BOOKS.AUTHORID=AUTHORS.AUTHORID
                            AND AUTHORS.AUTHORID=100 );""" ).fetchall() );

'''
