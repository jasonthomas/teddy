#!/bin/env python
## monitor irc room for url. take url and paste them in backend. shorten url. comment. ask bot to replay last url.
## grab title of url

import ircbot
import sys
import re
import mechanize

network = '127.0.0.1'
port = 6667
channel = '#chat'
nick = 'teddy'
name = 'teddy'

statistics = {}


class TeddyBot (ircbot.SingleServerIRCBot):
    def on_welcome (self, connection, event):
        connection.join ( channel )

    def on_pubmsg ( self, connection, event ):
        source = event.source().split ('!') [0]
        channel = event.target()
        msg = event.arguments()[0]
        
        if msg.lower().startswith("!%s" % self._nickname):
            connection.privmsg(channel, 'hello ' + source)
        if msg.lower().startswith("!%s" % "penis"):
            connection.privmsg(channel, source + ' loves the pee pee')
        if msg.lower().startswith("!%s" % "dance"):
            connection.privmsg(channel, ":D\<")
            connection.privmsg(channel, ":D|<")
            connection.privmsg(channel, ":D/<")
            connection.privmsg(channel, ":D|<")
        if msg.lower().startswith("http:"):
            try:
                browser = mechanize.Browser()
                browser.open(msg)
                connection.privmsg(channel, browser.title())
            except IOError:
                connection.privmsg(channel, "jason didnt design me with proper logic")
bot = TeddyBot ([( network, port )], nick, name)
bot.start() 
