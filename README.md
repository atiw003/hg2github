# Overview

This directory contains a small pile of scripts and instructions to 
stand up automatic synchronization from some number of mercurial
repositories to some number of repositories on github.

The config.json file that lives here specifies both the sources and 
destinations of the syncing.

# Prerequisites

* mercurial 1.6 or greater (version requirement for bookmark support)
* python 2.5 or greater
* dulwich (version 0.6.1 or greater recommended for recent fixes):
  http://samba.org/~jelmer/dulwich/
* hg-git: http://github.com/schacon/hg-git
  (if you have spaces in your mercurial tags, you may want this version:
   git://github.com/schacon/hg-git)
* simplejson for config.json parsing

# Setup and use

In order to put this script to use, you need to do the following:

## write config.json

You can copy config.json.example to config.json and sprinkle the following
in the file:

* `gh_user` - the github user that you will authenticate as
* `gh_token` - the authentication token of gh_user (from github)
* `gh_ssh_alias` - an ssh alias that will be used to connect over ssh for
  pushing changes (see discussion below)
* `gh_tgt_acct` - the target account where you'd like repositories to
  reside (may differ from gh_user when gh_user is a member of an organization.
* `repos` a map of repository descriptions, mapping the name to an object
   containing desription, src hg url, destination, and homepage.  Destination
   and homepage contain information that will initially be used to create repositories,
   and may changed later via github's api

## generate a passphraseless keypair

In order to allow ssh to authenticate to github, you must generate a keypair, and 
upload the public key to github to allow you to be recognized.  The private part
of this keypair should be reasonably secured.  Simply:

   ssh-keygen -t rsa -f id_rsa

## set up an ssh alias

For proper ssh authentication (and to let github authenticate you and associated
you with a user account), you must set up an alias in your `.ssh/config` file.  That
alias should then be named in config.json, as mentioned above.  Here is a sample
alias:

    Host github-alias
         HostName github.com
         User git
         IdentityFile /Users/lth/dev/hg2github/id_rsa

**NOTE:** IdentityFile is a path to the private key generated above.

# Bugs/Caveats

* All of the bugs in dulwich are also bugs of this script
* Github's API doesn't support creation of repositories in an acct other than of the
  user whom you are authenticating as.  That said, if you have a situation where
  gh_user != gh_acct_user (that is, you're trying to push repositories into a organization,
  and authenticating as a user with read/write permissions as that user), then you'll
  need to manually fork repositories over from the user to the organization after
  their creation.  Subsequent to that the `syncit.py` script should push to the correct
  location.
* hg-git, and git specifically, don't really like repositories with no commits.  Attempting
  to sync from such repositories may fail.  But then, it's really kinda of a useless thing to
  do, anyway. 
* git allows fewer chars in tags than hg, so if there are tags with spaces in your mercurial
  repository, they won't be properly sync'd.  You'll get error messages like:
  error: refusing to create funny ref 'refs/tags/last change before major code purge/reorg' remotely
  A solution is to grab the patch from this fork of hg-git:
  git://github.com/schacon/hg-git
