#!/usr/bin/env python
"""

Copyright (c) 2007  Dustin Sallings <dustin@spy.net>
"""

import unittest

import github

class GitHubTest(unittest.TestCase):

    def __gh(self, expUrl, filename):
        def opener(url):
            self.assertEquals(expUrl, url)
            return open(filename)
        return github.GitHub(opener)

    def __loadUser(self):
        return self.__gh('http://github.com/api/v1/xml/dustin',
            'data/user.xml').user('dustin')

    def __loadCommits(self):
        return self.__gh(
            'http://github.com/api/v1/xml/caged/gitnub/commits/master',
            'data/commits.xml').commits('caged', 'gitnub', 'master')

    def testUserBase(self):
        """Test the base properties of the user object."""
        u=self.__loadUser()
        self.assertEquals("Dustin Sallings", u.name)
        self.assertEquals("dustin", u.login)
        self.assertEquals("dustin@spy.net", u.email)
        self.assertEquals("Santa Clara, CA", u.location)
        self.assertEquals("<<User dustin with 19 repos>>", repr(u))

    def testUserRepos(self):
        """Test the repositories within the user object."""
        u=self.__loadUser()
        self.assertEquals(19, len(u.repos))
        self.assertEquals('buildwatch', u.repos['buildwatch'].name)
        self.assertEquals('http://github.com/dustin/buildwatch',
            u.repos['buildwatch'].url)
        self.assertEquals('A buildbot GUI for OS X',
            u.repos['buildwatch'].description)
        self.assertEquals('http://code.google.com/p/buildwatch/',
            u.repos['buildwatch'].homepage)
        self.assertEquals("<<Repository buildwatch>>",
            repr(u.repos['buildwatch']))

    def testCommitsBase(self):
        commits=self.__loadCommits()
        self.assertEquals(30, len(commits))
        c=commits[0]
        self.assertEquals('da603ec86b62418e2ad433bb848ae6073cef7137', c.id)
        self.assertEquals("Consider .xib files binary.", c.message)
        self.assertEquals(
            "http://github.com/dustin/buildwatch/commit/%s" % c.id, c.url)
        self.assertEquals("2008-03-12T15:44:56-07:00", c.committedDate)
        self.assertEquals("2008-03-12T15:44:56-07:00", c.authoredDate)
        self.assertEquals("3c40e4178cedbc98214eb9a2b987b2d26a60d09c", c.tree)
        self.assertEquals(['c80c0d9557bc88ec236e7de9854f738c1d6c03b9'],
            c.parents)
        self.assertEquals('Dustin Sallings', c.author.name)
        self.assertEquals('Dustin Sallings', c.committer.name)
        self.assertEquals('dustin@spy.net', c.author.email)
        self.assertEquals('dustin@spy.net', c.committer.email)

if __name__ == '__main__':
    unittest.main()
    # gh=github.GitHub(hack)
