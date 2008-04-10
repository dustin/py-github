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

if __name__ == '__main__':
    unittest.main()
    # gh=github.GitHub(hack)
