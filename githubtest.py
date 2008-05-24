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

    def __loadCommit(self, which):
        id='00000010000101'
        return self.__gh(
            'http://github.com/api/v1/xml/dustin/py-github/commit/%s' % id,
            'data/' + which).commit('dustin', 'py-github', id)

    def testUserBase(self):
        """Test the base properties of the user object."""
        u=self.__loadUser()
        self.assertEquals("Dustin Sallings", u.name)
        self.assertEquals("dustin", u.login)
        self.assertEquals("dustin@spy.net", u.email)
        self.assertEquals("Santa Clara, CA", u.location)
        self.assertEquals("<<User dustin with 34 repos>>", repr(u))

    def testUserRepos(self):
        """Test the repositories within the user object."""
        u=self.__loadUser()
        self.assertEquals(34, len(u.repos))
        self.assertEquals('buildwatch', u.repos['buildwatch'].name)
        self.assertEquals('http://github.com/dustin/buildwatch',
            u.repos['buildwatch'].url)
        self.assertEquals('A buildbot GUI for OS X',
            u.repos['buildwatch'].description)
        self.assertEquals('http://code.google.com/p/buildwatch/',
            u.repos['buildwatch'].homepage)
        self.assertEquals("<<Repository buildwatch>>",
            repr(u.repos['buildwatch']))

    def testUserWatchers(self):
        """Test the watchers element in the user response."""
        u=self.__loadUser()
        self.assertEquals(10, u.repos['java-memcached-client'].watchers)

    def testUserForks(self):
        """Test the forks element in the user response."""
        u=self.__loadUser()
        self.assertEquals(3, u.repos['java-memcached-client'].forks)

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

    def testCommitWithAdd(self):
        c= self.__loadCommit('commit-with-add.xml')
        self.assertEquals('33464f2c56ed5fd64319d8dcc52fdfdb5db9d8ae', c.id)
        self.assertEquals('b73e9af69c043f68b19aa000980e56377fddb600', c.tree)
        self.assertEquals('2008-04-11T21:43:32-07:00', c.committedDate)
        self.assertEquals('2008-04-11T21:43:32-07:00', c.authoredDate)
        self.assertEquals('Added support for listing recent commits.',
            c.message)
        self.assertEquals(['f54d6071a0dafadd3ce50dd0b01b3ca3b69818c7'],
            c.parents)
        self.assertEquals('http://github.com/dustin/py-github/commit/%s' % c.id,
            c.url)
        self.assertEquals('dustin@spy.net', c.author.email)
        self.assertEquals('dustin@spy.net', c.committer.email)
        self.assertEquals('Dustin Sallings', c.author.name)
        self.assertEquals('Dustin Sallings', c.committer.name)
        self.assertEquals(0, len(c.removed))
        self.assertEquals(['data/commits.xml'], c.added)
        self.assertEquals(['github.py', 'githubtest.py'],
            [m.filename for m in c.modified])

        self.assertTrue('Repository' in c.modified[0].diff)
        self.assertTrue('GitHubTest' in c.modified[1].diff)

    def testCommitWithMerge(self):
        c= self.__loadCommit('commit-merge.xml')
        self.assertEquals('c80c0d9557bc88ec236e7de9854f738c1d6c03b9', c.id)
        self.assertEquals('27d3edfc5f719e1f59871b420a5a4af6616ddca0', c.tree)
        self.assertEquals('2008-03-12T00:05:00-07:00', c.committedDate)
        self.assertEquals('2008-03-12T00:05:00-07:00', c.authoredDate)
        self.assertEquals("Merge branch 'torelease'", c.message)
        self.assertEquals(['c47c0aaa9579fd27d185366ac189cacaa0d9f066',
            '40133467bedae260f9322325ee93ca27fd4fac6c'], c.parents)
        self.assertEquals('http://github.com/dustin/buildwatch/commit/%s'
            % c.id, c.url)
        self.assertEquals('dustin@spy.net', c.author.email)
        self.assertEquals('dustin@spy.net', c.committer.email)
        self.assertEquals('Dustin Sallings', c.author.name)
        self.assertEquals('Dustin Sallings', c.committer.name)
        self.assertEquals(0, len(c.removed))
        self.assertEquals(0, len(c.added))
        self.assertEquals(['ApplicationDelegate.m',
            'English.lproj/MainMenu.xib', 'Info.plist', 'buildwatch.xml'],
            [m.filename for m in c.modified])

if __name__ == '__main__':
    unittest.main()
    # gh=github.GitHub(hack)
