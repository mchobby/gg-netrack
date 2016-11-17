#!/usr/bin/env python
# coding: utf-8

"""db-test.py: just test the database connectivity and queries"""

from config import *
from database import *

def main():
    print('Reading Config...')
    c = Config()
    print('Connect database %s' % c.dbname )
    db = DB( c.dbname, c.dbuser, c.dbhost, c.dbpasswd )
    print('NE Pending for preparation')
    print( '   %i' % len( db.get_pending_ne() ) )
    print('NE under preparation')
    print( '   %i' % len( db.get_preparing_ne() ) )
    print('NE at pickup location')
    print( '   %i' % len( db.get_pickup_ne() ) )
    print('NE shipped today' )
    print( '   %i' % len( db.get_shipped_today_ne() ) )
    print('NE at representative shelves' )
    print( '   %i' % len( db.get_repres_shelves_ne() ) )
    print( '-'*40 )
    print( '   Pending NE for Preparation ' )
    print( '-'*40 )
    for row in db.get_pending_ne():
        print( row )


if __name__ == '__main__':
    main()
