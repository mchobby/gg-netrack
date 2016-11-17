from ConfigParser import ConfigParser

class Config:
    def __init__( self, inifilename='netrack.ini' ):
        """ Read the configuration file and set the various property on the class """
        self._c = ConfigParser()
        self._c.read( inifilename )
        
        self.read_config()

    def read_config(self):
        self.dbname = self._c.get( 'DB', 'dbname' )
        self.dbuser = self._c.get( 'DB', 'dbuser' )
        self.dbhost = self._c.get( 'DB', 'dbhost' )
        self.dbpasswd = self._c.get( 'DB', 'dbpasswd' )

       

