#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python EBS-Integration Kit.
# Copyright (C) 2009  Yesudeep Mangalapilly.
#
# The MIT License
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

from base64 import b64decode
from Crypto.Cipher import ARC4
from datetime import datetime
from decimal import Decimal, InvalidOperation

import re
import urllib

EBS_DATESTRING_RE = re.compile(r'^(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2}) (?P<hours>[0-9]{2}):(?P<minutes>[0-9]{2}):(?P<seconds>[0-9]{2}).*$')


def parse_ebs_datetime(datestring, compiled_re=EBS_DATESTRING_RE):
    """
        Parses an EBS-provided datetime string into a Python datetime object.

        Warning:
    1.  Uses regular expressions.
    2.  EBS does not send TZ info so we do not assume any timezone.
        It is your responsibility to pick the correct one.
    """
    m = compiled_re.match(datestring)
    return datetime(*[int(i, 10) for i in m.groups()])

def get_ebs_typed_value(v):
    """
        Returns a typed_values value for a given string of text.

        "true"  -> True
        "yes"   -> True
        "no     -> False
        "faLSe" -> False      <= Case does not matter in all above cases.

        "0"          -> 0
        "2938423984" -> 2938423984
        "23.45"      -> Decimal("23.45")
    """

    try:
        value = parse_ebs_datetime(v)
    except AttributeError:
        try:
            value = int(v, 10)
        except ValueError:
            try:
                value = Decimal(v)
            except InvalidOperation:
                s_v = v.lower()
                if s_v in ['true', 'yes']:
                    value = True
                elif s_v in ['false', 'no']:
                    value = False
                else:
                    value = v
    return value

def urldecode(query, flatten_values=True, typed_values=True, \
        typed_value_getter=get_ebs_typed_value, key_value_pair_separator='&', key_value_separator='='):
    """
        Deserializes a query string into a dictionary of key-value pairs.

        Parameters::

        flatten_values
            A query string may contain multiple values for the same key.
            For example, in the query string::

                a=mask&b=cadr&a=down

            the key `a' has multiple values.  This function will return
            a dictionary with values as lists containing actual query values
            if you set flatten_values to False.  By default, the values will be
            flattened as in the example below::

                unflattened:

                    {'a': ['mask', 'down'],
                     'b': ['cadr']}             <= Note this line.

                flattened:

                    {'a': ['mask', 'down'],
                     'b': 'cadr'}               <= Note this line.

        typed_values
            When True (default), converts all possible type-able values
            to their proper types to make it easier for you to process them.
            For example, with typed_values set to True, passing in the query string::

                term=extreme%20masochism&lang=en&len=25&hex=false

            will make the function return::

                {'term': 'extreme masochism',
                 'lang': 'en',
                 'len': 25,
                 'hex': False}

    """
    query_params = {}
    query_key_value_pairs = query.split(key_value_pair_separator)
    for s in query_key_value_pairs:
        if s.find(key_value_separator):
            k, v = map(urllib.unquote_plus, s.split(key_value_separator))
            if typed_values:
                v = typed_value_getter(v)
            try:
                query_params[k].append(v)
            except KeyError:
                query_params[k] = [v]
    if flatten_values:
        for k, v in query_params.iteritems():
            if len(v) == 1:
                query_params[k] = v[0]
    return query_params


def arc4_encrypt(key, data):
    """
        Encrypts a body of text using Alleged-RC4 (Ron's Code 4) secret-key encryption.

        key
            secret key

        data
            data to encrypt
    """
    encryptor = ARC4.new(key)
    return encryptor.encrypt(data)


def arc4_decrypt(key, data):
    """
        Decrypts a body of text from Alleged-RC4 (Ron's Code 4) encrypted data.

        key
            secret key

        data
            data to decrypt
    """
    decryptor = ARC4.new(key)
    return decryptor.decrypt(data)


def replace_spaces_with_plus(string):
    """
        Transformation to replace all space ( ) characters in a string
        with the plus (+) character.
    """
    return string.replace(' ', '+')


def get_ebs_request_parameters(encoded_data, encryption_key, flatten_values=True, typed_values=True, \
        decoder=b64decode, transformation=replace_spaces_with_plus):
    """
        Given encoded transaction data from EBS and your EBS-assigned encryption
        key returns a dictionary of HTTP request query parameters.

        Parameters::

        encoded_data
            Base64-encoded request data that gets sent to your server from EBS
            after a transaction is complete.

        encryption_key
            The secret key that EBS assigned to you when you
            registered as a merchant with them.

        flatten_values
            See description for `flatten_values' for the urldecode function.

        typed_values
            See description for `typed_values' for the urldecode function.

        How it works::

    1.  A replace-spaces-with-plus-characters transformation is applied to
        received base64-encoded data.

    2.  The base64 decoder then decodes the data to reveal the cipher text.
        Cipher text is encrypted using a secret key which EBS will have
        provided to you at the time of your registration with them.

    3.  An ARC4 decryptor then uses your secret key to decrypt the cipher-
        text into the plain-text query string.

    4.  The query string is then decoded into a key-value dictionary containing
        query parameters, which is then returned as the result of the function.
    """
    transformed_data = transformation(encoded_data)
    cipher_text = decoder(transformed_data)
    query_string = arc4_decrypt(encryption_key, cipher_text)
    query_params = urldecode(query_string, flatten_values, typed_values)
    return query_params

