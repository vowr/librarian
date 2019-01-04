#!/usr/bin/python3
###################################################################
# File: vowr.py
# Written by: Jacob House
# Created: August 12, 2018
# Last Modified: "
# Modifications by: Jacob House
#
# Description: Python Flask application vowr.app for new digital
# catalogue to replace the one running on DOS
###################################################################


# System imports
import sys
import os
import csv
import datetime 

# Local imports
from . import music_manager
from . import auth_manager
from . import db_manager

# Flask magic
import flask
import flask_login

app = flask.Flask(__name__)
app.secret_key = '\xf0n\x94x\xdfK\x98\xbdN3\xb4\xd0\x1a\x1f\xd1\xd1\xf3P\xd1\xa6I~\x93@'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/gatekeeper/sign-in/basic' # This is dependent on the routes below

# General-use dictionary to pass things to the HTML processor
params = dict()
params['site_title'] = 'VOWR Music Librarian'

# I want the index page to have a consistent URI so redirecting to that page
@app.route('/')
def rootPatge():
    return(flask.redirect('/default', 301))

# The default splash/index page
@app.route('/default')
def defaultPage():
    return(flask.render_template('default.htm', params=params))

# Music search page
@app.route('/search', methods=['POST', 'GET'])
@flask_login.login_required
def searchPage():
    if flask.request.method == 'POST':
        search_terms = ['song_title', 'artist_name', 'album_num', 'category', 'canadian', 'dedup', 'page']
        search = {term:flask.request.form.get(term) for term in search_terms if flask.request.form.get(term)}
        try:
            db = db_manager.DBQuery()
        except:
            flask.abort(500)    
        params['searchResults'] = db.findMatchingSongs(search)
        params['num_results'] = len(params['searchResults'])
        # if len(params['searchResults']) < 1:
        #     params['searchResults'] = None
    return(flask.render_template('search.htm', params=params))

# Accepts only POSTS (from JS) to help autocomplete search requests
# The logic in db_manager will return the first 10 matches for all
# full or partial matches to any and all words in the search bar...
# The results are NOT ordered by relevance. This is something I would
# like to implement but since I am using MySQL boolean full text
# searching, this may be difficult without a full rewrite.
@app.route('/search/auto', methods=['GET', 'POST'])
@flask_login.login_required
def autocomplete():
    try:
        db = db_manager.DBQuery()
    except Exception:
        flask.abort(500)
    searchParams, results = {'var':None, 'val':None}, []
    for param in searchParams:
        # First check GET... should be nothing since GET is disallowed in the route
        searchParams[param] = flask.request.args.get(param)
        if searchParams[param] == None:
            # If nothing in get, try POST
            searchParams[param] = flask.request.form.get(param)
    results = db.autocomplete(searchParams['var'], searchParams['val'])
    return(flask.jsonify(results))

# This is used to add new entries to the database. The /append page is fairly flat...
# Unlike /modify, there is no logic going on here since the user must supply all values.
# The logic for /append is in the /append/commit backend page.
@app.route('/append', methods=['GET', 'POST'])
@flask_login.login_required
def appendPage():
    if flask.request.method == 'POST':
        # Here is where the logic for /append happens. If the user tries to append an entry that exists
        # (or is similar), we will ask if they want to modify X and if so, send to the /modify page
        # with the song ID in the request so that /modify can pull up the song from the DB and have the
        # properties ready for edit.
        # This function will send back (JSON?) for a delta of the changes.
        # Ex. <green>[<date>-<time>] <user> added <song> by <artist> from <albnum>.</green>
        # Ex. <red>[<date>-<time>] <user> FAILED to add <song> by <artist> from <albnum>. Please try again.</red>
        
        # Check if all the required fields are in the POST
        fields = ['song_title', 'artist_name', 'album_num', 'media', 'category', 'side', 'track', 'performance_type', 'theme', 'canadian']
        for field in fields:
            if field not in flask.request.form:
                flask.abort(400)
        try:
            db = db_manager.DBQuery()
        except Exception:
            flask.abort(500)
        timestamp = '[' + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + ']'
        artist_id = db.getArtistIdByName(flask.request.form.get('artist_name'), create=True)
        album_id = db.getAlbumIdByNum(flask.request.form.get('album_num'), artist_id, create=True)
        canadian = flask.request.form.get('canadian').lower().strip() == 'y'
        try:
            result = db.addSong(
                flask.request.form.get('song_title'),
                artist_id,
                album_id,
                flask.request.form.get('media'),
                flask.request.form.get('category'),
                flask.request.form.get('side'),
                flask.request.form.get('track'),
                flask.request.form.get('performance_type'),
                flask.request.form.get('theme'),
                canadian
            )
        except Exception as e:
            ret = '<div><span class="error">' + timestamp + '</span> Failed to append "' + flask.request.form.get('song_title') + '" (' + str(e) + ')</div>'
        else:
            ret = '<div><span class="success">' + timestamp + '</span> Appended "' + flask.request.form.get('song_title') + '"'
            if result != None:
                ret += ' (' + result[0] + ')</div>'
            else:
                ret += '</div>'
        return(flask.jsonify(ret))
    else:
        params['append_form'] = music_manager.EntityAddForm(flask.request.form)
        return(flask.render_template('append.htm', params=params))


# This page needs to get a POST of the song entry that the user is trying to edit.
# If no song_id in POST, just print the instructions.
# Otherwise, pull up the song from the DB by its ID and give the user access to edit it.
# We really should record when and by whom the last edit was made. Option to undo??
@app.route('/modify', methods=['POST', 'GET'])
@flask_login.login_required
def modifyPage():
    if flask.request.method == 'POST':
        if flask.request.form.get('song_id') != None:
            # We have a song. Retrieve it from the DB and return the info
            try:
                db = db_manager.DBQuery(flask.session.get('username'))
            except Exception:
                flask.abort(500)
            # getSongById will throw a 404 if the entity is not found
            params['entity'] = music_manager.Song(db.getSongById(flask.request.form.get('song_id')))
            db.close()
    return(flask.render_template('modify.htm', params=params))

@app.route('/modify/commit', methods=['POST'])
@flask_login.login_required
def commitModify():
    ret = list()
    if flask.request.method == 'POST' and flask.request.form.get('song_id') != None:
        # We want a delta between the new and old so that we can return what the changes are
        # Get the old
        try:
            db = db_manager.DBQuery(flask.session.get('username'))
            old = db.getSongById(flask.request.form.get('song_id')) # Dict
        except Exception:
            db.close()
            flask.abort(500)
        timestamp = '[' + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + ']'
        changes = dict()
        if old['name'] != flask.request.form.get('song'):
            changes['name'] = flask.request.form.get('song')
        if old['album_code'] != flask.request.form.get('album'):
            artist_id = db.getArtistIdByName(flask.request.form.get('artist'), create=True)
            changes['album'] = db.getAlbumIdByCode(flask.request.form.get('album'), artist_id, create=True)
        if old['artist_name'] != flask.request.form.get('artist'):
            changes['artist_id'] = artist_id
        if old['genre'] != flask.request.form.get('genre'):
            changes['genre'] = flask.request.form.get('genre')
        if old['canadian'] == (flask.request.form.get('genre') == 'y'):
            changes['canadian'] = flask.request.form.get('genre') == 'y'
        errs = db.processSongChanges(changes) # returns dict of failed items. empty dict is good
        succs = sorted(list(set(changes.keys()) - set(errs.keys())))
        if succs:
            msg = '<div class="success-msg">' + timestamp + ' '
            for success in succs:
                msg += success + ' changed ("' + str(old[success]) + '" to "' + str(changes[success]) + '"), '
            msg = msg[:-2] + '</div>'
            ret.append(msg)
        if errs:
            msg = '<div class="err-msg">' + timestamp + ' '
            for err in errs:
                msg += err + ' failed ("' + old[err] + '" to "' + err[err] + '"), '
            msg = msg[:-2] + '</div>'
            ret.append(msg)
        db.close()
    return(flask.jsonify(ret))



@app.route('/lineup', methods=['GET', 'POST'])
@flask_login.login_required
def lineupPage():
    try:
        db = db_manager.DBQuery()
    except Exception:
        flask.abort(500)
    params['playlist'] = None
    params['existingPlaylists'] = db.getPlaylists(flask_login.current_user.id) 
    return(flask.render_template('lineups.htm', params=params))

@app.route('/lineup/edit', methods=['GET', 'POST'])
@flask_login.login_required
def lineupEdit():
    if flask.request.method == 'POST' and flask.request.form.get('playlist'):
        try:
            db = db_manager.DBQuery()
        except Exception:
            flask.abort(500)
        params['playlistId'] = flask.request.form.get('playlist')

        if params['playlistId'] == 'create_new':
            if not 'playlist_name' in flask.request.form:
                flask.flash('New lineup name not received.', 'error')
                return(flask.redirect(flask.url_for('lineupPage')))
            try:
                params['playlistId'] = db.createPlaylist(flask.request.form.get('playlist_name'), flask_login.current_user.id)
            except Exception as e:
                flask.flash(str(e), 'error')                
                return(flask.redirect(flask.url_for('lineupPage')))
        try:
            params['playlistObj'] = db.getPlaylistById(params['playlistId'])
        except Exception as e:
            flask.flash('The lineup you requested exists but cannot be retrieved. (' + str(e) + ')', 'error')
        return(flask.render_template('lineups_edit.htm', params=params))
    else:
        return(flask.redirect(flask.url_for('playlistPage')))

@app.route('/control-panel')
@flask_login.login_required
def cpBase():
    return(flask.redirect(flask.url_for('cpHome'), 301))

@app.route('/control-panel/home')
@flask_login.login_required
def cpHome():
    return(flask.render_template('control-panel_home.htm', params=params))


@app.route('/control-panel/users')
@flask_login.login_required
def cpUsers():
    try:
        auth_manager.auth()
    except Exception as e:
        flask.flash(str(e), 'error')
        return(flask.redirect(flask.url_for('defaultPage')))
    try:
        db = db_manager.DBQuery()
    except:
        flask.abort(500)
    params['num_users'], params['users'] = db.getAllUsers() 
    return(flask.render_template('control-panel_users.htm', params=params))


@app.route('/control-panel/users/logs', methods=['GET', 'POST'])
@flask_login.login_required
def cpUserLogs():
    try:
        auth_manager.auth()
    except Exception as e:
        flask.flash(str(e), 'error')
        return(flask.redirect(flask.url_for('defaultPage')))
    if flask.request.method == 'POST' and flask.request.form.get('id'):
        try:
            db = db_manager.DBQuery()
        except:
            flask.abort(500)
        try:
            params['acct'] = db.getUsernameById(flask.request.form.get('id'))
            params['num_logins'], params['logs'] = db.getAcctActivity(flask.request.form.get('id'))
        except Exception as e:
            flask.flash(str(e), 'error')
            return(flask.redirect(flask.url_for('cpUsers')))
        return(flask.render_template('control-panel_users_logs.htm', params=params))
    else:
        return(flask.redirect(flask.url_for('cpUsers')))

@app.route('/control-panel/users/unlock', methods=['GET', 'POST'])
@flask_login.login_required
def cpUserUnlock():
    try:
        auth_manager.auth()
    except Exception as e:
        flask.flash(str(e), 'error')
        return(flask.redirect(flask.url_for('defaultPage')))
    if flask.request.method == 'POST' and flask.request.form.get('id'):
        try:
            db = db_manager.DBQuery()
        except:
            flask.abort(500)
        db.unlockAccount(flask.request.form.get('id'))
    return(flask.redirect(flask.url_for('cpUsers')))

@app.route('/control-panel/users/toggleactive', methods=['GET', 'POST'])
@flask_login.login_required
def cpUserActive():
    try:
        auth_manager.auth()
    except Exception as e:
        flask.flash(str(e), 'error')
        return(flask.redirect(flask.url_for('defaultPage')))
    if flask.request.method == 'POST' and flask.request.form.get('id'):
        try:
            db = db_manager.DBQuery()
        except:
            flask.abort(500)
        db.toggleActiveAccountById(flask.request.form.get('id'))
    return(flask.redirect(flask.url_for('cpUsers')))

@app.route('/control-panel/users/toggleadmin', methods=['GET', 'POST'])
@flask_login.login_required
def cpUserAdmin():
    try:
        auth_manager.auth()
    except Exception as e:
        flask.flash(str(e), 'error')
        return(flask.redirect(flask.url_for('defaultPage')))
    if flask.request.method == 'POST' and flask.request.form.get('id'):
        try:
            db = db_manager.DBQuery()
        except:
            flask.abort(500)
        db.toggleAdminAccountById(flask.request.form.get('id'))
    return(flask.redirect(flask.url_for('cpUsers')))

@app.route('/control-panel/users/togglemaster', methods=['GET', 'POST'])
@flask_login.login_required
def cpUserMaster():
    try:
        auth_manager.auth()
    except Exception as e:
        flask.flash(str(e), 'error')
        return(flask.redirect(flask.url_for('defaultPage')))
    if flask.request.method == 'POST' and flask.request.form.get('id'):
        try:
            db = db_manager.DBQuery()
        except:
            flask.abort(500)
        db.toggleMasterAccountById(flask.request.form.get('id'))
    return(flask.redirect(flask.url_for('cpUsers')))

@app.route('/control-panel/setup')
@flask_login.login_required
def cpSetup():
    try:
        auth_manager.auth()
    except Exception as e:
        flask.flash(str(e), 'error')
        return(flask.redirect(flask.url_for('defaultPage')))
    try:
        db = db_manager.DBQuery()
        db.createTables()
        params['setupErr'] = None
    except Exception as e:
        params['setupErr'] = str(e).strip()
    return(flask.render_template('control-panel_setup.htm', params=params))


@app.route('/gatekeeper/sign-in/basic', methods=['GET', 'POST'])
def gatekeeperSignInBasic():
    if flask_login.current_user.is_authenticated:
        flask.flash('You are already logged in.', 'success')
        return(flask.redirect(flask.url_for('defaultPage')))
    params['login_form'] = auth_manager.BasicLoginForm(flask.request.form)
    if flask.request.method == 'POST' and params['login_form'].validate():
        try:
            user = auth_manager.User(params['login_form'].username.data, None, login_type='basic')
            flask.session['login'] = 'basic'
        except Exception as e:
            flask.flash(str(e), 'error')
            if 'next' in flask.request.args:
                params['next'] = flask.request.args.get('next')
            return(flask.render_template('gatekeeper_sign-in_basic.htm', params=params))
        else:
            flask_login.login_user(user)
            flask.flash('You have successfully signed in.', 'success')
            if 'next' in flask.request.args:
                return(flask.redirect(flask.request.args.get('next')))
            else:
                return(flask.redirect(flask.url_for('defaultPage')))
    else:
        if 'next' in flask.request.args:
            params['next'] = flask.request.args.get('next')
        return(flask.render_template('gatekeeper_sign-in_basic.htm', params=params))


@app.route('/gatekeeper/sign-in/master', methods=['GET', 'POST'])
def gatekeeperSignInMaster():
    if flask_login.current_user.is_authenticated:
        flask.flash('You are already logged in.', 'success')
        return(flask.redirect(flask.url_for('defaultPage')))
    params['login_form'] = auth_manager.MasterLoginForm(flask.request.form)
    if flask.request.method == 'POST' and params['login_form'].validate():
        try:
            user = auth_manager.User(params['login_form'].username.data, params['login_form'].password.data, login_type='master')
            flask.session['login'] = 'master'
        except Exception as e:
            flask.flash(str(e), 'error')
            if 'next' in flask.request.args:
                params['next'] = flask.request.args.get('next')
            return(flask.render_template('gatekeeper_sign-in_master.htm', params=params))
        else:
            flask_login.login_user(user)
            flask.flash('You have successfully signed in.', 'success')
            if 'next' in flask.request.args:
                return(flask.redirect(flask.request.args.get('next')))
            else:
                return(flask.redirect(flask.url_for('defaultPage')))
    else:
        if 'next' in flask.request.args:
            params['next'] = flask.request.args.get('next')
        return(flask.render_template('gatekeeper_sign-in_master.htm', params=params))

@app.route('/gatekeeper/register', methods=['GET', 'POST'])
def gatekeeperRegister():
    if flask_login.current_user.is_authenticated:
        flask.flash('You are already registered and logged in.', 'success')
        return(flask.redirect(flask.url_for('defaultPage')))
    params['reg_form'] = auth_manager.SelfRegisterForm(flask.request.form)
    if flask.request.method == 'POST' and params['reg_form'].validate():
        try:
            db = db_manager.DBQuery()
            db.createUser(params['reg_form'])
        except AssertionError as e:
            flask.flash(str(e), 'error')
        except Exception as e:
            flask.flash(str(e), 'error')
        else:
            flask_login.login_user(auth_manager.User(params['reg_form'].username.data, None))
            flask.flash(flask.Markup('Your account was created successfully. If you want to switch to a <em>master</em> account, use the <em>Control Panel</em> tab above.'), 'success')
            return(flask.redirect(flask.url_for('defaultPage')))
    return(flask.render_template('gatekeeper_register.htm', params=params))

@app.route('/gatekeeper/sign-out')
def gatekeeperSignOut():
    if flask_login.current_user.is_authenticated:
        flask.flash('You are now logged out.', 'success')
    flask_login.logout_user()
    if 'username' in flask.session:
        flask.session.pop('username')
    return(flask.redirect(flask.url_for('defaultPage')))

@app.route('/gatekeeper/forgot', methods=['GET', 'POST'])
def gatekeeperForgot():
    if flask_login.current_user.is_authenticated:
        flask.flash('You are already logged in.', 'success')
        return(flask.redirect(flask.url_for('defaultPage')))
    params['btn_name'] = 'Submit'
    params['reset_form_part'] = 1
    if flask.request.method == 'POST' and flask.request.form.get('username'):
        params['reset_username'] = flask.request.form['username']
        try:
            db = db_manager.DBQuery()
            params['sec_q'], sec_a = db.getUserSecQAByUsername(params['reset_username'])
        except:
            del params['reset_username']
            flask.flash('Unable to retrieve account information', 'error')
            return(flask.redirect(flask.url_for('gatekeeperForgot')))
        if params['sec_q'] is None:
            flask.flash(flask.Markup("User account <strong>" + params['reset_username'] + "</strong> is not a master account. Only master accounts have passwords. To sign in, user the Basic Login page."))
            return(flask.redirect(flask.url_for('gatekeeperForgot')))
        params['reset_form_part'] = 2
        if flask.request.form.get('sec_a'):
            correct = auth_manager.verify(flask.request.form.get('sec_a'), sec_a)
            if correct:
                if flask.request.form.get('password'):
                    params['reset_form'] = auth_manager.PasswordResetForm(flask.request.form)
                else:
                    params['reset_form'] = auth_manager.PasswordResetForm()
                params['reset_sec_a'] = flask.request.form.get('sec_a')
                params['reset_form_part'] = 3
                params['btn_name'] = 'Reset'
                params['reset_form'] = auth_manager.PasswordResetForm(flask.request.form)
                if params['reset_form'].password.data == params['reset_form'].confirm.data:
                    try:
                        auth_manager.updatePassword(params['reset_username'], params['reset_form'].password.data)
                    except:
                        flask.flash('There was an error resetting your password. Try again later.', 'error')
                    else:
                        flask.flash('Your password has been reset. Please try signing in.', 'success')
                        return(flask.redirect(flask.url_for('gatekeeperSignInMaster')))
                else:
                    flask.flash('Passwords do not match', 'error')
            else:
                flask.flash('Incorrect security answer', 'error')
    return(flask.render_template('gatekeeper_forgot.htm', params=params))

@app.route('/gatekeeper/upgrade', methods=['GET', 'POST'])
@flask_login.login_required
def gatekeeperUpgrade():
    if flask_login.current_user.is_master:
        flask.flash('Your account is already a master account.', 'success')
        return(flask.redirect(flask.url_for('defaultPage')))
    params['register_form'] = auth_manager.AccountUpgradeForm(flask.request.form)
    if flask.request.method == 'POST' and params['register_form'].validate():
        try:
            auth_manager.upgradeUser(flask.session['username'], params['register_form']) 
        except Exception as e:
            flask.flash(str(e), 'error')
        else:
            flask.flash('Your account has been upgraded.', 'success')
            user = auth_manager.User(flask.session.pop('username'), None, is_authenticated=True)
            flask_login.logout_user()
            flask_login.login_user(user)
            return(flask.redirect(flask.url_for('defaultPage')))
    return(flask.render_template('gatekeeper_upgrade.htm', params=params))

@app.route('/about', methods=['GET'])
def aboutPage():
    return(flask.render_template('default.htm', params=params))


@login_manager.user_loader
def load_user(user_id):
    try:
        db = db_manager.DBQuery()
    except:
        flask.abort(500)
    username = db.getUsernameById(user_id)
    loginType = flask.session.get('login')
    if loginType != 'master':
        loginType = 'basic'
    flask.session['username'] = username
    try:
        user = auth_manager.User(username, None, is_authenticated=True, login_type=loginType)
        return(user)
    except AssertionError as e:
        flask.flash(str(e), 'error')
        return(flask.redirect(flask.url_for('gatekeeperSignInBasic')))

@app.before_request
def preflight():
    # Items to display in the navigation bar. I don't like having to use this dict but it is what it is
    params['navbar'] = dict()
    params['navbar']['Home'] = flask.url_for('defaultPage')
    if flask_login.current_user.is_authenticated:
        params['navbar']['Search'] = flask.url_for('searchPage')
        params['navbar']['My Lineup'] = flask.url_for('lineupPage')
        if flask_login.current_user.is_master:
            params['navbar']['Append'] = flask.url_for('appendPage')
            params['navbar']['Modify'] = flask.url_for('modifyPage')
        params['navbar']['Control Panel'] = flask.url_for('cpBase')
        if flask_login.current_user.is_admin:
            params['subnavbar'] = {
                'Home':flask.url_for('cpHome'),
                'Users':flask.url_for('cpUsers'),
                'Setup':flask.url_for('cpSetup')
            }
    params['navbar']['About'] = flask.url_for('aboutPage')
    

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    r.headers['X-Powered-By'] = 'ASP.NET'
    return(r)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
