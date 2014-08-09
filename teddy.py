# -*- coding: utf-8 -*
#!/usr/bin/python2.6
## monitor irc room for url. take url and paste them in backend. shorten url. comment. ask bot to replay last url.
## grab title of url

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from chatterbotapi import ChatterBotFactory, ChatterBotType
from pug import get as getpug
from lgtm import get as getlgtm
from reddit import get as getreddit
from score import Score
import sys
import re
import mechanize
import redis
import stock
import time
import random
import string
import MySQLdb
import woot
import upsidedown

import settings

networks = settings.NETWORKS
identity = settings.IDENTITY

dbhost = settings.MYSQL_HOST
dbuser = settings.MYSQL_USER
dbpass = settings.MYSQL_PASSWORD
dbname = settings.MYSQL_DB
woot_key = settings.WOOT_KEY

teddy_mute = 'no'
redis_server = redis.Redis(settings.REDIS_HOST)

factory = ChatterBotFactory()
teddy_brain = factory.create(ChatterBotType.JABBERWACKY)
teddy_session = teddy_brain.create_session()
score = Score(dbhost, dbuser, dbpass, dbname)


class TeddyBot(irc.IRCClient):
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        print('teddy bot signed on')

        network = self.factory.network

        if network['identity']['nickserv_pw']:
            self.msg('NickServ',
                     'IDENTIFY %s' % network['identity']['nickserv_pw'])

        for channel, key in network['autojoin']:
            print('join channel %s' % channel)
        if key:
                self.join(channel, key)
        else:
                self.join(channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""

    def _get_nickname(self):
        return self.factory.network['identity']['nickname']

    def _get_realname(self):
        return self.factory.network['identity']['realname']

    def _get_username(self):
        return self.factory.network['identity']['username']

    nickname = property(_get_nickname)
    realname = property(_get_realname)
    username = property(_get_username)

    def gen_random_string(self):
        char_set = string.ascii_lowercase + string.digits
        return ''.join(random.sample(char_set, 10))

    def get_title(self, url):
        browser = mechanize.Browser()
        browser.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2')]
        try:
            browser.open(url)
            return browser.title()
        except:
            print "Unexpected error:", sys.exc_info()

    def get_title_from_db(self, key, value):
        clean_value = MySQLdb.escape_string(key)
        sql = """SELECT title from redirect_url where %s='%s'""" % (key, value)
        return self.query_mysql(sql)

    def get_short_from_db(self, key, value):
        sql = """SELECT short from redirect_url where %s='%s' ORDER BY timestamp DESC LIMIT 1""" % (key, value)
        return self.query_mysql(sql)

    def query_mysql(self, query):
        db = MySQLdb.connect(host=dbhost, user=dbuser,
                             passwd=dbpass, db=dbname)
        cur = db.cursor()
        try:
            cur.execute(query)
            db.commit()
            if int(cur.rowcount) == 1:
                return cur.fetchone()[0]
            else:
                return cur.fetchall()
        except:
            db.rollback()

    def write_url_to_db(self, source, url):
        short = self.get_short_from_db("url", url)
        if len(short) == 0:
            title = self.get_title(url)
            clean_title = MySQLdb.escape_string(title)
            short = self.gen_random_string()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            sql = """INSERT INTO redirect_url (short, url, title, source, timestamp) VALUES ("%s", "%s", "%s", "%s", "%s")""" % (short, url, clean_title, source, timestamp)
            self.query_mysql(sql)
            return short
        else:
            return short

    def teddy_ai(self, msg):
        global teddy_brian
        san_msg = msg.replace('teddy', '')
        return teddy_session.think(san_msg)

    def url_by_source(self, source):
        myurl = []
        for url in redis_server.keys('http*'):
            if redis_server.hget(url, 'source') == source:
                myurl.append(url)
        return myurl

    def url_by_search(self, searchstr):
        myurl = []
        for url in redis_server.keys('http*'):
            if re.search(searchstr, url.lower()):
                myurl.append(url)
        return myurl

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        source = user.split('!', 1)[0]
        global teddy_mute

        if msg.lower().startswith("!%s" % self.nickname):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2:
                if source == 'jason' and parse_last[1] == 'mute':
                    teddy_mute = True
                    self.msg(channel, 'i will stop talking now ' + source)
                elif source == 'jason' and parse_last[1] == 'unmute':
                    teddy_mute = False
                    self.msg(channel, 'lets talk ' + source)

        if msg.lower().startswith("!%s" % "all"):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2:
                for url in self.url_by_source(parse_last[1]):
                    self.msg(source, url)

        if msg.lower().startswith("!%s" % "search"):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2:
                for url in self.url_by_search(parse_last[1]):
                    self.msg(source, url)

        if msg.lower().startswith("!%s" % "last"):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2:
                short = self.get_short_from_db('source', parse_last[1])
                title = self.get_title_from_db('short', short)
                self.msg(channel, title)
                self.msg(channel, "http://wgeturl.com/" + short)
            elif len(parse_last) == 1:
                short = self.get_short_from_db('source', source)
                title = self.get_title_from_db('short', short)
                self.msg(channel, title)
                self.msg(channel, "http://wgeturl.com/" + short)
            else:
                self.msg(channel, "!last username")

        if msg.lower().startswith("!%s" % "stock"):
            parse_last = re.split(' ', msg.strip())
            try:
                stock_data = stock.get(parse_last[1])
                self.msg(channel, stock_data)
            except:
                print "Unexpected error:", sys.exc_info()

        if msg.lower().startswith("!%s" % "flip"):
            parse_last = msg.strip()[6:]
            parse_last = msg.strip().lstrip('!flip ')
            angry = '(╯°□°)╯︵'

            if parse_last:
                flip = upsidedown.transform(parse_last)
                flipit = '%s %s' % (angry, flip.encode('utf-8'))
            else:
                flipit = '%s %s' % (angry, '┻━┻ ')

            try:
                self.msg(channel, flipit)
            except:
                print "Unexpected error:", sys.exc_info()

        if msg.lower().startswith("!%s" % "moofi"):
            parse_last = re.split(' ', msg.strip())
            try:
                items = woot.get(woot_key, event='moofi')
                for item in items:
                    output = "%s - Sale:$%s List:$%s" % (item['title'], item['saleprice'], item['listprice'])
                    short = self.write_url_to_db(source, item['url'])
                    self.msg(channel, output)
                    self.msg(channel, "http://wgeturl.com/" + short)
            except:
                print "Unexpected error:", sys.exc_info()

#       if msg.lower().startswith("!%s" % "woot"):
#           parse_last = re.split(' ', msg.strip())
#           try:
#               item = woot.get(woot_key)
#               output = "%s - Sale:$%s List:$%s" % (item['title'], item['saleprice'], item['listprice'])
#               short = self.write_url_to_db(source, item['url'])
#               self.msg(channel, output)
#               self.msg(channel, "http://wgeturl.com/" + short)
#           except:
#               print "Unexpected error:", sys.exc_info()

        if "pug me" in msg.lower():
            self.msg(channel, getpug())

        if "lgtm" in msg.lower():
            self.msg(channel, getlgtm())

        if "tits" in msg.lower():
            self.msg(channel, getreddit('tits'))

        if msg.lower().startswith("!r"):
            m = re.search('!r\W(.*)', msg.lower())
            self.msg(channel, getreddit(m.group(1)))

        if msg.lower().endswith('++'):
            m = re.search('(.*)\+\+', msg.lower())
            score.increment(m.group(1))

        if msg.lower().endswith('--'):
            m = re.search('(.*)\-\-', msg.lower())
            score.decrement(m.group(1))

        if msg.lower().startswith('!score'):
            user_score_name = re.split(' ', msg.strip())[1]
            try:
                user_score = score.get_score(user_score_name)
                self.msg(channel, 'User %s has %s points' % (user_score_name, user_score))

        if msg.lower().startswith("!%s" % "dance"):
            self.msg(channel, ":D\<")
            self.msg(channel, ":D|<")
            self.msg(channel, ":D/<")
            self.msg(channel, ":D|<")

        if msg.lower().startswith("!%s" % "angrydance"):
            self.msg(channel, ">\D:")
            self.msg(channel, ">|D:")
            self.msg(channel, ">/D:")
            self.msg(channel, ">|D:")

        if re.search("http", msg.lower()) and source != 'wesley':
            try:
                parse_string = msg[msg.find("http"):]
                url = parse_string.strip()
                short = self.write_url_to_db(source, url)
                title = self.get_title_from_db('short', short)
                self.msg(channel, title)
                if (len(parse_string) >= 29):
                    self.msg(channel, "http://wgeturl.com/" + short)
            except:
                print "Unexpected error:", sys.exc_info()

        if re.search("teddy", msg.lower()) and not teddy_mute):
            try:
                teddy_response = self.teddy_ai(msg.lower())
                self.msg(channel, source + ": " + teddy_response)
            except:
                self.msg(channel, source + ": My brain is broken :(")


class TeddyBotFactory(protocol.ClientFactory):
    protocol = TeddyBot

    def __init__(self, network_name, network):
        self.network_name = network_name
        self.network = network

    def clientConnectionLost(self, connector, reason):
        print('client connection lost')
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print('client connection failed')
        reactor.stop()

if __name__ == '__main__':
    for name in networks.keys():
        factory = TeddyBotFactory(name, networks[name])

        host = networks[name]['host']
        port = networks[name]['port']

        if networks[name]['ssl']:
            reactor.connectSSL(host, port, factory, ssl.ClientContextFactory())
        else:
            reactor.connectTCP(host, port, factory)

    reactor.run()
