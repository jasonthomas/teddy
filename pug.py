#!/bin/env python
#jason thomas
import mechanize
import json


def get():
    endpoint = 'http://pugme.herokuapp.com/random'
    response = json.loads(mechanize.urlopen(endpoint).read())
    return response['pug']
