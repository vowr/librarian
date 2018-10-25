# System imports
import flask
import flask_login
import db_manager
import passlib.hash
import wtforms

# When logging in as normal user (not master), check if the user is a master and has no password. If so then send to password page.

class FullRegisterForm(wtforms.Form):
    username = wtforms.StringField('User name', render_kw={"placeholder": "User name"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=2, max=32)
    ])
    password = wtforms.PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = wtforms.PasswordField('Confirm password', render_kw={"placeholder": "Confirm password"})
    sec_q = wtforms.SelectField('Security Question', choices=[
        ('What is your mother\'s middle name?', 'What is your mother\'s middle name?'),
        ('What high school did you go to?', 'What high school did you go to?'),
        ('On what street was your childhood home located?', 'On what street was your childhood home located?')
    ])
    sec_a = wtforms.StringField('Security answer', render_kw={"placeholder": "Security answer"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(max=255)
    ])
    master = wtforms.SelectField('Master User', choices=[
        ('n', 'No'),
        ('y', 'Yes')
    ])
    admin = wtforms.SelectField('Administrative User', choices=[
        ('n', 'No'),
        ('y', 'Yes')
    ])

class SelfRegisterForm(wtforms.Form):
    username = wtforms.StringField('User name', render_kw={"placeholder": "User name"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=2, max=32)
    ])

class AccountUpgradeForm(wtforms.Form):
    # Used to upgrade to master
    password = wtforms.PasswordField('New password', render_kw={"placeholder": "New password"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = wtforms.PasswordField('Confirm password', render_kw={"placeholder": "Confirm password"})
    sec_q = wtforms.SelectField('Security Question', choices=[
        ('What is your mother\'s middle name?', 'What is your mother\'s middle name?'),
        ('What high school did you go to?', 'What high school did you go to?'),
        ('On what street was your childhood home located?', 'On what street was your childhood home located?')
    ])
    sec_a = wtforms.StringField('Security answer', render_kw={"placeholder": "Security answer"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(max=255)
    ])

class PasswordResetForm(wtforms.Form):
    password = wtforms.PasswordField('New password', render_kw={"placeholder": "New password"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = wtforms.PasswordField('Confirm password', render_kw={"placeholder": "Confirm password"}, validators=[
        wtforms.validators.DataRequired()
    ])


class BasicLoginForm(wtforms.Form):
    username = wtforms.StringField('User name', render_kw={"placeholder": "User name"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=2, max=32)
    ])

class MasterLoginForm(wtforms.Form):
    username = wtforms.StringField('User name', render_kw={"placeholder": "User name"}, validators=[
        wtforms.validators.DataRequired(), 
        wtforms.validators.Length(min=2, max=32)
    ])
    password = wtforms.PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[
        wtforms.validators.DataRequired()
    ])

class User(flask_login.UserMixin):
    __slots__ = [
        '_id',
        '_username',
        '_active',
        '_lockout_count',
        '_permissions',
        '_effective_permissions'
    ]
    
    class _UserPermisson:
        __slots__ = [
            '_master',
            '_admin'
        ]
        def __init__(self):
            self._master = None
            self._admin = None

        @property
        def master(self):
            return(self._master)

        @property 
        def admin(self):
            return(self._admin)

    def __init__(self, username, plaintextPassword, is_authenticated=False, login_type='basic'):
        db = db_manager.DBQuery()
        if is_authenticated:
            userinfo = db.getUserByUsername(username)
        else:
            userinfo = db.getUserByUsername(username, action='login')
        if userinfo['lockout_count'] > 9:
            raise AssertionError('Authentication failed. Your account is locked due to repeated invalid login attempts.')

        self._permissions, self._effective_permissions = self._UserPermisson(), self._UserPermisson()
        if login_type == 'master':
            if not is_authenticated:
                goodPasswd = passlib.hash.pbkdf2_sha512.verify(plaintextPassword, userinfo['passhash'])
                if not goodPasswd:
                    db.incrementLockoutCount(username)
                    raise ValueError('Authentication failed. Incorrect password.')
            self._effective_permissions._master = userinfo['master'] 
            self._effective_permissions._admin = userinfo['admin']
        else:
            self._master, self._admin = False, False
        
        if not userinfo['active']:
            raise AssertionError('Authentication failed. Your account has been marked as inactive.')
        self._id = userinfo['id']
        self._username = userinfo['username']
        self._active = userinfo['active']
        self._lockout_count = userinfo['lockout_count']
        self._permissions._master = userinfo['master']
        self._permissions._admin = userinfo['admin']

    @property
    def is_authenticated(self):
        return(True)
    
    @property
    def id(self):
        return(self._id)
    
    @property
    def username(self):
        return(self._username)
    
    @property 
    def is_master(self):
        return(self._effective_permissions.master)

    @property
    def is_admin(self):
        return(self._effective_permissions.admin)
        
    @property
    def is_real_master(self):
        return(self._permissions.master)

    @property
    def is_real_admin(self):
        return(self._permissions.admin)

    def get_id(self):
        return(self._id)

    def __eq__(self, other):
        return(self._id == other._id)

def verify(candidate, hashed):
    return(passlib.hash.pbkdf2_sha512.verify(candidate, hashed))

def updatePassword(username, plaintextnewpassword):
    hashedpassword = passlib.hash.pbkdf2_sha512.hash(plaintextnewpassword, rounds=75000, salt_size=16)
    db = db_manager.DBQuery()
    db.updateHashedPassword(username, hashedpassword)

def encrypt(plaintext):
    ROUNDS = 75000
    SALT_SIZE = 16
    ret = passlib.hash.pbkdf2_sha512.hash(plaintext, rounds=ROUNDS, salt_size=SALT_SIZE)
    return(ret)


def upgradeUser(username, form):
    # The form should already be validated but just to make sure
    if not form.validate():
        flask.flash('Unable to validate account upgrade request.', 'error')
        return(flask.redirect(flask.url_for('cpHome')))
    passhash = encrypt(form.password.data)
    sec_q = form.sec_q.data
    sec_a = encrypt(form.sec_a.data)
    try:
        db = db_manager.DBQuery()
        db.setUserSecInfo(username, passhash, sec_q, sec_a)
        db.toggleMasterAccountByUsername(username) 
    except:
        raise AssertionError('Unable to upgrade your account. A system error occurred.')

def auth():
    if not flask_login.current_user.is_admin:
        raise PermissionError('Access denied to protected resource.')

def isAdmin():
    return(True)
    # if not flask_login.current_user.is_authenticated:
    #     return(False)
    # else:
    #     if False:
    #         return(True)
    #     else:
    #         return(False)

def canEdit():
    return(True)
    # if not flask_login.current_user.is_authenticated:
    #     return(False)
    # else:
    #     if False:
    #         return(True)
    #     else:
    #         return(False) 