#!/usr/bin/python2.7

import os
import json
import twitter
import unittest
import MySQLdb

class TwitterTestCase(unittest.TestCase):


    def setUp(self):
        self.MYSQL_DATABASE_HOST = "localhost"
        self.MYSQL_DATABASE_USER = "twitter"
        self.MYSQL_DATABASE_PASSWORD = "DF7U7q2yy6pUPSn3"
        self.MYSQL_DATABASE_DB = "twitter"
        self.db = MySQLdb.connect(
            host=self.MYSQL_DATABASE_HOST,
            user=self.MYSQL_DATABASE_USER,
            passwd=self.MYSQL_DATABASE_PASSWORD,
            db=self.MYSQL_DATABASE_DB)
        self.c = self.db.cursor()
        self.c.execute("DELETE FROM friends WHERE userId=6 OR followingId = 6")
        twitter.app.config['TESTING'] = True
        self.app = twitter.app.test_client()
        self.urls = (
            "/user_timeline.json?token=%s&username=%s",
            "/friendslist.json?token=%s&username=%s",
            "/followerslist.json?token=%s&username=%s",
            "/createfriend.json?token=%s&username=%s",
            "/destroyfriend.json?token=%s&username=%s")
        self.user_timeline_url="/user_timeline.json?token=%s&username=%s"
        self.friendslist_url="/friendslist.json?token=%s&username=%s"
        self.followerslist_url="/followerslist.json?token=%s&username=%s"
        self.addfriend_url="/createfriend.json?token=%s&username=%s"
        self.destroyfriend_url="/destroyfriend.json?token=%s&username=%s"
        self.token="1234567890abcdef"

    #def tearDown(self):
        #do nothing

    def test_main_url(self):
        """Verifies that the main URL works"""
        rv = self.app.get('/')
        assert 'URLS' in rv.data

    def test_timeline_json_response(self):
        """Verifies JSON list of tweets are returned"""
        URL=self.user_timeline_url % (self.token, "test")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        assert "tweets" in rv.data
        assert rv.status_code == 200

    def test_friends_list_json_response(self):
        """Verifies JSON list of users is returned for all friends of a specified user"""
        URL=self.friendslist_url % (self.token, "test")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        assert "users" in rv.data
        assert rv.status_code == 200

    def test_followers_list_json_response(self):
        """Verifies JSON list of users is returned for all users following a specified user"""
        URL=self.followerslist_url % (self.token, "test")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        assert "users" in rv.data
        assert rv.status_code == 200

    def test_add_remove_friend_json_response(self):
        """Verifies a user can be added and removed as a friend"""
        URL=self.addfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        assert json_out['user']['username'] == "brian"
        assert rv.status_code == 200
        URL=self.destroyfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        assert json_out['user']['username'] == "brian"
        assert rv.status_code == 200

    def test_null_tokens(self):
        """Verifies a null token argument will not allow access to any API calls"""
        for url in self.urls:
            URL = url[:url.find('?')]
            rv = self.app.get(URL)
            assert rv.status_code == 401
        URL="/user_timeline.json"
        rv2 = self.app.get(URL)
        assert rv2.status_code == 401

    def test_invalid_tokens(self):
        """Verifies an invalid token will not allow access to any API calls"""
        for url in self.urls:
            URL = url % (self.token + "1", "test")
            rv = self.app.get(URL)
            assert rv.status_code == 401
        URL="/user_timeline.json"
        rv2 = self.app.get(URL)
        assert rv2.status_code == 401

    def test_default_user_from_api(self):
        """Verifies user of the specified token is defaulted to when no user is specified
         For the create/destroy calls, these end up both being Bad Requests"""
        for url in self.urls:
            URL = url % (self.token, "")
            URL1 = url % (self.token, "test")
            rv = self.app.get(URL)
            rv1 = self.app.get(URL)
            assert rv.data == rv1.data
            assert rv.status_code == rv.status_code

    def test_duplicate_add_fails(self):
        """Verifies adding a friend fails when they already exist"""
        URL=self.addfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        URL=self.addfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        assert rv.status_code == 400
        URL=self.destroyfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)

        
    def test_remove_nonexistant_user_fails(self):
        """Verifies removing a friend fails when they are not your friend"""
        URL=self.destroyfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        assert rv.status_code == 400

    def test_add_friend_view_tweets_only_of_friends(self):
        """Verifies only self-tweets and tweets of followers are visible on the given users timeline"""
        URL=self.user_timeline_url % (self.token, "test")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        for tweet in json_out['tweets']:
            assert tweet['username'] != "brian"

        URL=self.addfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        URL=self.user_timeline_url % (self.token, "test")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        found_tweets_from_brian = 0
        for tweet in json_out['tweets']:
            if tweet['username'] == "brian": found_tweets_from_brian+=1 
            assert tweet['username'] in ("test", "brian")
        assert found_tweets_from_brian != 0

        URL=self.destroyfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        
    def test_new_friend_updates_friendslist_properly(self):
        """Verifies new friends show up in the friends list"""
        URL=self.friendslist_url % (self.token, "test")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        for user in json_out['users']:
            assert user['username'] != "brian"

        URL=self.addfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        URL=self.friendslist_url % (self.token, "test")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        found_user_brian = 0
        for user in json_out['users']:
            if user['username'] == "brian": found_user_brian += 1
        assert found_user_brian != 0

        URL=self.destroyfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)


    def test_new_follower_updates_followers_properly(self):
        """Verifies new followers show up in the followers list"""
        URL=self.followerslist_url % (self.token, "test")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        for user in json_out['users']:
            assert user['username'] != "brian"

        URL=self.addfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        URL=self.followerslist_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)
        found_user_test = 0
        for user in json_out['users']:
            if user['username'] == "test": found_user_test += 1
        assert found_user_test != 0

        URL=self.destroyfriend_url % (self.token, "brian")
        rv = self.app.get(URL)
        json_out = json.loads(rv.data)

        
if __name__ == '__main__':
    unittest.main(verbosity=2)
