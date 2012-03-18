#!/usr/bin/env python

import sys
import getpass
import itertools
import github

def printHeader(users):
    print """<html>
<head>
  <style type="text/css">
    tr.odd * {
      background: #bbf
    }
  </style>
</head>
<body>
<table>"""
    print "<thead><tr>"
    print "<th>Repo</th>"
    for u in users:
        print "  <th>%s</th>" % u
    print "<th>Repo</th>"
    print "</tr></thead>"

def printRepo(repo, allusers, repo_users, rowstylegen):

    print '<tr class="%s">' % rowstylegen.next()
    print "  <td><b>%s</b></td>" % repo

    for u in allusers:
        style = {True: 'user', False: 'notuser'}[u in repo_users]
        state = {True: u, False: '-'}[u in repo_users]
        print '  <td class="%s">%s</td>' % (style, state)

    print "  <td><b>%s</b></td>" % repo
    print "</th>"

def printFooter():
    print """
</table>
</body>
</html>"""

def usage():
    sys.stderr.write("Usage:  %s githubuser githubtoken > map.html\n"
                     % sys.argv[0])
    sys.exit(64)

if __name__ == '__main__':

    try:
        gh = github.GitHub(sys.argv[1], sys.argv[2])
    except IndexError:
        usage()

    rh = gh.repos.collaborators_all()

    allusers = set()
    for v in rh.itervalues():
        allusers.update(set(v))

    au = sorted(list(allusers))

    printHeader(au)

    rowstylegen = itertools.cycle(['odd', 'even'])

    print "<tbody>"
    for r in sorted(rh.keys()):
        printRepo(r, au, rh[r], rowstylegen)
    print "</tbody>"

    printFooter()
