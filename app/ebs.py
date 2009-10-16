#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License
#
# Copyright (c) 2009  Yesudeep Mangalapilly.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from hc_gae_util.collections.propertydict import PropertyDict
from hc_gae_util.encryption import arc4_decrypt
from base64 import b64decode
from urllib import urlencode
from hc_gae_util.urlhelper import urldecode
import re
from datetime import datetime


MODE_PRODUCTION = 'TEST'
MODE_DEVELOPMENT = 'TEST'

PAYMENT_GATEWAY_URL = 'https://secure.ebs.in/pg/ma/sale/pay/'

def replace_spaces_with_plus(string):
    return string.replace(' ', '+')

def get_request_parameters(encoded_data, encryption_key, decoder=b64decode, transformation=replace_spaces_with_plus):
    cipher_text = decoder(transformation(encoded_data))
    query_string = arc4_decrypt(encryption_key, cipher_text)
    query_params = urldecode(query_string)
    return query_params

def ebs_datetime(datetime_string):
    re_pattern = r'^(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2}) (?P<hours>[0-9]{2}):(?P<minutes>[0-9]{2}):(?P<seconds>[0-9]{2}).*$'
    compiled_re = re.compile(re_pattern)
    m = compiled_re.match(datetime_string)
    return datetime(*[int(i, 10) for i in m.groups()])

class Contact(PropertyDict):
    pass

class BillingContact(PropertyDict):
    pass

class ShippingContact(PropertyDict):
    def fields(self, *args, **kwargs):
        kwargs['prefix'] = 'ship_'
        return super(ShippingContact, self).fields(*args, **kwargs)

class BillingInformation(PropertyDict):
    pass

if __name__ == '__main__':
    bc = BillingContact(name='John Doe', phone='129382348', email='john@doe.com', address='postal address here, USA.', city='New York', postal_code='10010', state='CA', country='USA')
    sc = ShippingContact(name='John Smith', phone='129382348', email='john@doe.com', address='postal address here, USA.', city='New York', postal_code='10010', state='CA', country='USA')
    bi = BillingInformation(account_id='23848', reference_no='23492348', amount=21000, mode=MODE_DEVELOPMENT, description='hmmmmm.. hmmm.', return_url='/whatever/url/you/want')
    print bc.fields()
    print sc.fields()
    print bi.fields()
    #print urlencode(bi.fields())

