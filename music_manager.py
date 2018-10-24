
import passlib
import wtforms

# All information for these classes should be passed through the constructors.
# Objects of these classes are going to be passed back from DBManager so I don't
# want this module calling back to DBManager.

class Song:
    # We may (will) have a LOT of these objects made for searching or
    # doing the initial setup so __slots__ will make us MUCH more efficient
    __slots__ = [
        '_id',
        '_song_title', 
        '_artist', # I want this to be an object, not text
        '_album', # I want this to be an object, not text
        '_media', # Legacy? No idea what this is
        '_category',
        '_side',
        '_track',
        '_select', # Legacy? No idea what this is
        '_performance_type',
        '_theme',
        '_canadian'
    ]

    def __init__(self, properties):
        if type(properties) == type(dict()):
            # If the key in question is missing, we get an exception
            # This is on purpose; all of the fields are MANDATORY
            self._id = properties['id']
            self._song_title = properties['song_title']
            self._artist = Artist(properties['artist_id'])
            self._album = Album(properties['album_id'])
            self._media = properties['media']
            self._category = properties['category']
            self._side = properties['side']
            self._track = properties['track']
            self._select = properties['select']
            self._performance_type = properties['performance_type']
            self._canadian = properties['canadian']
        elif type(properties) == type(self):
            # This will be our "deep copy"
            self._id = properties._id
            self._song_title = properties._song_title
            self._artist = properties._artist
            self._album = properties._album 
            self._media = properties._media
            self._category = properties._category
            self._side = properties._side
            self._track = properties._track
            self._select = properties._select 
            self._performance_type = properties._performance_type
            self._canadian = properties._canadian
        else:
            raise TypeError('Song.__init__ takes dict or Song.')

    @property
    def id(self):
        return(self._id)




    def __sub__(self, other):
        # returns {field:[old, new]}
        pass 
        

class Artist:
    __slots__ = [
        '_id',
        '_artist_name'
    ]

    def __init__(self, artist_id, artist_name):
        if  type(artist_id) != type(int()) or type(artist_name) != type(str()):
            raise TypeError('Artist.__init__ takes int of artist_id and str of artist_id.')
        self._id = artist_id
        self._artist_name = artist_name

    def __str__(self):
        return(self._artist_name)

    @property
    def artist_name(self):
        return(self._artist_name)

    @property
    def id(self):
        return(self._id)


class Album:
    __slots__ = [
        '_id',
        '_album_number'
    ]

    def __init__(self, album_id, album_num):
        if type(album_id) != type(int()) or type(album_num) != type(str()):
            raise TypeError('Album.__init__ takes int of album_id and str of album_name.')
        self._id = album_id
        self._album_number = album_num

    def __str__(self):
        return(self._album_number)

    @property
    def album_number(self):
        return(self._album_number)

    @property
    def id(self):
        return(self._id)

class Playlist:
    __slots__ = [
        '_id', 
        '_playlist_name', 
        '_songs'
    ]

    def __init__(self, playlist_id, playlist_name, songs):
        if type(playlist_id) != type(int()) or type(playlist_name) != type(str()) or type(songs) != type(dict()):
            raise TypeError('Album.__init__ takes int of playlist_id and str of playlist_name and dict of songs in format position:Song.')
        self._id = playlist_id
        self._playlist_name = playlist_name
        self._songs = songs

    @property
    def playlist_name(self):
        return(self._playlist_name)

    @property
    def id(self):
        return(self._id)

    @property
    def songs(self):
        return(dict(self._songs)) 

    @property
    def song_ids(self):
        return(sorted(self._songs.keys()))

    def __str__(self):
        return(self._playlist_name)


class EntityAddForm(wtforms.Form):
    song_title = wtforms.StringField('Song', render_kw={"placeholder": "Sweet Dreams"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=1, max=255)
    ])
    artist_name = wtforms.StringField('Artist', render_kw={"placeholder": "Cline, Patsy"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=1, max=255)
    ])
    album_num = wtforms.StringField('Album Number', render_kw={"placeholder": "4028E"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=1, max=10)
    ])
    media = wtforms.StringField('Media', render_kw={"placeholder": "3"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=1, max=10)
    ])
    category = wtforms.StringField('Category', render_kw={"placeholder": "Country"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=4, max=75)
    ])
    side = wtforms.IntegerField('Side', render_kw={"placeholder": "3"}, validators=[
        wtforms.validators.DataRequired()
    ])
    track = wtforms.IntegerField('Track', render_kw={"placeholder": "5"}, validators=[
        wtforms.validators.DataRequired()
    ])
    performance_type = wtforms.StringField('Performance Type', render_kw={"placeholder": "Female"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=1, max=255)
    ])
    theme = wtforms.StringField('Theme', render_kw={"placeholder": "General"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=4, max=75)
    ])
    canadian = wtforms.SelectField('Canadian Content', choices=[
        ('n', 'No'),
        ('y', 'Yes')
    ])