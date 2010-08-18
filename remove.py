#!/usr/bin/env python

# A script to batch remove all repositories listed in config.json
# that are stored in the remote gh_user's acct.  This might be useful
# during initial setup.  Oh, and be *careful* with this thing!

import simplejson
import sys
import os
import urllib2
import urllib

# determine path to configuration file
cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
cfg_file = os.path.join(cwd, "config.json")

if not os.path.isfile(cfg_file):
    raise RuntimeError("config file missing, expected at: " + cfg_file)

# parse the configuration file
f = open(cfg_file)
j = simplejson.load(f)
f.close();

# validate config file
if not type(j) is dict or not j.has_key('repos') or not type(j['repos']) is dict:
    raise RuntimeError("malformed configuration file (requires a 'repos' key)")

for k in ['gh_user', 'gh_token', 'gh_tgt_acct', 'gh_ssh_alias']:
    if not j.has_key(k):
        raise RuntimeError("malformed configuration file (requires a '" + k + "' key)")

gh_user = j['gh_user']
gh_token = j['gh_token']

def getExistingGithubRepos(user):
    u = urllib2.urlopen("http://github.com/api/v2/json/repos/show/" + user)
    r = simplejson.loads(u.read())
    return [m["name"] for m in r['repositories']]

def deleteRepoOnGithub(name, user, token):
    # ohdamn, in this case we want to authenticate as auth_user but create
    # a repository in 'acct' where auth_user != acct.  At first blush it doesn't
    # appear this is supported in the github WSAPI:
    # http://develop.github.com/p/repo.html
    query_args = {
        'login': user,
        'token': token
        }
    request = urllib2.Request("https://github.com/api/v2/json/repos/delete/" + name)
    request.add_data(urllib.urlencode(query_args))
    r = simplejson.loads(urllib2.urlopen(request).read())

    # second post to seal the deal
    query_args['delete_token'] = r['delete_token']
    request = urllib2.Request("https://github.com/api/v2/json/repos/delete/" + name)
    request.add_data(urllib.urlencode(query_args))
    print urllib2.urlopen(request).read()
    return True

# and let's get the existing repositories that exist under the syncer account
# (the account that's authenticating, but not really where we want our repos to land)
reposOnGithub = getExistingGithubRepos(gh_user)

for repo in reposOnGithub:
    if not repo in [k for k in j['repos']]:
        continue

    print "need to kill " + repo

    deleteRepoOnGithub(repo, gh_user, gh_token)
