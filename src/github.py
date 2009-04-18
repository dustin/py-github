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

import urllib
import xml
import xml.dom.minidom

_types = {
    'string': lambda x: x.firstChild.data,
    'integer': lambda x: int(x.firstChild.data),
    'float': lambda x: float(x.firstChild.data),
    'datetime': lambda x: x.firstChild.data,
    'boolean': lambda x: x.firstChild.data == 'true'
}

def _parse(el):
    """Generic response parser."""

    type = 'string'
    if el.attributes and 'type' in el.attributes.keys():
        type = el.attributes['type'].value
    elif el.localName in _types:
        type = el.localName
    elif len(el.childNodes) > 1:
        # This is a container, find the child type
        type = None
        ch = el.firstChild
        while ch and not type:
            if ch.localName == 'type':
                type = ch.firstChild.data
            ch = ch.nextSibling

    if not type:
        raise Exception("Can't parse %s, known: %s"
                        % (el.toxml(), repr(_types.keys())))

    return _types[type](el)

def parses(t):
    """Parser for a specific type in the github response."""
    def f(orig):
        orig.parses = t
        return orig
    return f

@parses('array')
def _parseArray(el):
    rv = []
    ch = el.firstChild
    while ch:
        if ch.nodeType != xml.dom.Node.TEXT_NODE and ch.firstChild:
            rv.append(_parse(ch))
        ch=ch.nextSibling
    return rv

class BaseResponse(object):
    """Base class for XML Response Handling."""

    def __init__(self, el):
        ch = el.firstChild
        while ch:
            if ch.nodeType != xml.dom.Node.TEXT_NODE and ch.firstChild:
                ln = ch.localName.replace('-', '_')
                self.__dict__[ln] = _parse(ch)
            ch=ch.nextSibling

    def __repr__(self):
        return "<<%s>>" % str(self.__class__)

class User(BaseResponse):
    """A github user."""

    parses = 'user'

    def __repr__(self):
        return "<<User %s>>" % self.name

class Plan(BaseResponse):
    """A github plan."""

    parses = 'plan'

    def __repr__(self):
        return "<<Plan %s>>" % self.name

class Repository(BaseResponse):
    """A repository."""

    parses = 'repository'

    def __repr__(self):
        return "<<Repository %s/%s>>" % (self.owner, self.name)

# Load the known types.
for __t in (t for t in globals().values() if hasattr(t, 'parses')):
    _types[__t.parses] = __t

class BaseEndpoint(object):

    def __init__(self, user, token, fetcher):
        self.user = user
        self.token = token
        self.fetcher = fetcher

    def _fetch(self, path):
        p = "http://github.com/api/v2/xml/" + path
        args = ''
        if self.user and self.token:
            params = '&'.join(['login=' + urllib.quote(self.user),
                               'token=' + urllib.quote(self.token)])
            if '?' in path:
                p += params
            else:
                p += '?' + params
        return xml.dom.minidom.parseString(self.fetcher(p).read())

    def _parsed(self, path):
        doc = self._fetch(path)
        return _parse(doc.documentElement)

class UserEndpoint(BaseEndpoint):

    def search(self, query):
        return self._parsed('user/search/' + query)

    def show(self, username):
        return self._parsed('user/show/' + username)

class RepositoryEndpoint(BaseEndpoint):

    def forUser(self, username):
        """Get the repositories for the given user."""
        return self._parsed('repos/show/' + username)

class GitHub(object):
    """Interface to github."""

    def __init__(self, user=None, token=None, fetcher=default_fetcher):
        self.user = user
        self.token = token
        self.fetcher = fetcher

    @property
    def users(self):
        """Get access to the user API."""
        return UserEndpoint(self.user, self.token, self.fetcher)

    @property
    def repos(self):
        """Get access to the user API."""
        return RepositoryEndpoint(self.user, self.token, self.fetcher)

