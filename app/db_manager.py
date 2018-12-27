# System inports
import pymysql
pymysql.install_as_MySQLdb()
import re
import os
import csv
from collections import OrderedDict
import flask
import datetime

# Local imports
from . import music_manager
from . import xmlconf
from . import auth_manager

##############################################################################
# This class is used to deal with all querying and updating
# to the  database for a particular user using a
# single connection and cursor to the database
##############################################################################
class DBQuery:
    """General class that allows you to Query the database and as data is fetched from the database, an 
    internal data structure acts like a cache and as data is accessed it is stored in this data structure """
    

    ##########################################################################
    # self.conn is MySQL connection object to the sys_config database
    # self.cursor is the handler to the sys_config database
    # self.username is the user who is responsible for the database connection
    #
    # close() should be called when an instance of this class is done with in
    # order to cleanly kill of the connection with the sys_config database
    ###########################################################################
    def __init__(self, user=None):
        self.conn = None
        self.cursor = None
        self._user = user
        self.connect()

    ###########################################################################
    # This method connects to the database as a high user who has read
    # and write privileges by using information in a config file on
    # arlene to do the binding.
    #
    # After this method is called the instance variables self.conn and
    # self.cursor of this class should be initialized and ready to be used.
    ###########################################################################
    def connect(self):
        try:
            curr_hosts,curr_user,curr_passwd,curr_db = ('','','','')
            curr_hosts = xmlconf.getConfValue('vowr.conf', 'mysql_hosts')
            curr_user = xmlconf.getConfValue('vowr.conf', 'mysql_user')[0]
            curr_db = xmlconf.getConfValue('vowr.conf', 'database')[0]
            curr_passwd = xmlconf.getConfValue('vowr.conf', 'mysql_pw')[0]
        except:
            raise AssertionError("Could not retrieve DB config from XML file.")

        if (curr_user == None or curr_passwd == None or curr_db == None or curr_hosts == None):
            raise AssertionError("Config file did not have all required "
                + "connection info")

        if len(curr_hosts) == 0:
            raise AssertionError("Config file did not specify db hosts")

        self.conn = None
        self.cursor = None
        # self.username = curr_user
        
        # Connect to the first available server in the list
        # Note that on the computer that hosts the web tools that
        # manage the master database the configuration file must
        # contain only the master database host name along with the
        # password and username of the database administrator so that
        # the webtool programs can connect and make changes as necessary.
        for host in curr_hosts:
            try:
                self.conn = pymysql.connect(host=host, user=curr_user,
                			passwd=curr_passwd, db=curr_db)
                self.cursor = self.conn.cursor()
                break
            except pymysql.Error:
                if self.conn != None:
                	self.conn.close()
                self.conn = None
                continue
        # End for

        if self.cursor == None:
            if self.conn != None:
                self.conn.close()
            raise pymysql.Error("MySQL Connection Error")
    # End self.connect()

    ###########################################################################
    # Closes the connection to the sys_config database used by the given
    # instance of this class.
    ###########################################################################
    def close(self):
        if self.cursor != None:
            self.cursor.close()
        if self.conn != None:
            self.conn.close()

    def __del__(self):
        self.close()

    ################################################################
    # Returns a list of all possible entity types.
    #
    # Returns:
    #   ent_types a list of all possible entity types
    ################################################################
    # def get_ent_types(self):
    #     ent_types = []
    #     try:
    #         self.cursor.execute("DESCRIBE entity")
    #         results = self.cursor.fetchall()
    #         for row in results:
    #             if row[0] == 'type':
    #             	raw_ent_types = row[1]
    #             	raw_ent_types = raw_ent_types[5:-1]
    #             	raw_ent_types = re.sub("'","",raw_ent_types)
    #             	ent_types = raw_ent_types.split(',')
    #     except Exception as e:
    #         raise Exception("Error retrieving entity types: " + str(e))
    #     for index in range(0,len(ent_types)):
    #         if ent_types[index] == 'association':
    #             del ent_types[index]
    #             break
    #     return ent_types
    #End get_ent_types()
    
    
    ######################################################################
    # Returns a list of all used variable values in the ent_var_vals
    # table for the given variable of the given entity type.
    #
    # Parameters:
    #	ent_type the entity type of the given variable to search for all
    #		used variable values for
    #	var the variable of the given entity type to search for all used
    #		variable values for
    #
    # Returns:
    #	used_var_vals a list of all used variable values in the
    #		ent_var_vals table for the given variable of the given
    #		entity type
    #######################################################################
    def FindMatchingEntities(self,ent_type,pairs):
        """
           ###
           # Find all entities that match the entity type and pairs,
           # pairs is a python dictionary of key:value pairs that correspond
           # to variables and their values
           ###
        """
        entities = None
        for var in pairs.keys():
            try:
                self.cursor.execute("""
                        SELECT DISTINCT entity.name
                        FROM entity,ent_var_vals
                        WHERE entity.type=%s AND entity.ent_id=ent_var_vals.ent_id
                        AND ent_var_vals.var=%s AND ent_var_vals.val=%s
                        """
                        , (ent_type,var,pairs[var]))
                res = self.cursor.fetchall()
            except pymysql.Error as e:
                raise pymysql.Error("MySQL Error retrieving all values of variable '"
                                                        + str(var) + "' for entity type '"
                                                        + str(ent_type) + "': " + e.args[1])
            except Exception as e:
                raise Exception("MySQL Error retrieving all values of variable '"  + str(e) + "'")

            newEntities = {}
            for row in res:
                if (entities == None) or entities.haskey(row[0]):
                    newEntities[row[0]] = 1
            # End for
            entities = newEntities
        # End for
        return entities.keys()
    # Ens FindMatchingEntities()

    # def get_all_used_var_vals(self, ent_type, var):
    #     try:
    #         self.cursor.execute("""
    #             SELECT DISTINCT ent_var_vals.val
    #             FROM entity,ent_var_vals
    #             WHERE entity.type=%s AND entity.ent_id=ent_var_vals.ent_id
    #             AND ent_var_vals.var=%s
    #             """
    #             , (ent_type,var))
    #         res = self.cursor.fetchall()
    #     except pymysql.Error as e:
    #         raise pymysql.Error("MySQL Error retrieving all values of variable '"
    #             				+ str(var) + "' for entity type '"
    #             				+ str(ent_type) + "': " + e.args[1])
    #     except Exception as e:
    #         raise Exception("MySQL Error retrieving all values of variable '"
    #             				+ str(var) + "' for entity type '"
    #             				+ str(ent_type) + "': " + e.args[1])
    #     used_var_vals = []
    #     for val_row in res:
    #         used_var_vals.append(val_row[0])
    #     used_var_vals.sort(key=str.lower)
    #     return used_var_vals
    # # End get_all_used_var_vals()
        
        
    #################################################################
    # Returns a list of the variable value for the given entity name
    # of the given entity type for the given variable, or an empty
    # list, i.e. [], if the variable doesn't exist for the entity
    #
    # Parameters:
    #	ent_type the entity type of the given entity name to get
    #		the given variable values for
    #	ent_name the entity name of the given entity type to get
    #		the given variable values for
    #	var the variable to get the variable values for the given
    #		entity name of the given entity type for
    #
    # Returns:
    #	val_list a list of all the variable value for the given
    #		variable for the given entity_type of the given entity
    #		name, or an empty list, i.e. [], if the variable doesn't
    #		exist for the entity
    #################################################################
    def GetEntityVarVals(self, ent_name, ent_type, var):
        try:
            self.cursor.execute("""
                SELECT val FROM ent_var_vals,entity
                WHERE name=%s AND type=%s AND status='active'
                AND ent_var_vals.ent_id=entity.ent_id
                AND ent_var_vals.var=%s ORDER BY indx
                """
                , (ent_name,ent_type,var))
            res = self.cursor.fetchall()
        except pymysql.Error as e:
            raise pymysql.Error("MySQL Error retrieving " + str(var)
                	+ " value for host " + str(ent_name) + ": "
                	+ e.args[1])
        except Exception as e:
            raise Exception("Error retrieving " + str(var) 
                	+ " value for host " + str(ent_name) + ": "
                	+ str(e))
        val_list = []
        for val_row in res:
            val_list.append(val_row[0])
        return val_list
    # End GetEntityVarVals()


    ####################################################################
    # Returns a list of all the (variable,value) pairs as size 2
    # tuples for the given entity name of the given entity type.
    #
    # Parameters:
    #	ent_type the entity type of the given entity name to get
    #		all (variable,value) pairs for
    #	ent_name the entity name of the given entity type to get
    #		all (variable,value) pairs for
    #
    # Returns:
    #	var_val_list a list of all the (variable,value) pairs as size 2
    #		tuples for the given entity name of the given entity type,
    #		this is an empty list if no such pairs exist
    ####################################################################
    # def get_ent_all_var_vals(self,ent_type,ent_name):
    #     try:
    #         self.cursor.execute("""
    #             SELECT var,val
    #             FROM ent_var_vals,entity
    #             WHERE ent_var_vals.ent_id=entity.ent_id
    #             AND entity.type=%s AND entity.name=%s
    #             ORDER BY var,val, indx
    #             """
    #             , (ent_type,ent_name))
    #         var_val_list = self.cursor.fetchall()
    #     except Exception as e:
    #         raise Exception("Failed to get all variable/values for entity '"
    #             			+ ent_name + "' of type '" + ent_type + "':"
    #             			+ str(e))
    #     return var_val_list
    # # End get_ent_all_var_vals()

    ###########################################################################
    # Set up an associative array of all variable values for a particular
    # entity of a particular type.
    #
    # Parameters:
    #	ent_type the entity type of the entity to get all (variable,value)
    #		pairs for
    #	ent_name the entity name of the entity to get all (variable,value)
    #		pairs for
    #
    # Returns:
    #	table: an associative array of all variables as key and values as a list
    #       of values for the given entity name of the given entity type
    ###########################################################################
    def get_ent_vals_table(self, ent_type, ent_name):
        try:
            self.cursor.execute("""
                SELECT var, val
                FROM entity, ent_var_vals 
                WHERE type='%s' and name='%s' and entity.ent_id=ent_var_vals.ent_id 
                """
                % (ent_type, ent_name))
            res = self.cursor.fetchall()
        except Exception as e:
            raise Exception("Error retrieving all entity variable values for '" +
                			ent_name + "' of type '" + ent_type +
                			"': " + str(e))
        table = {}
        for item in res:
            val = item[1]
            while val.rfind('"') != -1:
                val = str.replace(val,'"','&quot;')
            if item[0] in table:
                table[item[0]].append(val)
            else:
                table[item[0]] = [val]
        return table
    # End get_ent_vals_table()


    def createTables(self):
        tables = [
            ['users','''CREATE TABLE `users`(`id` INT AUTO_INCREMENT PRIMARY KEY,
                    `username` VARCHAR(32) NOT NULL,
                    UNIQUE(`username`),
                    `passhash` CHAR(130) DEFAULT NULL,
                    `admin` BIT(1) NOT NULL DEFAULT 0,
                    `master` BIT(1) NOT NULL DEFAULT 0,
                    `active` BIT(1) NOT NULL DEFAULT 1,
                    `lockout_count` INT DEFAULT 0,
                    `sec_q` VARCHAR(255) DEFAULT NULL,
                    `sec_a` VARCHAR(255) DEFAULT NULL
                    )'''],
            ['user_logins','''CREATE TABLE `user_logins`(`id` INT AUTO_INCREMENT PRIMARY KEY,
                    `user` INT NOT NULL,
                    FOREIGN KEY (`user`) REFERENCES `users`(`id`),
                    `remote_ip` VARCHAR(45) NOT NULL,
                    `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )'''],
            ['artists','''CREATE TABLE `artists`(`id` INT AUTO_INCREMENT PRIMARY KEY,
                    `name` VARCHAR(255) NOT NULL,
                    UNIQUE(`name`),
                    FULLTEXT(`name`)
                    )'''],
            ['albums','''CREATE TABLE `albums`(`id` INT AUTO_INCREMENT PRIMARY KEY,
                    `alb_num` VARCHAR(10) NOT NULL,
                    UNIQUE(`alb_num`),
                    `artist_id` INT,
                    FULLTEXT(`alb_num`),
                    `name` VARCHAR(255) DEFAULT NULL,
                    FOREIGN KEY (`artist_id`) REFERENCES `artists`(`id`)
                    )'''],
            ['songs','''CREATE TABLE `songs`(`id` INT AUTO_INCREMENT PRIMARY KEY,
                    `song_title` VARCHAR(255) NOT NULL,
                    `artist_id` INT DEFAULT NULL,
                    `album_id` INT DEFAULT NULL,
                    `media` VARCHAR(10) DEFAULT NULL,
                    `category` VARCHAR(75) DEFAULT NULL,
                    `theme` VARCHAR(75) DEFAULT NULL,
                    `side` INT NOT NULL,
                    `track` INT NOT NULL,
                    `performance_type` VARCHAR(255) DEFAULT NULL,
                    `canadian` BIT(1) NOT NULL DEFAULT 0,
                    `display` BIT(1) NOT NULL DEFAULT 1,
                    `deleted_by_id` INT DEFAULT NULL,
                    `deletion_date` DATETIME DEFAULT NULL,
                    FULLTEXT(`song_title`),
                    FULLTEXT(`category`),
                    FOREIGN KEY (`album_id`) REFERENCES `albums`(`id`),
                    FOREIGN KEY (`artist_id`) REFERENCES `artists`(`id`) 
                    )'''],
            ['playlists','''CREATE TABLE `playlists`(`id` INT AUTO_INCREMENT PRIMARY KEY,
                    `user_id` INT NOT NULL,
                    `name` VARCHAR(255) NOT NULL,
                    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
                    UNIQUE `user_playlist_comb`(`user_id`, `name`)
                    )'''],
            ['playlist_songs','''CREATE TABLE `playlist_songs`(`id` INT AUTO_INCREMENT PRIMARY KEY,
                    `playlist_id` INT NOT NULL,
                    `song_id` INT NOT NULL,
                    UNIQUE(`song_id`),
                    `position` INT NOT NULL,
                    UNIQUE `song_index`(`playlist_id`, `position`),
                    FOREIGN KEY (`playlist_id`) REFERENCES `playlists`(`id`),
                    FOREIGN KEY (`song_id`) REFERENCES `songs`(`id`)
                    )''']
        ]
        try:
            self.cursor.execute('''
            SHOW TABLES
            ''')
            existingTables = self.cursor.fetchall()
        except Exception as e:
            raise Exception("Failed to get all tables: " + str(e))
        existingTables = [row[0] for row in existingTables]
        for table in tables:
            # We will assume that if the table exists then it is in the right format
            if table[0] not in existingTables:
                try:
                    print('Creating table: ' + table[0])
                    self.cursor.execute(table[1])
                except Exception as e:
                    raise Exception("Failed to create table: " + table[0] + ", " + str(e))
        self.conn.commit()            

    def autocomplete(self, var, val):
        LIMIT = 10
        val = self.conn.escape_string(val)
        val = ' '.join(['+' + x + '*' for x in re.findall(r'[a-zA-Z0-9]+', val)])
        # val = ' '.join(['+(' + x + ' ' + x + '*)' for x in re.findall(r'[a-zA-Z0-9]+', val)])
        if var == 'artist_name':
            # query = "SELECT country FROM countries WHERE MATCH (country) AGAINST ('" + val + "' IN BOOLEAN MODE) LIMIT " + str(LIMIT) # Testing with country DB
            self.cursor.execute("SELECT DISTINCT name FROM artists WHERE MATCH (name) AGAINST (%s IN BOOLEAN MODE) LIMIT %s", (val, LIMIT))
        elif var == 'album_num':
            self.cursor.execute("SELECT DISTINCT alb_num FROM albums WHERE MATCH (alb_num) AGAINST (%s IN BOOLEAN MODE) LIMIT %s", (val, LIMIT))
        elif var == 'song_title':
            self.cursor.execute("SELECT DISTINCT song_title FROM songs WHERE display = 1 AND MATCH (song_title) AGAINST (%s IN BOOLEAN MODE) LIMIT %s", (val, LIMIT))
        elif var == 'category':
            self.cursor.execute("SELECT DISTINCT category FROM songs WHERE display = 1 AND MATCH (category) AGAINST (%s IN BOOLEAN MODE) LIMIT %s", (val, LIMIT))
        else:
            return([])
        results = self.cursor.fetchall()
        results = [x[0] for x in results]
        print(var, val, results)
        return(results)

    def getSongById(self, id):
        ret = dict()
        id = str(id).strip()
        id = self.conn.escape_string(id)
        id = re.sub(r'[^0-9]+', '', id)
        self.cursor.execute("SELECT id,song_title,artist_id,album_id,media,category,side,track,select,performance_type,canadian,select FROM songs WHERE display = 1 AND id = %s", (id,))
        results = self.cursor.fetchall()
        if len(results) != 1:
            flask.abort(404)
        ret['id'] = results[0][0]
        ret['song_title'] = results[0][1]
        ret['artist_id'] = results[0][2]
        ret['album_id'] = results[0][3]
        ret['media'] = results[0][4]
        ret['category'] = results[0][5]
        ret['side'] = results[0][6]
        ret['track'] = results[0][7]
        ret['select'] = results[0][8]
        ret['performance_type'] = results[0][9]
        ret['canadian'] = results[0][10] == b'\x00'
        songObj = music_manager.Song(ret)
        return(songObj)

    def getAlbumNumById(self, id):
        id = self.conn.escape_string(id)
        id = re.sub(r'[^0-9]+', '', id)
        self.cursor.execute("SELECT alb_num FROM albums WHERE id = %s", (id,))
        results = self.cursor.fetchall()
        if len(results) < 1:
            return(None)
        elif len(results) > 1:
            flask.abort(500)
        return(results[0][0])

    def getArtistNameById(self, id):
        id = self.conn.escape_string(str(id))
        id = re.sub(r'[^0-9]+', '', id)
        self.cursor.execute("SELECT name FROM artists WHERE id = %s", (id,))
        results = self.cursor.fetchall()
        if len(results) < 1:
            return(None)
        elif len(results) > 1:
            raise AssertionError('DB response indicates duplicate in unique key')
        else:
            return(results[0][0])

    # def getPlaylistNameById(self, id):
    #     id = id.strip()
    #     id = self.conn.escape_string(str(id))
    #     id = re.sub(r'[^0-9]+', '', id)
    #     self.cursor.execute("SELECT name FROM playlists WHERE id = %s", (id,))
    #     results = self.cursor.fetchall()
    #     if len(results) < 1:
    #         return(None)
    #     elif len(results) > 1:
    #         raise AssertionError('DB response indicates duplicate in unique key')
    #     else:
    #         return(results[0][0])

    def getArtistIdByName(self, name, create=False):
        if name.strip() == str():
            return(None)
        name = name.strip()
        name = self.conn.escape_string(name)
        name = re.sub(r'[^a-zA-z0-9,& ]+', '', name)
        self.cursor.execute("SELECT id FROM artists WHERE name LIKE %s", (name,))
        results = self.cursor.fetchall()
        if len(results) < 1:
            if create:
                self.cursor.execute("INSERT INTO artists (name) values (%s)", (name,))
                self.conn.commit()
                return(self.getArtistIdByName(name, create))
            else:
                flask.abort(404)
        elif len(results) > 1:
            raise AssertionError('DB response indicates duplicate in unique key')
        else:
            return(results[0][0])

    def getAlbumIdByNum(self, num, artist_id=None, create=False):
        if num.strip() == str():
            return(None)
        num = num.strip()
        num = self.conn.escape_string(num)
        num = re.sub(r'[^a-zA-z0-9,& ]+', '', num)
        self.cursor.execute("SELECT id FROM albums WHERE alb_num LIKE %s", (num,))
        results = self.cursor.fetchall()
        if len(results) < 1:
            if create and artist_id == None:
                self.cursor.execute("INSERT INTO albums (alb_num) values (%s)", (num,))
                self.conn.commit()
                return(self.getAlbumIdByNum(num, create))
            if create and artist_id != None:
                if type(artist_id) != type(int()) or self.getArtistNameById(artist_id) == None:
                    raise AssertionError('Invalid artist_id: ' + str(artist_id))
                self.cursor.execute("INSERT INTO albums (alb_num, artist_id) values (%s, %s)", (num, artist_id))
                self.conn.commit()
                return(self.getAlbumIdByNum(num, artist_id, create))
            else:
                flask.abort(404)
        elif len(results) > 1:
            raise AssertionError('DB response indicates duplicate in unique key')
        else:
            return(results[0][0])

    def processSongChanges(self, changes):
        # changes should be {'field':[old, new]}
        pass

    def getPlaylists(self, uid):
        # Get playlists belonging to self.username
        self.cursor.execute("SELECT id,name FROM playlists WHERE user_id = %s", (uid,))
        results = self.cursor.fetchall()
        ret = {row[0]:row[1] for row in results}
        return(ret)

    def getPlaylistById(self, id):
        # Returns Playlist object
        self.cursor.execute("SELECT name FROM playlists WHERE id = %s", (id,))
        results = self.cursor.fetchall()
        name = results[0][0]
        self.cursor.execute("SELECT song_id,position FROM playlist_songs WHERE playlist_id = %s", (id,))
        result = self.cursor.fetchall()
        songs = {row[1]:self.getSongById(row[0]) for row in result}
        ret = music_manager.Playlist(id, name, songs)
        return(ret)

    def createPlaylist(self, playlist_name, owned_by):
        # Returns ID of new playlist
        pass

    def addSong(self, song_title, artist_id, album_id, media, category, side, track, performance_type, theme, canadian):
        canadian = int(canadian)
        # Check if we already have a song like the one we are adding
        self.cursor.execute("SELECT id FROM songs WHERE song_title = %s AND artist_id = %s AND album_id = %s", (song_title, artist_id, album_id))
        results = self.cursor.fetchall()
        if len(results) > 0:
            raise AssertionError('Duplicate entry exists. <a class="usepost" href="/modify?song_id=%s">Edit entry</a>.' % (results[0][0],))
        self.cursor.execute("INSERT INTO songs (song_title, artist_id, album_id, media, category, side, track, performance_type, theme, canadian) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (song_title, artist_id, album_id, media, category, side, track, performance_type, theme, canadian))
        self.conn.commit()
        results = self.cursor.fetchall()
        if len(results) > 0:
            return(results[0])
    
    def importCSVDB(self, file):
        def sanitize(string):
            string = re.sub(r'O\\', r"O'", string)
            string = re.sub(r"[^a-zA-z0-9,&' ]+", '', string)

        required_keys = ['MKEY', 'MEDIA', 'MCATEGORY', 'ARTIST', 'TITLE', 'SIDE', 'TRACK', 'ALBNUM', 'SELECT', 'PERFTYPE', 'THEME', 'CANADIAN']
        with open(file, 'rU') as infile:
            lines = infile.readlines()
            data = csv.reader(lines)
            keys = next(data)
            if len(set(required_keys) - set(keys)):
                raise ValueError('Invalid format for CSV file. Required columns are: ' + str(required_keys))
            key_indexes = {key:keys.index(key) for key in keys}
            errors = {}
            for song in data:
                safeSong = [sanitize(x) for x in song]
                MKEY = safeSong[key_indexes['MKEY']]
                MEDIA = safeSong[key_indexes['MEDIA']]
                MCATEGORY = safeSong[key_indexes['MCATEGORY']]
                ARTIST_ID = self.getArtistIdByName(safeSong[key_indexes['ARTIST']], create=True)
                TITLE = safeSong[key_indexes['TITLE']]
                SIDE = safeSong[key_indexes['SIDE']]
                TRACK = safeSong[key_indexes['TRACK']]
                ALBNUM_ID = self.getAlbumIdByNum(safeSong[key_indexes['ALBNUM']], artist_id=ARTIST_ID, create=True)
                PERFTYPE = safeSong[key_indexes['PERFTYPE']]
                THEME = safeSong[key_indexes['THEME']]
                CANADIAN = str(safeSong[key_indexes['CANADIAN']]).upper() == 'Y'
                try:   
                    self.addSong(
                        song_title = TITLE,
                        artist_id = ARTIST_ID,
                        album_id = ALBNUM_ID,
                        media = MEDIA,
                        category = MCATEGORY,
                        side = SIDE,
                        track = TRACK,
                        performance_type = PERFTYPE,
                        theme = THEME,
                        canadian = CANADIAN
                    )
                    print('Imported ' + MKEY)
                except Exception as e:
                    errors[MKEY] = e
            return(errors)

    def findMatchingSongs(self, search):
        if len(search) < 1:
            return(None)
        print(search)
        query = "SELECT * FROM songs WHERE display = 1"
        query_params = list()
        for key in search:
            query += " AND MATCH (%s) AGAINST (%s IN BOOLEAN MODE)"
            query_params += [key, search[key]]
        print(query, query_params)
        self.cursor.execute(query, query_params)
        results = self.cursor.fetchall()
        pass 

    def getUsernameById(self, id):
        self.cursor.execute("SELECT username FROM users WHERE id = %s", (id,))
        results = self.cursor.fetchall()
        if len(results) < 1:
            raise ValueError('User does not exist.')
        elif len(results) > 1:
            # Users with that username already exist.
            raise AssertionError('Duplicate user exists. Contact an adminstrator to ensure database consistency.')
        return(results[0][0])

    def getUserByUsername(self, username, action=None):
        self.cursor.execute("SELECT id,username,passhash,master,admin,active,lockout_count,sec_q,sec_a FROM users WHERE username = %s", (username,))
        results = self.cursor.fetchall()
        if len(results) < 1:
            raise ValueError('User does not exist.')
        elif len(results) > 1:
            # Users with that username already exist.
            raise AssertionError('Duplicate user exists. Contact an adminstrator to ensure database consistency.')
        userinfo = {
            'id':results[0][0],
            'username':results[0][1],
            'passhash':results[0][2],
            'master':results[0][3] == b'\x01',
            'admin':results[0][4] == b'\x01',
            'active':results[0][5] == b'\x01',
            'lockout_count':int(results[0][6]),
            'sec_q':results[0][7],
            'sec_a':results[0][8]
        }
        if action == 'login':
            if 'HTTP_X_FORWARDED_FOR' in flask.request.headers:
                ip = flask.request.headers['HTTP_X_FORWARDED_FOR']
            elif 'REMOTE_ADDR' in flask.request.headers:
                ip = flask.request.headers['REMOTE_ADDR']
            else:
                ip = 'TERMINAL LOGIN'
            self.cursor.execute("INSERT INTO user_logins (user, remote_ip) VALUES (%s, %s)", (userinfo['id'], ip))
            self.conn.commit()
        return(userinfo)

    def getUserSecQAByUsername(self, username):
        qty = self.cursor.execute("SELECT sec_q,sec_a FROM users WHERE username = %s", (username,))
        results = self.cursor.fetchall()
        if qty < 1:
            raise ValueError('User does not exist.')
        elif qty > 1:
            raise AssertionError('Duplicate user exists. Contact an adminstrator to ensure database consistency.')
        return(results[0])

    def createUser(self, form):
        # Form should already be validated but we will double check
        if not form.validate():
            raise AssertionError('Unable to validate account creation request.')
        num_results = self.cursor.execute("SELECT id,username FROM users WHERE username = %s", (form.username.data,))
        results = self.cursor.fetchall()
        if num_results > 0:
            # Users with that username already exist.
            raise AssertionError('Username exists already: ' + str(results[0][1]))# + ':' + str(results[0][0]))
        # The username is good. Create the user.
        self.cursor.execute("INSERT INTO users (username) VALUES (%s)", (form.username.data))
        self.conn.commit()
    
    def getAllUsers(self):
        self.cursor.execute("SELECT id,username,admin,lockout_count,active,master FROM users")
        results = self.cursor.fetchall()
        users = [{'id':row[0], 'username':row[1], 'admin':row[2] == b'\x01', 'locked':row[3] > 9, 'active':row[4] == b'\x01', 'master':row[5] == b'\x01'} for row in results]
        return(len(users), users)
    
    def getAcctActivity(self, id):
        self.cursor.execute("SELECT remote_ip,timestamp FROM user_logins WHERE user = %s", (id,))
        results = self.cursor.fetchall()
        ret = list()
        for result in results:
            newresult = dict()
            newresult['ip'] = result[0]
            newresult['day'] = result[1].strftime('%d-%b-%Y')
            newresult['time'] = result[1].strftime('%H:%M:%S')
            ret.append(newresult)
        return(len(ret), ret)

    def unlockAccount(self, id):
        self.cursor.execute("UPDATE users SET lockout_count = 0 WHERE id = %s", (id,))
        self.conn.commit()

    def updateHashedPassword(self, username, newhashedpassword):
        self.cursor.execute("UPDATE users SET passhash = %s WHERE username = %s", (newhashedpassword, username))
        self.conn.commit()

    def toggleActiveAccountById(self, id):
        self.cursor.execute("SELECT active FROM users WHERE id = %s", (id,))
        results = self.cursor.fetchall()
        if results[0][0] == b'\x01':
            # Deactivate account
            self.cursor.execute("UPDATE users SET active = 0 WHERE id = %s", (id,))
        else:
            # Activate account
            self.cursor.execute("UPDATE users SET active = 1 WHERE id = %s", (id,))
        self.conn.commit()

    def toggleMasterAccountById(self, id):
        self.cursor.execute("SELECT master FROM users WHERE id = %s", (id,))
        results = self.cursor.fetchall()
        if results[0][0] == b'\x01':
            # Make normal account
            self.cursor.execute("UPDATE users SET master = 0 WHERE id = %s", (id,))
        else:
            # Make master account
            self.cursor.execute("UPDATE users SET master = 1 WHERE id = %s", (id,))
        self.conn.commit()

    def toggleAdminAccountById(self, id):
        self.cursor.execute("SELECT admin FROM users WHERE id = %s", (id,))
        results = self.cursor.fetchall()
        if results[0][0] == b'\x01':
            # Make normal account
            self.cursor.execute("UPDATE users SET admin = 0 WHERE id = %s", (id,))
        else:
            # Make admin account
            self.cursor.execute("UPDATE users SET admin = 1 WHERE id = %s", (id,))
        self.conn.commit()

    def toggleActiveAccountByUsername(self, username):
        self.cursor.execute("SELECT active FROM users WHERE username = %s", (username,))
        results = self.cursor.fetchall()
        if results[0][0] == b'\x01':
            # Deactivate account
            self.cursor.execute("UPDATE users SET active = 0 WHERE username = %s", (username,))
        else:
            # Activate account
            self.cursor.execute("UPDATE users SET active = 1 WHERE username = %s", (username,))
        self.conn.commit()

    def toggleMasterAccountByUsername(self, username):
        self.cursor.execute("SELECT master FROM users WHERE username = %s", (username,))
        results = self.cursor.fetchall()
        if results[0][0] == b'\x01':
            # Make normal account
            self.cursor.execute("UPDATE users SET master = 0 WHERE username = %s", (username,))
        else:
            # Make master account
            self.cursor.execute("UPDATE users SET master = 1 WHERE username = %s", (username,))
        self.conn.commit()

    def toggleAdminAccountByUsername(self, username):
        self.cursor.execute("SELECT admin FROM users WHERE username = %s", (username,))
        results = self.cursor.fetchall()
        if results[0][0] == b'\x01':
            # Make normal account
            self.cursor.execute("UPDATE users SET admin = 0 WHERE username = %s", (username,))
        else:
            # Make admin account
            self.cursor.execute("UPDATE users SET admin = 1 WHERE username = %s", (username,))
        self.conn.commit()

    def incrementLockoutCount(self, username):
        self.cursor.execute("UPDATE users SET lockout_count = lockout_count + 1 WHERE username = %s", (username,))
        self.conn.commit()

    def setUserSecInfo(self, username, passhash, sec_q, sec_a):
        self.cursor.execute("UPDATE users SET passhash = %s, sec_q = %s, sec_a = %s WHERE username = %s", (passhash, sec_q, sec_a, username))
        self.conn.commit()

































#main() function for testing methods in the DBQuery class
def main():
    # print 'Demo of all the methods of the DBQuery class'
    dbquery = DBQuery()
    # print '\nDemo of method: dbquery.get_ent_types()'
    # print str(dbquery.get_ent_types())
    # print '\nDemo of method: dbquery.FindMatchingEntities()'
    # pairs = {'servers':'amazon'}
    # print str(dbquery.FindMatchingEntities('client', pairs ))
    # print '\nDemo of method: dbquery.get_all_used_var_vals()'
    # print str(dbquery.get_all_used_var_vals('client', 'servers'))
    # print '\nDemo of method: dbquery.GetEntityVarVals()'
    # print str(dbquery.GetEntityVarVals('tiny', 'server', 'functions'))
    # print '\nDemo of method: dbquery.get_ent_all_var_vals()'
    # print str(dbquery.get_ent_all_var_vals('printer', 'icomprt1'))
    # print '\nDemo of method: dbquery.get_ent_vals_table()'
    # print str(dbquery.get_ent_vals_table('printer', 'icomprt1'))
    dbquery.close()
    return 0

if __name__ == '__main__':
    main()

