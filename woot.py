#!/bin/env python
#jason thomas
import requests
import json


def get(key, site='woot', event='Daily'):

    item = {}
    # this should make it easier for lookups
    sites = {
             'woot': 'www.woot.com',
             'wine': 'wine.woot.com',
            }
    eventt = event.title()

    api = "http://api.woot.com/2/events.json?site=%s&eventType=%s&key=%s" % (sites[site], eventt, key)
    request = requests.get(api)
    data = request.json()
    item['saleprice'] = data[0]['Offers'][0]['Items'][0]['SalePrice']
    item['listprice'] = data[0]['Offers'][0]['Items'][0]['ListPrice']
    item['title'] = data[0]['Offers'][0]['Items'][0]['Title'].strip()
    item['url'] = data[0]['Offers'][0]['OfferUrl']

    return item
