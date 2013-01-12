#!/bin/env python
#jason thomas
import requests
import json


def get(key, site='woot', event='Daily'):

    # this should make it easier for lookups
    items=[]
    sites = {
             'woot': 'www.woot.com',
             'wine': 'wine.woot.com',
            }
    eventt = event.title()

    api = "http://api.woot.com/2/events.json?site=%s&eventType=%s&key=%s" % (sites[site], eventt, key)
    request = requests.get(api)
    data = request.json()
    for offer in data:
        item = {}

        item['saleprice'] = offer['Offers'][0]['Items'][0]['SalePrice']
        item['listprice'] = offer['Offers'][0]['Items'][0]['ListPrice']
        item['title'] = offer['Offers'][0]['Items'][0]['Title'].strip()
        item['url'] = offer['Offers'][0]['OfferUrl']

        items.append(item)
    return items
