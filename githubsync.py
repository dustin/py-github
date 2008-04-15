#!/usr/bin/env python
"""
Grab all of a user's projects from github.

Copyright (c) 2008  Dustin Sallings <dustin@spy.net>
"""

import os
import sys
import subprocess

import github

def sync(path, user, repo):
    p=os.path.join(path, repo.name) + ".git"
    print "Syncing %s -> %s" % (repo, p)
    if os.path.exists(p):
        subprocess.call(['git', '--git-dir=' + p, 'fetch', '-f'])
    else:
        url = "git://github.com/%s/%s" % (user.login, repo.name)
        subprocess.call(['git', 'clone', '--bare', url, p])
        subprocess.call(['git', '--git-dir=' + p, 'remote', 'add', 'origin',
            url])

def usage():
    sys.stderr.write("Usage:  %s username destination_url\n" % sys.argv[0])
    sys.stderr.write(
        "  Ensures you've got the latest stuff for the given user.\n")

if __name__ == '__main__':
    try:
        user, path = sys.argv[1:]
    except ValueError:
        usage()
        exit(1)

    gh=github.GitHub()
    u = gh.user(user)

    for repo in u.repos.values():
        sync(path, u, repo)
