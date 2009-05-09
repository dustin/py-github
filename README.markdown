# What's on Github?

This is a library that implements
[github's API](http://develop.github.com/) in python.

# Supported APIs

All API access begins with the creation of a `GitHub` object.  For the
sake of brevity, this document assumes you've created an object called
`gh` as a github endpoint:

    gh = github.GitHub()

Some operations require (or are enhanced by) authentication.  These
are noted within the documentation and will use an object called `agh`
created the following way:

    agh = github.GitHub('myusername', 'mytoken')

You can find your token from your [account page][accountpage].

## User

The [user API][userapi] is available via `gh.users`.

### Search

This is a simple user search call.  All properties returned by the API
will be available as properties.

Example displaying search results using the `name` and `fullname`
properties:

    for u in gh.users.search(myquery):
        print "User:  %s (%s)" % (u.name, u.fullname)

### Show

Get details about an individual user.

    username = 'dustin'
    print "%s's web site:  %s" % (username, gh.users.show(%s).blog)

Note that this API returns more information if you're authenticated
and ask for yourself:

    print "My disk usage: %d" % agh.users.show(me).disk_usage

### Keys

List your ssh keys:

    print "Names of my keys:"
    for k in agh.users.keys():
        print k.title

## Repositories

The [repository API][repoapi] is available via `gh.repos`.

### Repository List for a User

List the repositories owned by a user.  If you are authenticated this
user, private repositories will also be returned.

    print "My repo names:"
    for r in gh.repos.forUser(me):
        print r.name

### Branches Within a Repo

List the branches within a repo:

    print "memcached branches:"
    for branchname, branchhash in gh.repos.branches('dustin', 'memcached'):
        print branchname

### Search for a Repository

    for r in gh.repos.search('memcached'):
        print "%s's %s" % (r.username, r.name)

### Show a Repository

Retrieve an individual repository.

    print gh.repos.show('dustin', 'py-github').homepage

### Watch a Repository

Begin watching a repository.

    gh.repos.watch('dustin', 'memcached')

### Unwatch a Repository

Stop watching a repository.

    gh.repos.unwatch('dustin', 'memcached')

### Get a Repository's Network

Retrieve the network for a repository.

    for r in gh.repos.network('dustin', 'memcached'):
        print "%'s %s" % (r.owner_name, r.name)

### Adjust a Repository's Visibility

You can adjust repository visibility for your own repositories only
(therefore the username is omitted).

To set a repository public:

    agh.repos.setVisible('repo-name')

To set a repository private:

    agh.repos.setVisible('repo-name', False)

### Create a New Repository

The most simple invocation (create a public repository with no
description or URL) would look like this:

    agh.repos.create('testrepository')

You can pass many flags in to set up the repository, however.
Consider this case where a private repository is created.

    agh.repos.create('testrepo', description='My test repo',
                     homepage='http://www.spy.net/', public=0)

### Deleting a Repository

You may delete repositories attached to your account only.

    agh.repos.delete('testrepo')

### Forking a Repository

    agh.repos.fork('dustin', 'memcached')

### Adding a Collaborator

    agh.repos.addCollaborator('memcached', 'trondn')

### Removing a Collaborator

    agh.repos.removeCollaborator('memcached', 'trondn')

### Listing Deploy Keys

    agh.repos.deployKeys('myrepo')

## Commits

The [commit API][commitapi] is available via `gh.commits`.

### Get the Commits from a Branch

Master is assumed:

    for c in gh.commits.forBranch('dustin', 'py-github'):
        print "%s %s" % (c.id[:7], c.message[:60].split("\n")[0])

Otherwise, you can specify a branch name:

    for c in gh.commits.forBranch('dustin', 'py-github', 'v2'):
        print "%s %s" % (c.id[:7], c.message[:60].split("\n")[0])

### Get the Commits Affecting a File

Retrieve all of the commits for the specified file.  Again, master is
assumed):

    for c in gh.commits.forFile('dustin', 'py-github', 'README.markdown'):
        print "%s %s" % (c.id[:7], c.message[:60].split("\n")[0])

...but you can also specify a branch name:

    for c in gh.commits.forFile('dustin', 'py-github', 'README.markdown', 'v2'):
        print "%s %s" % (c.id[:7], c.message[:60].split("\n")[0])

### Show a Specific Commit

    print gh.commits.show('dustin', 'memcached',
        '923a335bf8613696d658448cd9c48a963924d436').message

## Issues

The [issues api][issueapi] is available via `gh.issues`.

### List Repository Issues

    for i in gh.issues.list('dustin', 'py-github'):
        print "issue #%s:  %s" % (i.number, i.title)

### Show a Particular Issue

    i = gh.issues.show('dustin', 'py-github', 1)
    print "%s:  %s" % (i.state, i.title)

### Add a Label to an Issue

    agh.issues.add_label('dustin', 'py-github', 38, 'awesome')

### Remove a Label from an Issue

    agh.issues.remove_label('dustin', 'py-github', 38, 'fun')

### Close an Issue

    agh.issues.close('dustin', 'py-github', 38)

### Reopen a Closed Issue

    agh.issues.reopen('dustin', 'py-github', 38)

### Create a New Issue

    agh.issues.new('dustin', 'py-github', 'more code', 'Write more code.')

The body parameter (last) is optional.

### Edit an Existing Issue

    agh.issues.edit('dustin', 'py-github', 8284, 'New Title', 'New Body')

## Objects

The [objects API][objectapi] is available via `gh.objects`.

### Get a Tree

Retreive the tree object with the given hash:

    t = gh.objects.tree('dustin', 'py-github',
        'b34f658fd7be0d3e00cc961b75da10ca0d44d050')
    for k,v in t.items():
        print "%s\t%s\t%s" % (v.sha, v.type, k)

### Retrieve a Blob (with info)

    b = gh.objects.blob('dustin', 'py-github',
        'b34f658fd7be0d3e00cc961b75da10ca0d44d050', 'README.markdown')
    print b.data

### Retrieve a Raw Blob

    print b.raw_blob('dustin', 'py-github',
        'a1ae3723758a0dc1ea857e9efe6640f18a6b3865')

[accountpage]: https://github.com/account
[userapi]: http://develop.github.com/p/users.html
[repoapi]: http://develop.github.com/p/repo.html
[issueapi]: http://develop.github.com/p/issues.html
[commitapi]: http://develop.github.com/p/commits.html
[objectapi]: http://develop.github.com/p/object.html
