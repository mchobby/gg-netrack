#!/usr/bin/env python
# coding: utf-8
import curses
from time import sleep
from database import *
from config import *

REFRESH_TIME = 90

# Those values are copied from Stock.ch
NEACTION_EN_ATTENTE = 98
NEACTION_ANNULE = 99
NEACTION_PREPARATION = 10
NEACTION_VERIFOK = 11
NEACTION_COLIS = 15
NEACTION_EXPEDITION = 20
NEACTION_ENLEVEMENT = 21
NEACTION_REPRESENTANT = 22

NEACTION_EXP_PARTSEXPRESS = 23
NEACTION_EXP_GLS = 24
NEACTION_EXP_POSTE = 28
NEACTION_EXP_BPS = 30

NE_ACTION_REPRES_GAETAN = 25
NE_ACTION_REPRES_BRUNO = 26
NE_ACTION_REPRES_GUY = 27
NE_ACTION_REPRES_GREG = 29

NE_ACTION_CLOTURE = 80

def is_repres_neaction( value ):
    return value in (NEACTION_REPRES_GAETAN, NEACTION_REPRES_BRUNO, NEACTION_REPRES_GUY, NEACTION_REPRES_GREG )

def is_exp_neaction( value ):
    return value in (NEACTION_EXP_PARTSEXPRESS, NEACTION_EXP_GLS, NEACTION_EXP_POSTE, NEACTION_EXP_BPS )

def exp_neaction_code( value ):
    __code = { NEACTION_EXP_PARTSEXPRESS : 'PAR', NEACTION_EXP_GLS : 'GLS', NEACTION_EXP_POSTE : 'POS', NEACTION_EXP_BPS : 'BPS' }
    if is_exp_neaction( value ):
        return __code[value]
    else:
        return ''

class MyApp:
    def __init__( self, screen ):
        self.screen = screen
        (self.height, self.width) = screen.getmaxyx()
        self.subwin = [] # SubWin array
        self.create_subwin()
        
        self._c   = Config() # Configuration parser
        self._db  = DB( self._c.dbname, self._c.dbuser, self._c.dbhost, self._c.dbpasswd )
        self.data = {} # Storing the row sets (or reload_data) into a dictionnary

    def wshipped_redraw(self):
        """ redraw the subwin background """
        self.wshipped.clear()
        self.wshipped.border()
        self.wshipped.addstr( 0, 2, "[ Shipped ]" )

    def wpending_redraw(self):
        """ redraw the subwin background """
        self.wpending.clear()
        self.wpending.border()
        self.wpending.addstr( 0, 2, "[ Pending ]" )

    def wpickup_redraw(self):
        """ redraw the subwin background """
        self.wpickup.clear()
        self.wpickup.border()
        self.wpickup.addstr( 0, 2, "[ Pickup ]" )

    def create_subwin( self ):
        self.wpending = curses.newwin(self.height-1,20,0,0) # NLines, NCols, begin_y, begin_x
        self.wpending.border()
        self.wpending.addstr(0,2,"[ Pending ]")
        self.wpending.addstr(1,1,"%i , %i" % self.wpending.getmaxyx() )
        self.subwin.append( (self.wpending,self.wpending_redraw) )

        #self.wpreparing = curses.newwin(19,20,0,19)
        #self.wpreparing.border()
        #self.wpreparing.addstr(0,2,"[ Prepare ]")
        #self.subwin.append( self.wpreparing )

        self.wshipped = curses.newwin(16,self.width-self.wpending.getmaxyx()[1],0,self.wpending.getmaxyx()[1])
        self.wshipped_redraw()
        self.subwin.append( (self.wshipped,self.wshipped_redraw) )

        self.wpickup = curses.newwin( 
5,self.width-self.wpending.getmaxyx()[1], self.wshipped.getmaxyx()[0]-1, 
self.wpending.getmaxyx()[1] )
        self.wpickup_redraw()
        self.subwin.append( (self.wpickup,self.wpickup_redraw) )

        self.status = curses.newwin(2,self.width,self.height-1,0) # min 2 lines height!!!

    def reload_data( self ):
        # Reload the needed data to draw the screen.
        n = [('pending'  , self._db.get_pending_ne  ),
             ('preparing', self._db.get_preparing_ne),
             ('pickup'   , self._db.get_pickup_ne   ),
             ('shipped'  , self._db.get_shipped_today_ne),
             ('repres'   , self._db.get_repres_shelves_ne),
             ('tinystats', self._db.get_tiny_stats)]
        for key, func in n:
            if key  in self.data:
                del( self.data[key] )
            self.data[key] = func()

    def draw_screen( self ):      
        def fill_vertical( w, rows, f ): 
            """ fill out a vertical list 
                w: window to fill
                rows: the rows of data (properly ordered)
                f : lambda row, return a string to display for the row
            """
            hclient = w.getmaxyx()[0] - 2 # Height of the client area
            wclient = w.getmaxyx()[1] - 2
            # max data width
            max_data_width = 0
            for row in rows:
                if len( f(row) ) > max_data_width:
                    max_data_width = len( f(row) )

            # Zip a counter with the rows
            r = zip( range(len(rows)), rows ) # Zip a counter with the row
            
            #for icurrent, row in r:
            #    if icurrent+1 < hclient:
            #        sdata = f( row ) # call lambda to have the string to display
            #        w.addstr( icurrent+1, 1, sdata )
            #    else:
            #        break
            for icurrent, row in r:
                (_line,_col)=(icurrent%hclient, icurrent//hclient)
                if (_col+1)*(max_data_width+1) > wclient:
                    break
                sdata = f(row)
                w.addstr( _line+1, _col*(max_data_width+1)+1, sdata )

        # Drawing pending
        # Client (NNE)S (S:* for special status, >> for EXP)
        def __pending_caption(row):
            _shipinfo = '-->' if row[4].upper() == 'EXP' else row[4][0:3].lower()
            if row[0] == NEACTION_PREPARATION:
              state = '(%3s)' % _shipinfo
            elif row[0] == NEACTION_EN_ATTENTE:
              state = 'w%3s ' % _shipinfo
            else:
              state = ' %3s ' % _shipinfo
            return ' %s %4s-%s' % (state, row[2],row[3].split('/')[0] )

        def pending_sorting( row ):
             # Order by NNE (desc)
             if (row[0] == None) or (row[0] == NEACTION_PREPARATION): 
                 return int(row[3].split('/')[0])*1
             else:
                 # Reject other status at the end (except preparation)
                 return int(row[3].split('/')[0])*-1

        pendings = sorted( self.data['pending']+self.data['preparing'], key=pending_sorting, reverse=True )
        self.wpending_redraw()
        fill_vertical( self.wpending, pendings, __pending_caption ) 
        
        # Drawing preparing
        #def __preparing_caption(row):
        #    if row[4].upper() == 'EXP':
        #       state = '>>>'
        #    else:
        #       state = row[4][0:3].lower()
        #    return ' %s %4s-%s' % (state, row[2],row[3].split('/')[0] )
        #fill_vertical( self.wpreparing, self.data['preparing'], __preparing_caption )

        # Drawing the shipped 
        def __shipping_caption(row):
            exp = exp_neaction_code( row[0] )
            return ' %4s-%s %s' % ( row[2],row[3].split('/')[0], exp )

        def __shipping_sorting(row):
            # Keep number only
            _client = '0'
            for c in row[2]:
                if c.isdigit():
                    _client = _client+c
            # id_client + Numerical part of NNEtxt (50320/1)
            return int(_client)*1000000+int(row[3].split('/')[0])
        self.wshipped_redraw()
        fill_vertical( self.wshipped, sorted( self.data['shipped'], key=__shipping_sorting) , __shipping_caption )

      
        def __pickup_caption( row ):
            # Client Nbr , 3 last char of NNE number
            #   return '%4s-%s' % (row[2], row[3].split('/')[0][-3:]) 
            # Just return the customer number
            return '%4s' % (row[2]) 
        def __pickup_sorting( row ):
            # Keep number only
            _client = '0'
            for c in row[2]:
                if c.isdigit():
                    _client = _client + c
            # id_client + numerical part of the NE (50320/1)
            return int( _client ) * 1000000 + int( row[3].split('/')[0] )
        self.wpickup_redraw()
        fill_vertical( self.wpickup, sorted( self.data['pickup'], key=__pickup_sorting ) , __pickup_caption )

        # Update the whole screen 
        for win, redraw  in self.subwin:
            win.refresh()

    def draw_status( self, refresh_time ):
        self.status.addstr( 0, 0, " "*self.width, curses.A_REVERSE )
        self.status.addstr( 0, 1, '%1d:%02d' % (refresh_time//60,refresh_time%60), curses.A_REVERSE )

        _tinystat = self.data['tinystats']
        _s = "| #Cmd: %03d | #NE-a-prep: %02d | NE Charge: %03d | #Boites: %d" % ( _tinystat['CMDCOUNT'], _tinystat['NEPREPCOUNT'], _tinystat['NEWORKLOAD'],_tinystat['BOXCOUNT']) 
        self.status.addstr( 0, 8, _s, curses.A_REVERSE )

    def run( self ):
        while True:
            # Start a new refresh time @ 90 sec
            _refresh_sec = REFRESH_TIME 
            self.reload_data()
            self.screen.clear()
            self.draw_screen()

            # Redraw the screen
            while _refresh_sec > 0:
                self.draw_status( _refresh_sec )
                self.status.refresh()
                sleep(1)
                _refresh_sec -= 1

def main(screen):
    curses.curs_set( 0 ) # Not visible
    curses.start_color()
    app = MyApp( screen )
    app.run()

if __name__ == '__main__':
    curses.wrapper(main)
