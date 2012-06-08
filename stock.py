#!/bin/env python2.6
#jason thomas
import mechanize
import json
import re

def get(name):
  stock_api = "http://finance.google.com/finance/info?client=ig&q=%s" % name
  response = mechanize.urlopen(stock_api)
  clean = re.sub('[\[\]/]', '',response.read())
  data = json.loads(clean)
  stock_data = "%s @ %s %s - %s" % (data['t'], data['l_cur'], data['c'],  data['lt'])
  return stock_data
