#!/usr/bin/env python
"""
Interface to github's API.

Copyright (c) 2007  Dustin Sallings <dustin@spy.net>
"""

# Copyright (c) 2005  Dustin Sallings <dustin@spy.net>
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

# GAE friendly URL detection (theoretically)
try:
    import urllib2
    default_fetcher=urllib2.urlopen
except LoadError:
    pass

import xml
import xml.dom.minidom

class Repository(object):
    """A github repository."""

    def __init__(self, el):
        ch=el.firstChild
        while ch:
            if ch.nodeType != xml.dom.Node.TEXT_NODE and ch.firstChild:
                self.__dict__[ch.localName] = ch.firstChild.data
            ch=ch.nextSibling

    def __repr__(self):
        return "<<Repository %s>>" % self.name

class Person(object):
    """A person."""

    def __init__(self, el):
        ch=el.firstChild
        while ch:
            if ch.nodeType != xml.dom.Node.TEXT_NODE:
                if ch.localName != 'repositories':
                    self.__dict__[ch.localName] = ch.firstChild.data
            ch=ch.nextSibling
        repos=[Repository(el) for el in el.getElementsByTagName('repository')]
        self.repos=dict([(r.name, r) for r in repos])

    def __repr__(self):
        return "<<Person %s <%s>>>" % (self.name, self.email)

class User(Person):
    """A github user."""

    def __init__(self, doc):
        Person.__init__(self, doc.firstChild)

    def __repr__(self):
        return "<<User %s with %d repos>>" % (self.login, len(self.repos))

class Commit(object):
    """A single commit."""

    def __init__(self, el):
        ch=el.firstChild
        while ch:
            if ch.nodeType != xml.dom.Node.TEXT_NODE:
                if ch.localName == 'parents':
                    self.parents = [str(s.firstChild.data)
                        for s in ch.getElementsByTagName('id')]
                elif ch.localName == 'author':
                    self.author = Person(ch)
                elif ch.localName == 'committer':
                    self.committer = Person(ch)
                elif ch.localName == 'committed-date':
                    self.committedDate = self.__parseDate(ch)
                elif ch.localName == 'authored-date':
                    self.authoredDate = self.__parseDate(ch)
                else:
                    self.__dict__[ch.localName] = ch.firstChild.data
            ch=ch.nextSibling

    def __parseDate(self, el):
        dateStr=el.firstChild.data
        # XXX:  Parse here.
        return dateStr

    def __repr__(self):
        return "<<Commit %s>>" % self.id

class GitHub(object):
    """Interface to github."""

    def __init__(self, fetcher=default_fetcher):
        self.fetcher=fetcher

    def user(self, username):
        """Get the info for a user."""
        x=self.fetcher("http://github.com/api/v1/xml/%s" % username).read()
        doc=xml.dom.minidom.parseString(x)
        return User(doc)

    def commits(self, username, repo, branch):
        """Get the recent commits for the given repo."""
        x=self.fetcher("http://github.com/api/v1/xml/%s/%s/commits/%s"
            % (username, repo, branch)).read()
        doc=xml.dom.minidom.parseString(x)
        return [Commit(el) for el in doc.getElementsByTagName('commit')]

if __name__ == '__main__':
    import sys
    gh=GitHub()
    if len(sys.argv) == 2:
        u = gh.user(sys.argv[1])
        print "User:  %s (%s)" % (u.login, u.name)
        for repo in [u.repos[k] for k in sorted(u.repos.keys())]:
            print "- %s" % repo.name
            print "  %s" % repo.url
            print "  %s" % "git://github.com/%s/%s.git" % (u.login, repo.name)
    elif len(sys.argv) == 4:
        for commit in gh.commits(*sys.argv[1:]):
            print "%s %s - %s" % (commit.id[0:7],
                commit.author.email, commit.message)
    else:
        print "Usages:"
        print " %s user" % sys.argv[0]
        print "    -- show info about a given user"
        print " %s user repo branch" % sys.argv[0]
        print "    -- show recent commits on a specific branch"
