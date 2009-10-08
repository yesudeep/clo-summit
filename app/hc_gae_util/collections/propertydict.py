#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PropertyDict(object):
    """
    WARNING:
        Do not do this:
            p = PropertyDict(a='what', b='where', c='why', d='how')
            del p.a

        This does not delete p['a']. Use del ['a'] instead to delete the
        property.
    """

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        self.__properties__.add(key)
        setattr(self, key, value)

    def __delitem__(self, key):
        self.__properties__.remove(key)
        delattr(self, key)

    def __init__(self, *args, **kwargs):
        self.__properties__ = set([])
        for prop in args:
            self.__properties__.add(prop)
            setattr(self, prop, None)
        for k, v in kwargs.iteritems():
            self.__properties__.add(k)
            setattr(self, k, v)

    def __repr__(self):
        return repr(self.fields())

    def properties(self):
        return list(self.__properties__)[:]

    def has_property(self, key):
        return key in self.__properties__

    def fields(self, *names, **kwargs):
        prefix = kwargs.get('prefix', '')
        suffix = kwargs.get('suffix', '')
        props = self.__properties__
        result = {}
        if names:
            for prop in props:
                if prop in names:
                    result[prefix + prop + suffix] = getattr(self, prop)
        else:
            for prop in props:
                result[prefix + prop + suffix] = self[prop]
        return result

if __name__ == '__main__':
    p1 = PropertyDict(A='what', B='hmm')
    p2 = PropertyDict(a='what', b='whoo')

    print p1.fields()
    print p1.A, p1['A'], p1.B, p1['B']

    print p2.fields()
    print p2.a, p2['a'], p2.b, p2['b']

