#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from google.appengine.api import memcache, urlfetch
from countries import COUNTRY_ISO_ALPHA_TABLE

logging.basicConfig(level=logging.INFO)

def ip_address_to_country_code(ip_address, default_country_code='ZZZ'):
    '''
    Uses an external service to map an IP address to its country.
    '''
    url = 'http://abusebutler.appspot.com/loc/%s' % ip_address

    result_country_code = memcache.get('geoiplocator:' + url)
    if not result_country_code:
        result_country_code = default_country_code
        try:
            result = urlfetch.fetch(url)
            if result and result.status_code == 200:
                alpha_2_iso_country_code = result.content.strip()
                if alpha_2_iso_country_code:
                    #logging.info(alpha_2_iso_country_code)
                    result_country_code = COUNTRY_ISO_ALPHA_TABLE.get(alpha_2_iso_country_code, default_country_code)
                    #logging.info(result_country_code)
                    memcache.set(url, result_country_code)
            else:
                result_country_code = default_country_code
        except urlfetch.DownloadError:
            result_country_code = default_country_code
    return result_country_code

