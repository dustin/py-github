# What's on Github?

This is the beginning of a tool I'm writing so I can figure out and keep track
of what I've got at github (and hopefully other places as well).

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

