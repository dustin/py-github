#!/usr/bin/env python
#
# Copyright (c) 2005-2008  Dustin Sallings <dustin@spy.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# <http://www.opensource.org/licenses/mit-license.php>
"""
Interface to github's API (v2).

Basic usage:

g = GitHub()

for r in g.user.search('dustin'):
    print r.name

See the GitHub docs or README.markdown for more usage.

Copyright (c) 2007  Dustin Sallings <dustin@spy.net>
"""

import sys
import xml
import xml.dom.minidom

try: import simplejson as json
except ImportError: import json

from urllib import urlencode

import hclient

def _string_parser(x):
    """Extract the data from the first child of the input."""
    return x.firstChild.data

_types = {
    'string': _string_parser,
    'integer': lambda x: int(_string_parser(x)),
    'float': lambda x: float(_string_parser(x)),
    'datetime': _string_parser,
    'boolean': lambda x: _string_parser(x) == 'true'
}

def _parse(el):
    """Generic response parser."""

    type = 'string'
    if el.attributes and 'type' in list(el.attributes.keys()):
        type = el.attributes['type'].value
    elif el.localName in _types:
        type = el.localName
    elif len(el.childNodes) > 1:
        # This is a container, find the child type
        type = None
        ch = el.firstChild
        while ch and not type:
            if ch.localName == 'type':
                type = ch.firstChild.data
            ch = ch.nextSibling

    if not type:
        raise Exception("Can't parse %s, known: %s"
                        % (el.toxml(), repr(list(_types.keys()))))

    return _types[type](el)

def parses(t):
    """Parser for a specific type in the github response."""
    def f(orig):
        orig.parses = t
        return orig
    return f

def with_temporary_mappings(m):
    """Allow temporary localized altering of type mappings."""
    def f(orig):
        def every(self, *args):
            global _types
            o = _types.copy()
            for k,v in list(m.items()):
                if v:
                    _types[k] = v
                else:
                    del _types[k]
            try:
                return orig(self, *args)
            finally:
                _types = o
        return every
    return f

@parses('array')
def _parseArray(el):
    rv = []
    ch = el.firstChild
    while ch:
        if ch.nodeType != xml.dom.Node.TEXT_NODE and ch.firstChild:
            rv.append(_parse(ch))
        ch=ch.nextSibling
    return rv

class BaseResponse(object):
    """Base class for XML Response Handling."""

    def __init__(self, el):
        ch = el.firstChild
        while ch:
            if ch.nodeType != xml.dom.Node.TEXT_NODE and ch.firstChild:
                ln = ch.localName.replace('-', '_')
                self.__dict__[ln] = _parse(ch)
            ch=ch.nextSibling

    def __repr__(self):
        return "<<%s>>" % str(self.__class__)

class User(BaseResponse):
    """A github user."""

    parses = 'user'

    def __repr__(self):
        return "<<User %s>>" % self.name

class Plan(BaseResponse):
    """A github plan."""

    parses = 'plan'

    def __repr__(self):
        return "<<Plan %s>>" % self.name

class Repository(BaseResponse):
    """A repository."""

    parses = 'repository'

    @property
    def owner_name(self):
        if hasattr(self, 'owner'):
            return self.owner
        else:
            return self.username

    def __repr__(self):
        return "<<Repository %s/%s>>" % (self.owner_name, self.name)

class PublicKey(BaseResponse):
    """A public key."""

    parses = 'public-key'
    title = 'untitled'

    def __repr__(self):
        return "<<Public key %s>>" % self.title

class Commit(BaseResponse):
    """A commit."""

    parses = 'commit'

    def __repr__(self):
        return "<<Commit: %s>>" % self.id

class Parent(Commit):
    """A commit parent."""

    parses = 'parent'

class Author(User):
    """A commit author."""

    parses = 'author'

class Committer(User):
    """A commit committer."""

    parses = 'committer'

class Issue(BaseResponse):
    """An issue within the issue tracker."""

    parses = 'issue'

    def __repr__(self):
        return "<<Issue #%d>>" % self.number

class IssueComment(BaseResponse):
    """ An issue comment within the issue tracker."""

    parses = 'comment'

    def __repr__(self):
        return "<<Comment #%s>>" % self.body

class Label(BaseResponse):
    """A Label within the issue tracker."""
    parses = 'label'

    def __repr__(self):
        return "<<Label $%s>>" % self.name

class Tree(BaseResponse):
    """A Tree object."""

    # Parsing is scoped to objects...
    def __repr__(self):
        return "<<Tree: %s>>" % self.name

class Blob(BaseResponse):
    """A Blob object."""

    # Parsing is scoped to objects...
    def __repr__(self):
        return "<<Blob: %s>>" % self.name

class Modification(BaseResponse):
    """A modification object."""

    # Parsing is scoped to usage
    def __repr__(self):
        return "<<Modification of %s>>" % self.filename

class Network(BaseResponse):
    """A network entry."""

    parses = 'network'

    def __repr__(self):
        return "<<Network of %s/%s>>" % (self.owner, self.name)

class Organization(BaseResponse):
    """An organization."""

    parses = 'organization'

    def __repr__(self):
        return "<<Organization %s>>" % getattr(self, 'name', self.login)

# Load the known types.
for __t in (t for t in list(globals().values()) if hasattr(t, 'parses')):
    _types[__t.parses] = __t

class BaseEndpoint(object):

    BASE_URL = 'https://github.com/api/v2/xml/'

    def __init__(self, user, token, fetcher):
        self.user = user
        self.token = token
        self.fetcher = fetcher

    def _raw_fetch(self, path, base=None, data=None, httpAuth=False, method=None):
        if not base:
            base = self.BASE_URL
        p = base + path
        args = ''
        if self.user and self.token and not httpAuth:
            params = '&'.join(['login=' + hclient.quote(self.user),
                               'token=' + hclient.quote(self.token)])
            if '?' in path:
                p += '&' + params
            else:
                p += '?' + params

        if httpAuth:
            return self.fetcher(p, data,
                                username=self.user, password=self.token,
                                method=method)
        else:
            return self.fetcher(p, data)

    def _fetch(self, path, parselang = False):
        rawfetch = self._raw_fetch(path).read()
        # Hack since Github languages API gives malformed XML
        if parselang:
            rawfetch = rawfetch.replace('#', 'sharp')
            rawfetch = rawfetch.replace('-', '')
            rawfetch = rawfetch.replace('+', 'p')
            rawfetch = rawfetch.replace(' Lisp', 'Lisp')
            rawfetch = rawfetch.replace('Visual Basic', 'VisualBasic')
            rawfetch = rawfetch.replace('Pure Data', 'PureData')
            rawfetch = rawfetch.replace('Max/MSP', 'MaxMSP')
        return xml.dom.minidom.parseString(rawfetch)

    def _jfetch(self, path, httpAuth=True):
        return json.load(self._raw_fetch(path, 'https://api.github.com/',
                                         httpAuth=httpAuth))

    def _jpost(self, path, data, httpAuth=True):
        return json.load(self._raw_fetch(path, 'https://api.github.com/',
                                         data=data,
                                         httpAuth=httpAuth))

    def _post(self, path, **kwargs):
        p = {'login': self.user, 'token': self.token}
        p.update(kwargs)
        return self.fetcher(self.BASE_URL + path, urlencode(p)).read()

    def _put(self, path, **kwargs):
        p = {'login': self.user, 'token': self.token}
        p.update(kwargs)
        # Setting PUT with urllib2: http://stackoverflow.com/questions/111945
        import urllib2
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(self.BASE_URL + path, data=hclient.urlencode(p))
        request.get_method = lambda: 'PUT'
        return opener.open(request).read()

    def _parsed(self, path):
        doc = self._fetch(path)
        return _parse(doc.documentElement)

    def _posted(self,path,**kwargs):
        stuff = self._post(path,**kwargs)
        doc = xml.dom.minidom.parseString(stuff)
        return _parse(doc.documentElement)

class UserEndpoint(BaseEndpoint):

    def search(self, query):
        """Search for a user."""
        return self._parsed('user/search/' + query)

    def show(self, username):
        """Get the info for a user."""
        return self._parsed('user/show/' + username)

    def keys(self):
        """Get the public keys for a user."""
        return self._parsed('user/keys')

    def removeKey(self, keyId):
        """Remove the key with the given ID (as retrieved from keys)"""
        self._post('user/key/remove', id=keyId)

    def addKey(self, name, key):
        """Add an ssh key."""
        self._post('user/key/add', name=name, key=key)

class RepositoryEndpoint(BaseEndpoint):

    def forUser(self, username, page=1):
        """Get the repositories for the given user."""
        return self._parsed('repos/show/' + username + "/?page=" + str(page))

    def branches(self, user, repo):
        """List the branches for a repo."""
        doc = self._fetch("repos/show/" + user + "/" + repo + "/branches")
        rv = {}
        for c in doc.documentElement.childNodes:
            if c.nodeType != xml.dom.Node.TEXT_NODE:
                rv[c.localName] = str(c.firstChild.data)
        return rv

    def languages(self, user, repo):
        """List the languages for a repo."""
        doc = self._fetch("repos/show/" + user + "/" + repo + "/languages", True)
        rv = {}
        for c in doc.documentElement.childNodes:
            if c.nodeType != xml.dom.Node.TEXT_NODE:
                rv[c.localName] = str(c.firstChild.data)
        return rv

    def tags(self, user, repo):
        """List the tags for a repo."""
        doc = self._fetch("repos/show/" + user + "/" + repo + "/tags")
        rv = {}
        for c in doc.documentElement.childNodes:
            if c.nodeType != xml.dom.Node.TEXT_NODE:
                rv[c.localName] = str(c.firstChild.data)
        return rv

    def search(self, term, **args):
        """Search for repositories.

        Accept arguments to filter the search:
        - start_page => specifies the page of the results to show
        - language   => limits the search to a programming language """

        path = 'repos/search/' + hclient.quote_plus(term)
        params = "&".join(["%s=%s" % (k, v) for k,v in list(args.items())])
        if params:
            path += '?%s' % params
        return self._parsed(path)

    def show(self, user, repo):
        """Lookup an individual repository."""
        return self._parsed('/'.join(['repos', 'show', user, repo]))

    def set(self, user, repo, **args):
        """Set repository parameters.

        Repository parameters include the following:

         - description
         - homepage
         - has_wiki
         - has_issues
         - has_downloads"""

        prepared_args = {}
        for k,v in list(args.items()):
            prepared_args['values[' + k + ']'] = v
        return self._post('/'.join(['repos', 'show', user, repo]),
                          **prepared_args)

    def watch(self, user, repo):
        """Watch a repository."""
        self._post('repos/watch/' + user + '/' + repo)

    def unwatch(self, user, repo):
        """Stop watching a repository."""
        self._post('repos/unwatch/' + user + '/' + repo)

    def watched(self, user):
        """Get watched repositories of a user."""
        return self._parsed('repos/watched/' + user)

    def network(self, user, repo):
        """Get the network for a given repo."""
        return self._parsed('repos/show/' + user + '/' + repo + '/network')

    def setVisible(self, repo, public=True):
        """Set the visibility of the given repository (owned by the current user)."""
        if public:
            path = 'repos/set/public/' + repo
        else:
            path = 'repos/set/private/' + repo
        self._post(path)

    def create(self, name, description='', homepage='', public=1):
        """Create a new repository."""
        self._post('repos/create', name=name, description=description,
                   homepage=homepage, public=str(public))

    def delete(self, repo):
        """Delete a repository."""
        self._post('repos/delete/' + repo)

    def fork(self, user, repo):
        """Fork a user's repo."""
        self._post('repos/fork/' + user + '/' + repo)

    def watchers(self, user, repo):
        """Find all of the watchers of one of your repositories."""
        return self._parsed('repos/show/%s/%s/watchers' % (user, repo))

    def collaborators(self, user, repo):
        """Find all of the collaborators of one of your repositories."""
        return self._parsed('repos/show/%s/%s/collaborators' % (user, repo))

    def addCollaborator(self, repo, username):
        """Add a collaborator to one of your repositories."""
        self._post('repos/collaborators/' + repo + '/add/' + username)

    def removeCollaborator(self, repo, username):
        """Remove a collaborator from one of your repositories."""
        self._post('repos/collaborators/' + repo + '/remove/' + username)

    def collaborators_all(self):
        """Find all of the collaborators of every of your repositories.

        Returns a dictionary with reponame as key and a list of collaborators as value."""
        ret = {}
        for reponame in (rp.name for rp in self.forUser(self.user)):
            ret[reponame] = self.collaborators(self.user, reponame)
        return ret

    def addCollaborator_all(self, username):
        """Add a collaborator to all of your repositories."""
        for reponame in (rp.name for rp in self.forUser(self.user)):
            self.addCollaborator(reponame, username)

    def removeCollaborator_all(self, username):
        """Remove a collaborator from all of your repositories."""
        for reponame in (rp.name for rp in self.forUser(self.user)):
            self.removeCollaborator(reponame, username)

    def deployKeys(self, repo):
        """List the deploy keys for the given repository.

        The repository must be owned by the current user."""
        return self._parsed('repos/keys/' + repo)

    def addDeployKey(self, repo, title, key):
        """Add a deploy key to a repository."""
        self._post('repos/key/' + repo + '/add', title=title, key=key)

    def removeDeployKey(self, repo, keyId):
        """Remove a deploy key."""
        self._post('repos/key/' + repo + '/remove', id=keyId)

    def discoverHooks(self):
        """Get the known hook types supported by github.

        returns a dict of name -> info.  (see info['schema'] for config params)
        """
        hooks = self._jfetch('hooks', httpAuth=False)
        return dict((h['name'], h) for h in hooks)

    def listHooks(self, user, repo):
        """List hooks configured for a repo."""
        # /repos/:user/:repo/hooks
        return self._jfetch('/'.join(['repos', user, repo, 'hooks']))

    def getHook(self, user, repo, hookid):
        """Get a specific hook by ID."""
        return self._jfetch('/'.join(['repos', user, repo, 'hooks',
                                      str(hookid)]))

    def createHook(self, user, repo, name, config,
                   events=["push"], active=True):
        """Create a hook on the given repo.

        For more info, see the docs:
             http://developer.github.com/v3/repos/hooks/
        """

        doc = json.dumps({'name': name,
                          'active': active,
                          'config': config,
                          'events': events})

        return self._jpost('/'.join(['repos', user, repo, 'hooks']), doc)

    def testHook(self, user, repo, hookid):
        """Test a specific hook by ID."""
        return self._raw_fetch('/'.join(['repos', user, repo, 'hooks',
                                     str(hookid), 'test']),
                               base='https://api.github.com/',
                               data='', httpAuth=True).read()

    def deleteHook(self, user, repo, hookid):
        """Remove a specified hook."""
        return self._raw_fetch('/'.join(['repos', user, repo, 'hooks',
                                         str(hookid)]),
                               base='https://api.github.com/',
                               data='', httpAuth=True, method='DELETE').read()


class CommitEndpoint(BaseEndpoint):

    def forBranch(self, user, repo, branch='master', page=1):
        """Get the commits for the given branch."""
        return self._parsed('/'.join(['commits', 'list', user, repo, branch])+ "?page=" + str(page))

    def forFile(self, user, repo, path, branch='master'):
        """Get the commits for the given file within the given branch."""
        return self._parsed('/'.join(['commits', 'list', user, repo, branch, path]))

    @with_temporary_mappings({'removed': _parseArray,
                              'added': _parseArray,
                              'modified': Modification,
                              'diff': _string_parser,
                              'filename': _string_parser})
    def show(self, user, repo, sha):
        """Get an individual commit."""
        c = self._parsed('/'.join(['commits', 'show', user, repo, sha]))
        # Some fixup due to weird XML structure
        if hasattr(c, 'removed'):
            c.removed = [i[0] for i in c.removed]
        if hasattr(c, 'added'):
            c.added = [i[0] for i in c.added]
        return c

class IssuesEndpoint(BaseEndpoint):

    @with_temporary_mappings({'user': None})
    def search(self, user, repo, state, search_term):
        """Search the issues for the given repo for the given state and search term."""
        return self._parsed('/'.join(['issues', 'search', user, repo, state,
                                      hclient.quote_plus(search_term)]))

    @with_temporary_mappings({'user': None})
    def list(self, user, repo, state='open'):
        """Get the list of issues for the given repo in the given state."""
        return self._parsed('/'.join(['issues', 'list', user, repo, state]))

    @with_temporary_mappings({'user': None})
    def comments(self, user, repo, issue_id):
        return self._parsed('/'.join(['issues', 'comments', user, repo, str(issue_id)]))

    def add_comment(self, user, repo, issue_id, comment):
        """Add a comment to an issue."""
        return self._post('/'.join(['issues', 'comment', user,
                                    repo, str(issue_id)]),
                          comment=comment)

    @with_temporary_mappings({'user': None})
    def show(self, user, repo, issue_id):
        """Show an individual issue."""
        return self._parsed('/'.join(['issues', 'show', user, repo, str(issue_id)]))

    def add_label(self, user, repo, issue_id, label):
        """Add a label to an issue."""
        self._post('issues/label/add/' + user + '/'
                       + repo + '/' + label + '/' + str(issue_id))

    def remove_label(self, user, repo, issue_id, label):
        """Remove a label from an issue."""
        self._post('issues/label/remove/' + user + '/'
                   + repo + '/' + label + '/' + str(issue_id))

    def close(self, user, repo, issue_id):
        """Close an issue."""
        self._post('/'.join(['issues', 'close', user, repo, str(issue_id)]))

    def reopen(self, user, repo, issue_id):
        """Reopen an issue."""
        self._post('/'.join(['issues', 'reopen', user, repo, str(issue_id)]))

    def new(self, user, repo, title, body=''):
        """Create a new issue."""
        return self._posted('/'.join(['issues', 'open', user, repo]),
                            title=title, body=body)

    def edit(self, user, repo, issue_id, title, body):
        """Create a new issue."""
        self._post('/'.join(['issues', 'edit', user, repo, str(issue_id)]),
                   title=title, body=body)

class ObjectsEndpoint(BaseEndpoint):

    @with_temporary_mappings({'tree': Tree, 'type': _string_parser})
    def tree(self, user, repo, t):
        """Get the given tree from the given repo."""
        tl = self._parsed('/'.join(['tree', 'show', user, repo, t]))
        return dict([(t.name, t) for t in tl])

    @with_temporary_mappings({'blob': Blob})
    def blob(self, user, repo, t, fn):
        return self._parsed('/'.join(['blob', 'show', user, repo, t, fn]))

    def raw_blob(self, user, repo, sha):
        """Get a raw blob from a repo."""
        path = 'blob/show/%s/%s/%s' % (user, repo, sha)
        return self._raw_fetch(path).read()

class OrganizationsEndpoint(BaseEndpoint):

    def show(self, org):
        """Get the info of an organization."""
        return self._parsed('organizations/' + org)

    def forUser(self, username):
        """Get the organizations for the given user."""
        return self._parsed('user/show/' + username + "/organizations")

    def forMe(self):
        """Get the organizations for an authenticated user."""
        return self._parsed('organizations')

    def set(self, org, **args):
        """Set organization parameters.

        Organization parameters include the following:
         - name
         - email
         - blog
         - company
         - location
         - billing_email"""
        prepared_args = {}
        for k,v in args.items():
            prepared_args['organization[' + k + ']'] = v
        return self._put('/'.join(['organizations', org]),
            **prepared_args)

    def repositories(self):
        """List repositories across all the organizations that an authenticated user can access."""
        return self._parsed("organizations/repositories")

    def owners(self, org):
        """List the owners of an organization."""
        return self._parsed("organizations/" + org + "/owners")

    def publicRepositories(self, org):
        """List the public repositories for an organization."""
        return self._parsed("organizations/" + org + "/public_repositories")

    def publicMembers(self, org):
        """List the public members of an organization."""
        return self._parsed("organizations/" + org + "/public_members")


class TeamsEndpoint(BaseEndpoint):

    def addUserToTeam(self, team_id, username):
        self._post('teams/%s/members' % str(team_id), name=username)

    def addRepoToTeam(self, team_id, user, repo):
        self._post('teams/%s/repositories' % team_id, name="%s/%s" % (user, repo))

class GitHub(object):
    """Interface to github."""

    def __init__(self, user=None, token=None, fetcher=hclient.fetch, base_url=None):
        self.user    = user
        self.token   = token
        self.fetcher = fetcher

        if base_url:
            BaseEndpoint.BASE_URL = base_url

    @property
    def users(self):
        """Get access to the user API."""
        return UserEndpoint(self.user, self.token, self.fetcher)

    @property
    def repos(self):
        """Get access to the user API."""
        return RepositoryEndpoint(self.user, self.token, self.fetcher)

    @property
    def commits(self):
        return CommitEndpoint(self.user, self.token, self.fetcher)

    @property
    def issues(self):
        return IssuesEndpoint(self.user, self.token, self.fetcher)

    @property
    def objects(self):
        return ObjectsEndpoint(self.user, self.token, self.fetcher)

    @property
    def organizations(self):
        return OrganizationsEndpoint(self.user, self.token, self.fetcher)

    @property
    def teams(self):
        return TeamsEndpoint(self.user, self.token, self.fetcher)
