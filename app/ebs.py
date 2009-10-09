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
from urllib import urlencode

MODE_PRODUCTION = 'TEST'
MODE_DEVELOPMENT = 'TEST'

PAYMENT_GATEWAY_URL = 'https://secure.ebs.in/pg/ma/sale/pay/'

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

