# Challenge

Create a twitter like api service with the following basic functionality:

1. a call to read the tweets for a given user (include self-tweets and people being followed by user)
2. a call to get the list of people a user is following as well as the followers of the user
3. a call to start following a user
4. a call to unfollow a user

Please make sure all calls are guarded with an API token in the query string that will serve to authenticate the calls (this can be a 16-character alphanumeric sequence); if the wrong API token is given, a 401 error is thrown (unauthorized).

The output can be in either json or xml format (or both).

# Solution

I implemented the API using python-flask and MySQLdb libraries.

I used an index page which lists all of the URLs (including bonus tweeting), and a list of users and their associated API token.  The source for the twitter.py, testsuite.py and schema.sql can also be viewed from the running flask server.

For the timeline, friends and followers list, I decided that if a target username is not specified, the authenticating user is substituted in its place.  Requests with invalid data will resort in HTTP Error 400 (Bad Request), unless it is a failure related to the token - these result in HTTP Error 401.

I wrote some basic integration testing using the Werkzeug test client that Flask provides.  All tests are performed authenticating as the user "test".  Adding/removing of a friend is always performed against the user "brian".  The friends list of user "test" is always purged before any tests, so that subsequent tests would continue if one were to fail.  I set verbosity=2 on the tests so that their comments would be outputted during execution.  I am using MySQLdb.escape_string() on query strings, but I did not write any coverage to ensure SQL injections are prevented.

# Setup

1. Restore the schema; it will create a database named 'twitter'.  With great power comes great responsibility; don't blindly run unknown files as root without looking at them!
```
mysql -u root -p  < schema.sql
```

Add a user 'twitter' on localhost, identified by the same password which is stored in twitter.py
```
grant INSERT, SELECT, DELETE, UPDATE ON twitter.* to  'twitter'@'localhost' identified by 'DF7U7q2yy6pUPSn3';
flush privileges;
```
