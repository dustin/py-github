# What's on Github?

This is a library that implements
[github's API](http://github.com/guides/the-github-api) in python.

Part of the reason I wrote this was to have a simple way to keep local clones
of my projects.  Included is githubsync.py which does that for any given user
(within the limitations of the github API, which currently limits you to public
projects).

# Supported APIs

## User

This code (which happens to be main in git.py)

    import sys
    u = GitHub().user(sys.argv[1])
    print "User:  %s (%s)" % (u.login, u.name)
    for repo in [u.repos[k] for k in sorted(u.repos.keys())]:
        print "- %s" % repo.name
        print "  %s" % repo.url
        print "  %s" % "git://github.com/%s/%s.git" % (u.login, repo.name)

Yields this result:

    User:  dustin (Dustin Sallings)
    - app-hider
      http://github.com/dustin/app-hider
      git://github.com/dustin/app-hider.git
    - buildwatch
      http://github.com/dustin/buildwatch
      git://github.com/dustin/buildwatch.git
    - cache_fu
      http://github.com/dustin/cache_fu
      git://github.com/dustin/cache_fu.git
    - diggwatch
      http://github.com/dustin/diggwatch
      git://github.com/dustin/diggwatch.git
    - environ
      http://github.com/dustin/environ
      git://github.com/dustin/environ.git

## Search

Search for repos or descriptions matching the given search terms.

    repos = GitHub().search('memcache')
    for r in repos:
        print "%s has %d forks and %d watchers" % (
            r.name, r.forks, r.watchers)

## Commits

Get the recent commits for a given repo.

    commits = GitHub().commits('dustin', 'py-github')
    for c in commits:
        print "%s: %s" % (c.id[:7], c.message.split('\n')[0])

Also, you may specify a particular branch:

    commits = GitHub().commits('dustin', 'memcached', 'binary')
    for c in commits:
        print "%s: %s" % (c.id[:7], c.message.split('\n')[0])

## Commit

Fetch a specific commit and lots of details about it.

Note there is a *lot* of structured data in here this example doesn't show.
For example, modified files contain a full diff of each file, and every commit
has a list of parent IDs (in the case of an octopus merge, there can be many).
If you want more information, it's quite likely there.

    commit = GitHub().commit('gitmirror', 'git', 'c998ae9b')
    print "%s made the change\n%s\nAffecting the following files:" % (
        commit.author.name, commit.message)
    for c in commit.added: print "A", c.filename
    for c in commit.removed: print "R", c.filename
    for c in commit.modified: print "M", c.filename
