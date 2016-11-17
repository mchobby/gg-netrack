#!/usr/bin/env python
# coding: utf-8

import psycopg2

class DB:
    def __init__( self, dbname, dbuser, dbhost, dbpasswd ):
        constr = "dbname='%s' user='%s' host='%s' password='%s'"
        self._conn = psycopg2.connect( constr % (dbname, dbuser, dbhost, dbpasswd) )

    def get_pending_ne( self ):
        """ The printed Send Notes that are not yet handled (or Waiting or aborded) """
        cur = self._conn.cursor()
        cur.execute( "select * from getOT_PendingNE()" )
        rows = cur.fetchall()
        del( cur )
        return rows

    def get_pickup_ne( self ):
        """ The send notes waiting on Pickup shelves """
        cur = self._conn.cursor()
        cur.execute( "select * from getOT_PickupNE()" )
        rows = cur.fetchall()
        del( cur )
        return rows

    def get_shipped_today_ne( self ):
        """ The Send Notes shipped today """
        cur = self._conn.cursor()
        cur.execute( "select * from getOT_ShippedTodayNE()" )
        rows = cur.fetchall()
        del( cur )
        return rows 

    def get_repres_shelves_ne( self ):
        """ The NE stored on the representative shelves (max 100) """
        cur = self._conn.cursor()
        cur.execute( "select * from getOT_RepresShelvesNE()" )
        rows = cur.fetchall()
        del( cur )
        return rows

    def get_preparing_ne( self ):
        """ The NE that are currently prepared """ 
        cur = self._conn.cursor()
        cur.execute( "select * from getOT_PreparingNE()" )
        rows = cur.fetchall()
        del( cur )
        return rows

    def get_tiny_stats( self ):
        """ Returns the Tiny Stats as a dict CODE=VALUE """
        cur = self._conn.cursor()
        cur.execute( "select * from gettinystat()" )
        rows = cur.fetchall()
        result = {}
        for row in rows:
            result[row[0]]=row[2] # TinyStat.code = TinyStat.value
        return result


