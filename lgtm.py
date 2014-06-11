#!/bin/env python2.6
#jason thomas
import mechanize
import re

def get():
  br = mechanize.Browser()
  br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
  lgtm_api = "http://www.lgtm.in/g"

  br.open(lgtm_api)
  link = list(br.links())[6]

  br.open(link.url)
  br.select_form(nr=0)

  return br.form.controls[0].value
