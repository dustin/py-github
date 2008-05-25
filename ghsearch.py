#!/usr/bin/env python

import sys

import github

def usage():
    """display the usage and exit"""
    print "Usage:  %s keyword [keyword...]" % (sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':
    g = github.GitHub()
    if len(sys.argv) < 2:
        usage()
    res = g.search(' '.join(sys.argv[1:]))

    for repo in res:
        print "Found %s at %s" % (repo.name, repo.url)