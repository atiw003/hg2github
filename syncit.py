#!/usr/bin/env python

import simplejson
import sys
import os
import urllib2
import urllib

# determine path to configuration file
basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
cfg_file = os.path.join(basedir, "config.json")
work_dir = os.path.join(basedir, "work")

if not os.path.isfile(cfg_file):
    raise RuntimeError("config file missing, expected at: " + cfg_file)

# create work directory if neccesary
if not os.path.exists(work_dir) and not os.path.isdir(work_dir):
    os.mkdir(work_dir)

if not os.path.isdir(work_dir):
    raise RuntimeError("cannot create work directory: " + work_dir)

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
gh_tgt_acct = j['gh_tgt_acct']
gh_ssh_alias =  j['gh_ssh_alias']

def getExistingGithubRepos(user):
    u = urllib2.urlopen("http://github.com/api/v2/json/repos/show/" + user)
    r = simplejson.loads(u.read())
    return [m["name"] for m in r['repositories']]

def createRepoOnGithub(name, desc, homepage, acct, auth_user, auth_token):
    # ohdamn, in this case we want to authenticate as auth_user but create
    # a repository in 'acct' where auth_user != acct.  At first blush it doesn't
    # appear this is supported in the github WSAPI:
    # http://develop.github.com/p/repo.html
    query_args = {
        'name': name,
        'description': desc,
        'homepage': homepage,
        'public': 1,
        'login': auth_user,
        'token': auth_token
        }
    request = urllib2.Request("https://github.com/api/v2/json/repos/create")
    request.add_data(urllib.urlencode(query_args))

    print urllib2.urlopen(request).read()
    return True

def tryAndWhine(cmd, whinery):
    x = os.system(cmd + " 2>&1 > /dev/null")
    if not x == 0:
        print whinery

# now let's hit github and get a list of repositories already created there
# under our target user
existingRepos = getExistingGithubRepos(gh_tgt_acct)

# and let's get the existing repositories that exist under the syncer account
# (the account that's authenticating, but not really where we want our repos to land)
existingReposOops = getExistingGithubRepos(gh_user)

for repo in j['repos']:
    # more data validation.  we need a lil' schema here! /me swears
    for k in ['homepage', 'src', 'desc']:
        if not j['repos'][repo].has_key(k):
            raise RuntimeError("'"+repo+"' repository is missing a '" + k + "' key" )
    tgt_dir = os.path.join(work_dir, repo)
    src = j['repos'][repo]['src']
    homepage = j['repos'][repo]['homepage']
    desc = j['repos'][repo]['desc']

    if os.path.isdir(tgt_dir):
        # in this case, the directory already exists, we'll assume that we've
        # already cloned the repository and pull updates
        os.chdir(tgt_dir)
        tryAndWhine("hg pull \"" + src + "\"", "Failed to pull from " + src)
    else:
        # the directory doesn't exist!  We should clone fresh 
        tryAndWhine("hg clone \"" + src + "\" \"" + tgt_dir + "\"", "Failed to clone from " + src)
        os.chdir(tgt_dir)
        # after clone, make a bookmark of default hg branch so master
        # is created upon push to git
        tryAndWhine("hg bookmark -r default master", "Failed to set master 'bookmark'")

    # now, does the repository exist on github?  If not, create it
    pushto = gh_user
    if repo in existingRepos:
        pushto = gh_tgt_acct
    elif repo in existingReposOops:
        # all output will result in an email message (this script is destined for
        # a cronjob.)  This message *should* generate a nagging email.
        print 'OOPS, please manually fork repo "http://github.com/' + gh_user + "/" + repo + \
              "' to '"+ "'http://github.com/"+gh_tgt_acct+"/" + repo + "'"
    else:
        createRepoOnGithub(repo, desc, homepage, gh_tgt_acct,
                           gh_user, gh_token)

    # now it's time to push changes over to github
    # TODO: figure out how to feed privkey and uname to ssh run via git
    tryAndWhine("hg push git+ssh://" + gh_ssh_alias + "/" + pushto + "/" + repo,
                "failed attempting to push " + repo)
