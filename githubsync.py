#!/usr/bin/env python
"""
Grab all of a user's projects from github.

Copyright (c) 2008  Dustin Sallings <dustin@spy.net>
"""

import os
import sys
import subprocess

import github

def sync(path, url, repo_name):
    p=os.path.join(path, repo_name) + ".git"
    print "Syncing %s -> %s" % (repo_name, p)
    if not os.path.exists(p):
        subprocess.call(['git', 'clone', '--bare', url, p])
        subprocess.call(['git', '--git-dir=' + p, 'remote', 'add', '--mirror',
            'origin', url])
    subprocess.call(['git', '--git-dir=' + p, 'fetch', '-f'])

def sync_user_repo(path, user, repo):
    sync(path, "git://github.com/%s/%s" % (user.login, repo.name), repo.name)

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

    privfile = os.path.join(os.getenv("HOME"), ".github-private")
    if os.path.exists(privfile):
        f=open(privfile)
        for line in f:
            name, url = line.strip().split("\t")
            sync(path, url, name)

    gh=github.GitHub()
    u = gh.user(user)

    for repo in u.repos.values():
        sync_user_repo(path, u, repo)
