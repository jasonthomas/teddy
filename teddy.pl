#!/bin/env python
## monitor irc room for url. take url and paste them in backend. shorten url. comment. ask bot to replay last url.
## grab title of url

import ircbot
import sys
import re
import mechanize
import memcache

network = '127.0.0.1'
port = 6667
channel = '#chat'
nick = 'teddy'
name = 'teddy'

statistics = {}


class TeddyBot (ircbot.SingleServerIRCBot):
    def on_welcome (self, connection, event):
        connection.join ( channel )

    def memcache_write(self, key, value):
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        mc.set(key,value)

    def memcache_read(self, key):
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        return mc.get(key)

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
               connection.privmsg(channel, self.memcache_read(parse_last[1]))
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
                self.memcache_write(source,msg)
                connection.privmsg(channel, browser.title())
            except IOError:
                connection.privmsg(channel, "jason didnt design me with proper logic")
            except:
                connection.privmsg(channel, source + " what did you send me?")
         
bot = TeddyBot ([( network, port )], nick, name)
bot.start() 
