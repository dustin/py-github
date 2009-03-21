# What's on Github?

This is a library that implements
[github's API](http://develop.github.com/) in python.

v2 is still in early development, so don't expect it to be terribly
uesful for a bit.

# Supported APIs

## User

### Search

This is a simple search call.  All properties returned by the API will
be available as properties (just using the `name` and `fullname`
properties here).

    import sys
    for u in github.GitHub().users.search(username):
        print "User:  %s (%s)" % (u.name, u.fullname)

