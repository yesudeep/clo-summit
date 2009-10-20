#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
from urlparse import urlsplit, urlunsplit

def url_join_path(base_url, path):
    u = urlsplit(base_url)
    return urlunsplit((u.scheme, u.netloc, path, u.query, u.fragment))


def urldecode(query):
   d = {}
   a = query.split('&')
   for s in a:
      if s.find('='):
         k,v = map(urllib.unquote, s.split('='))
         try:
            d[k].append(v)
         except KeyError:
            d[k] = [v]
   return d

