# What's on Github?

This is a library that implements
[github's API](http://github.com/guides/the-github-api) in python.

Part of the reason I wrote this was to have a simple way to keep local clones
of my projects.  Included is githubsync.py which does that for any given user
(within the limitations of the github API, which currently limits you to public
projects).

## Example

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

