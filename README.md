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


