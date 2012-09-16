#!/usr/bin/python2.6
## monitor irc room for url. take url and paste them in backend. shorten url. comment. ask bot to replay last url.
## grab title of url

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
import sys
import re
import mechanize
import redis
import stock
import time
import random
import string
import ConfigParser
from chatterbotapi import ChatterBotFactory, ChatterBotType
import MySQLdb


config = ConfigParser.RawConfigParser()
config.read("teddy.cfg")

network = config.get('irc', 'network')
port = config.getint('irc', 'port')
channel = config.get('irc', 'channel')
nick = config.get('irc', 'nick')
name = config.get('irc', 'name')
key = config.get('irc', 'key')

dbhost = config.get('mysql', 'host')
dbuser = config.get('mysql', 'user')
dbpass = config.get('mysql', 'password')
dbname = config.get('mysql', 'name')

teddy_mute = 'no'
redis_server = redis.Redis(config.get('redis', 'host'))
factory = ChatterBotFactory()
teddy_brain = factory.create(ChatterBotType.CLEVERBOT)
teddy_session = teddy_brain.create_session()


class TeddyBot(irc.IRCClient):

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.setNick(self.factory.nickname)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel, self.factory.key)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""

    def gen_random_string(self):
        char_set = string.ascii_lowercase + string.digits
        return ''.join(random.sample(char_set,10))

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
        db=MySQLdb.connect(host=dbhost,user=dbuser,
                           passwd=dbpass,db=dbname)
        cur=db.cursor()
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
        san_msg = msg.replace('teddy','')
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
            if len(parse_last) == 2 :
                if source == 'jason' and parse_last[1] == 'mute':
                    teddy_mute = 'yes'
                    self.msg(channel, 'i will stop talking now ' + source)
                elif source == 'jason' and parse_last[1] == 'unmute':
                    teddy_mute = 'no'
                    self.msg(channel, 'lets talk ' + source)
            elif len(parse_last) == 3 and source == 'jason' and parse_last[1] == 'op':
                    connection.mode(channel, '+o '+ parse_last[2])
            elif len(parse_last) == 3 and source == 'jason' and parse_last[1] == 'kill':
                    connection.mode(channel, 'a '+ parse_last[2])
            else:
                self.msg(channel, 'hello ' + source)

        if msg.lower().startswith("!%s" % "all"):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2 :
                for url in self.url_by_source(parse_last[1]):
                    self.msg(source, url)

        if msg.lower().startswith("!%s" % "search"):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2 :
                for url in self.url_by_search(parse_last[1]):
                    self.msg(source, url)

        if msg.lower().startswith("!%s" % "last"):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2 :
               short = self.get_short_from_db('source', parse_last[1])
               title = self.get_title_from_db('short', short)
               self.msg(channel, title)
               self.msg(channel, "http://wgeturl.com/" + short)
            elif len(parse_last)==1 :
               short = self.get_short_from_db('source', source)
               title = self.get_title_from_db('short', short)
               self.msg(channel, title)
               self.msg(channel, "http://wgeturl.com/" + short)
            else :
                self.msg(channel, "!last username")

        if msg.lower().startswith("!%s" % "stock"):
            parse_last = re.split(' ', msg.strip())
            try:
                stock_data = stock.get(parse_last[1])
                self.msg(channel, stock_data)
            except:
                print "Unexpected error:", sys.exc_info()

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

        if re.search("http",msg.lower()) and source != 'wesley':
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

        if re.search("teddy",msg.lower()) and teddy_mute == 'no':
            try:
                teddy_response = self.teddy_ai(msg.lower())
                self.msg(channel, source + ": " + teddy_response)
            except:
                self.msg(channel, source + ": My brain is broken :(")
         
class TeddyBotFactory(protocol.ClientFactory):
    protocol = TeddyBot

    def __init__(self, channel, key, nick):
        self.channel = channel
        self.key = key
        self.nickname = nick

    def buildProtocol(self, addr):
        p = TeddyBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

if __name__ == '__main__':
    # create factory protocol and application
    bot = TeddyBotFactory(channel, key, nick)

    # connect factory to this host and port
    reactor.connectSSL(network, port, bot, ssl.ClientContextFactory())

    # run bot
    reactor.run()
