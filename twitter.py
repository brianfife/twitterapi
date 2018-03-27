#!/usr/bin/python2.7

from functools import wraps
from flask import Flask, request, jsonify, Response, abort, json

import MySQLdb, collections

app = Flask(__name__)

MYSQL_DATABASE_HOST = "127.0.0.1"
MYSQL_DATABASE_USER = "twitter"
MYSQL_DATABASE_PASSWORD = "DF7U7q2yy6pUPSn3"
MYSQL_DATABASE_DB = "twitter"


db = MySQLdb.connect(host=MYSQL_DATABASE_HOST, user=MYSQL_DATABASE_USER, passwd=MYSQL_DATABASE_PASSWORD, db=MYSQL_DATABASE_DB)

def run_query(q):
  c = db.cursor()
  size = c.execute(q)
  return size, c

@app.route('/twitter.py')
def ret_twitter_source():
  return "<pre>" + open('twitter.py', 'r').read() + "</pre>"

@app.route('/testsuite.py')
def ret_testsuite_source():
  return "<pre>" + open('testsuite.py', 'r').read() + "</pre>"

@app.route('/schema.sql')
def ret_schema_source():
  return "<pre>" + open('schema.sql', 'r').read() + "</pre>"

@app.route('/')
def hello():
  out = """
<pre>URLS
<a href=/user_timeline.json>User Timeline</a> params: token, username (optional, defaults to users token)
<a href=/friendslist.json>Friends List</a> params: token, username (optional, defaults to users token)
<a href=/followerslist.json>Followers List</a> params: token, username (optional, defaults to users token)
<a href=/createfriend.json>Add Friend</a> params: token, username
<a href=/destroyfriend.json>Destroy Friend</a> params: token, username
<a href=/tweet.json>Add tweet</a> (not tested) params: token, message

append query string token=<token> for user-context token
append query string username=<desired user> to query parameters about

i.e. /friendslist.json?token=1b43ef1e0618de6d&username=brian

<a href=/twitter.py>twitter.py source</a>
<a href=/testsuite.py>testsuite.py source</a>
<a href=/schema.sql>database schema</a>


"""
  query = "SELECT username, token FROM users"
  size, ret = run_query(query)
  rows = ret.fetchall()
  for row in rows:
    out += "User: %s, Token: %s\n" % (row[0], row[1])
  out += "</pre>"
  return out


@app.route('/user_timeline.json')
def get_tweets():
  """Returns JSON-encoded list of tweets belonging to the specified username, and their friends
     If no username is specified, default to the authenticating user
     Returns HTTP Error 400 if given username doesn't exist"""
  auth_user = verify_token(get_req_args_or_fail('token', 401))
  target_user = ""
  if check_None_or_empty(request.args.get('username', None)):
    target_user = auth_user
  else:
    target_user = get_req_args_or_fail('username')
  get_userid(target_user)
  query = "SELECT timestamp, users.username, messageId, message FROM tweets LEFT JOIN users ON users.id = tweets.userId WHERE tweets.userId  = ANY (SELECT id FROM users WHERE username = '%s' UNION SELECT friends.followingId FROM users JOIN friends ON friends.userId = users.id WHERE users.username = '%s') ORDER BY timestamp DESC" % (target_user, target_user)
  size, ret = run_query(query)
  tweets = []
  rows = ret.fetchall()
  for row in rows:
    d = collections.OrderedDict()
    d['timestamp'] = row[0].isoformat()
    d['username'] = row[1]
    d['messageId'] = row[2]
    d['tweet'] = row[3]
    tweets.append(d)
  return jsonify(tweets=tweets)


@app.route('/friendslist.json')
def get_friends():
  """Returns a list of users the specified username is friends with
     If no username is specified, default to the authenticating user
     Returns HTTP Error 400 if given username doesn't exist"""
  auth_user = verify_token(get_req_args_or_fail('token', 401))
  target_user = ""
  if check_None_or_empty(request.args.get('username', None)):
    target_user = auth_user
  else:
    target_user = get_req_args_or_fail('username')
  get_userid(target_user)
  query = "SELECT id, username FROM users WHERE id IN (SELECT friends.followingId FROM users JOIN friends ON friends.userId = users.id WHERE users.username = '%s')" % target_user
  size, ret = run_query(query)
  friends = []
  rows = ret.fetchall()
  for row in rows:
    d = collections.OrderedDict()
    d['id'] = row[0]
    d['username'] = row[1]
    friends.append(d)
  return jsonify(users=friends)

@app.route('/followerslist.json')
def get_followers():
  """Returns a list of users who follow the specified username
     If no username is specified, default to the authenticating user
     Returns HTTP Error 400 if given username doesn't exist"""
  auth_user = verify_token(get_req_args_or_fail('token', 401))
  target_user = ""
  if check_None_or_empty(request.args.get('username', None)):
    target_user = auth_user
  else:
    target_user = get_req_args_or_fail('username')
  get_userid(target_user)
  query = "SELECT id, username FROM users WHERE id IN (SELECT friends.userId FROM users JOIN friends ON friends.followingId = users.id WHERE users.username = '%s')" % target_user
  size, ret = run_query(query)
  followers = []
  rows = ret.fetchall()
  for row in rows:
    d = collections.OrderedDict()
    d['id'] = row[0]
    d['username'] = row[1]
    followers.append(d)
  return jsonify(users=followers)

@app.route('/tweet.json')
def add_tweet():
  """EXPERIMENTAL Add tweet for the authenticating user"""
  auth_user = verify_token(get_req_args_or_fail('token', 401))
  message = get_req_args_or_fail('message')
  userid = get_userid(auth_user)
  query = "INSERT into tweets (userId, message) VALUES ('%i', '%s')" % (userid, message)
  try:
    size, ret = run_query(query)
  except:
    abort(400)
  return jsonify(tweet={'status': "Success!"})


@app.route('/createfriend.json')
def add_friend():
  """Adds the specified username to the authenticating users friends list
  Returns HTTP Erorr 400 if username is None, an empty string, the authenticating user or a non-existant user
  Returns the user id and username upon successful friending"""
  auth_user = verify_token(get_req_args_or_fail('token', 401))
  target_user = get_req_args_or_fail('username')
  if target_user == auth_user: abort(400)
  userid = get_userid(auth_user)
  target_userid = get_userid(target_user)
  query = "INSERT into friends (userId, followingId) VALUES ('%i', '%i')" % (userid, target_userid)
  try:
    size, ret = run_query(query)
  except:
    abort(400)
  d = collections.OrderedDict()
  d['id'] = target_userid
  d['username'] = target_user
  return jsonify(user=d)

@app.route('/destroyfriend.json')
def remove_friend():
  """Removes the specified username from the authenticating users friends list
  Returns HTTP Erorr 400 if username is None, an empty string, the authenticating user or a non-existant user
  Returns the user id and username upon successful removing"""
  auth_user = verify_token(get_req_args_or_fail('token', 401))
  target_user = get_req_args_or_fail('username')
  if target_user == auth_user: abort(400)
  userid = get_userid(auth_user)
  target_userid = get_userid(target_user)
  query = "DELETE FROM friends where userId = '%i' AND followingId = '%i'" % (userid, target_userid)
  size, ret = run_query(query)
  if size == 0: abort(400)
  d = collections.OrderedDict()
  d['id'] = target_userid
  d['username'] = target_user
  return jsonify(user=d)

def get_userid(user):
  """Simple statement to retrieve a given users id
  Throw an HTTP Error 400 if the user doesn't exist"""
  query = "SELECT id FROM users WHERE username = '%s'" % user
  size, ret = run_query(query)
  if size != 1:
    abort(400)
  uid = ret.fetchone()[0]
  return uid

def get_req_args_or_fail(attribute, abortCode=400):
  """Retrieves query string parameters and verifies they are not None/empty
  Returns the value if succesful, or throws an HTTP Error code (400 by default)"""
  value = request.args.get(attribute, None)
  if check_None_or_empty(value): abort(abortCode)
  return MySQLdb.escape_string(value)

def check_None_or_empty(string):
  """Returns True if the string is None or empty, False otherwise"""
  if string is None or string == "": return True
  return False

def verify_token(token):
  """Verifies a user API token is valid
  Returns the authenticating username, or throws an HTTP Error 401 Authorization Denied"""
  query = "SELECT username FROM users WHERE token = '%s'" % token
  size, ret = run_query(query)
  if size == 0: abort(401)
  if size == 1: 
    return ret.fetchone()[0]
  abort(401)

if __name__ == "__main__":
  app.debug = True
  app.run(host="0.0.0.0")
