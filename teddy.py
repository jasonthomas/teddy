#!/bin/env python
## monitor irc room for url. take url and paste them in backend. shorten url. comment. ask bot to replay last url.
## grab title of url

import ircbot
import sys
import re
import mechanize
import redis
import time
import random
import string
import ConfigParser
import eliza



config = ConfigParser.RawConfigParser()
config.read("teddy.cfg")

network = config.get('irc', 'network')
port = config.getint('irc', 'port')
channel = config.get('irc', 'channel')
nick = config.get('irc', 'nick')
name = config.get('irc', 'name')

redis_server = redis.Redis(config.get('redis', 'host'))

class TeddyBot (ircbot.SingleServerIRCBot):
    def on_welcome (self, connection, event):
        connection.join ( channel )

    def gen_random_string(self):
        char_set = string.ascii_lowercase + string.digits
        return ''.join(random.sample(char_set,10))

    def parse_url(self, msg):
        browser = mechanize.Browser()
        browser.open(msg)
        return browser.title()

    def redis_exists(self, key, value):
        if redis_server.hexists(key, value):
            return 1
        else:
            return 0

    def redis_get_value(self, key, value):
        if self.redis_exists(key, value):
            return redis_server.hget(key, value);
        else:
            return () 

    def redis_read_last(self, key):
        return redis_server.get(key)

    def redis_write(self, source, url, title):
        if not self.redis_exists(url, title):
            short = self.gen_random_string()
            redis_server.hset(url, "short", short)
            redis_server.hset(url, "title", title)
            redis_server.hset(url, "source", source)
            redis_server.hset(url, "time", time.gmtime())

    def redis_write_last(self, key, value):
        redis_server.set(key,value)

    def teddy_ai(self, msg):
        teddy_brain = eliza.eliza()
        return teddy_brain.respond(msg)

    def on_pubmsg (self, connection, event):
        source = event.source().split ('!') [0]
        channel = event.target()
        msg = event.arguments()[0]
        
        if msg.lower().startswith("!%s" % self._nickname):
            connection.privmsg(channel, 'hello ' + source)
        if msg.lower().startswith("!%s" % "penis"):
            connection.privmsg(channel, source + ' what are you saying ??')
        if msg.lower().startswith("!%s" % "last"):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2 :
               url = self.redis_read_last(parse_last[1])
               title = self.redis_get_value(url,"title")
               connection.privmsg(channel, url)
               connection.privmsg(channel, title)
            else :
                connection.privmsg(channel, "!last username")

        if msg.lower().startswith("!%s" % "dance"):
            connection.privmsg(channel, ":D\<")
            connection.privmsg(channel, ":D|<")
            connection.privmsg(channel, ":D/<")
            connection.privmsg(channel, ":D|<")

        if msg.lower().startswith("!%s" % "angrydance"):
            connection.privmsg(channel, ">\D:")
            connection.privmsg(channel, ">|D:")
            connection.privmsg(channel, ">/D:")
            connection.privmsg(channel, ">|D:")
        if re.search("http",msg.lower()):
            try:
                parse_string = msg[msg.find("http://"):]
                parse_string  = parse_string.strip()
                title = self.parse_url(parse_string)
                self.redis_write_last(source, parse_string)
                self.redis_write(source, parse_string, title)
                connection.privmsg(channel, title)
            except IOError:
                connection.privmsg(channel, "jason didnt design me with proper logic")
            except:
                connection.privmsg(channel, source + " what did you send me?")
        if re.search("teddy",msg.lower()):
            teddy_response = self.teddy_ai(msg.lower())
            connection.privmsg(channel, source + ": " + teddy_response)
         
bot = TeddyBot ([( network, port )], nick, name)
bot.start() 
