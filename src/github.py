#!/usr/bin/env python
#
# Copyright (c) 2005-2008  Dustin Sallings <dustin@spy.net>
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# <http://www.opensource.org/licenses/mit-license.php>
"""
Interface to github's API (v2).

Basic usage:

g = GitHub()

for r in g.user.search('dustin'):
    print r.name

See the GitHub docs or README.markdown for more usage.

Copyright (c) 2007  Dustin Sallings <dustin@spy.net>
"""

# GAE friendly URL detection (theoretically)
try:
    import urllib2
    default_fetcher = urllib2.urlopen
except LoadError:
    pass

import xml
import xml.dom.minidom

_types = {
    'string': lambda x: x.firstChild.data,
    'integer': lambda x: int(x.firstChild.data),
    'float': lambda x: float(x.firstChild.data)
}

def _parse(el):
    """Generic response parser."""

    type = 'string'
    if 'type' in el.attributes.keys():
        type = el.attributes['type'].value

    return _types[type](el)

class BaseResponse(object):
    """Base class for XML Response Handling."""

    def __init__(self, el):
        ch = el.firstChild
        while ch:
            if ch.nodeType != xml.dom.Node.TEXT_NODE and ch.firstChild:
                self.__dict__[ch.localName] = _parse(ch)
            ch=ch.nextSibling

    def __repr__(self):
        return "<<%s>>" % str(self.__class__)

class User(BaseResponse):
    """A github user."""

    parses = 'user'

    def __repr__(self):
        return "<<User %s>>" % self.name

# Load the known types.
for __t in (t for t in globals().values() if isinstance(type, type(t))):
    if hasattr(__t, 'parses'):
        _types[__t.parses] = __t

class BaseEndpoint(object):

    def __init__(self, fetcher):
        self.fetcher = fetcher

    def _fetch(self, path):
        p = "http://github.com/api/v2/xml/" + path
        return xml.dom.minidom.parseString(self.fetcher(p).read())

class UserEndpoint(BaseEndpoint):

    def search(self, query):
        print "Searching for", query
        doc = self._fetch('user/search/' + query)
        users = doc.getElementsByTagName('user')
        return [User(u) for u in users]

class GitHub(object):
    """Interface to github."""

    def __init__(self, fetcher=default_fetcher):
        self.fetcher = fetcher

    @property
    def users(self):
        """Get access to the user API."""
        return UserEndpoint(self.fetcher)

