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

network = '127.0.0.1'
port = 6667
channel = '#chat'
nick = 'teddy'
name = 'teddy'

redis_server = redis.Redis("192.168.0.70")

class TeddyBot (ircbot.SingleServerIRCBot):
    def on_welcome (self, connection, event):
        connection.join ( channel )

    def gen_random_string(self):
        char_set = string.ascii_lowercase + string.digits
        return ''.join(random.sample(char_set,10))

    def redis_write(self, source, url, title):
        short = self.gen_random_string()
        redis_server.hset(url, "short", short)
        redis_server.hset(url, "title", title)
        redis_server.hset(url, "source", source)
        redis_server.hset(url, "time", time.gmtime())

    def redis_write_last(self, key, value):
        redis_server.set(key,value)

    def redis_read_last(self, key):
        return redis_server.get(key)

    def on_pubmsg (self, connection, event):
        source = event.source().split ('!') [0]
        channel = event.target()
        msg = event.arguments()[0]
        
        if msg.lower().startswith("!%s" % self._nickname):
            connection.privmsg(channel, 'hello ' + source)
        if msg.lower().startswith("!%s" % "penis"):
            connection.privmsg(channel, source + ' loves the pee pee')
        if msg.lower().startswith("!%s" % "last"):
            parse_last = re.split(' ', msg.strip())
            if len(parse_last) == 2 :
               connection.privmsg(channel, self.redis_read_last(parse_last[1]))
            else :
                connection.privmsg(channel, "!last username")
        if msg.lower().startswith("!%s" % "dance"):
            connection.privmsg(channel, ":D\<")
            connection.privmsg(channel, ":D|<")
            connection.privmsg(channel, ":D/<")
            connection.privmsg(channel, ":D|<")
        if msg.lower().startswith("http"):
            try:
                browser = mechanize.Browser()
                browser.open(msg)
                self.redis_write(source,msg,browser.title())
                self.redis_write_last(source,msg)
                connection.privmsg(channel, browser.title())
            except IOError:
                connection.privmsg(channel, "jason didnt design me with proper logic")
           # except:
            #    connection.privmsg(channel, source + " what did you send me?")
         
bot = TeddyBot ([( network, port )], nick, name)
bot.start() 
