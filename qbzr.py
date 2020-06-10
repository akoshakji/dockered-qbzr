#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# anwar koshakji
# (c) 2020 all rights reserved
#

## Required: docker installation
## The script launches a docker container which runs qbzr on a specified file or folder.
## Docker container is then automatically removed.
##
## Inputs: 
## 1) qbzr command (qlog, qcommit, qshelve, qannotate, qdiff, qadd, qconflicts) 
## 2) path to the file or folder present in the bzr repository

# imports
import os
import sys
import argparse
from argparse import RawTextHelpFormatter

# check that the docker image is present on the system.
qbzr_docker_image = "akoshakji/qbzr"
try :
    docker_images = os.popen("docker images").read()[:-1]
except OSError as err :
    print("OS error: {0}".format(err))
    print("Error retrieving docker images. Check your docker installation")
    raise

# loop over all docker images
imageIsFound = False
for line in docker_images.splitlines() :
    if line.split(' ', 1)[0] == qbzr_docker_image : 
        imageIsFound = True
        break
    
# if qbzr image was not found, pull it from docker hub
if not imageIsFound :
    try :
        print("Pulling qbzr from docker...")
        os.system("docker pull akoshakji/qbzr")
    except OSError as err :
        print("OS error: {0}".format(err))
        print("Failed to pull the image. Run docker login first.")
        raise

# parse input
parser = argparse.ArgumentParser(description='Run qbzr using docker container\n\n' \
    'Maintainer: Anwar Koshakji https://github.com/akoshakji',  formatter_class=RawTextHelpFormatter)
parser.add_argument("qbzr_cmd", metavar='qbzr_cmd', nargs=1, \
    help="command of qbzr (e.g. qlog, qshelve, qcommit, ...)")
parser.add_argument("qbzr_input", metavar='qbzr_input', nargs='*',\
    help="path to files or folders that are passed as input to qbzr command")
args = parser.parse_args()

# inputs
qbzr_cmd = args.qbzr_cmd[0]   # command of qbzr
qbzr_input = args.qbzr_input  # input to qbzr command

# if no paths were passed as input, take the current directory
noinputs = False
if not qbzr_input :
    noinputs = True
    qbzr_input = [os.getcwd()]

# gather all the input on the same string
absolutepaths = []
for path in qbzr_input :
    # get absolute path
    absolutepaths.append(os.path.abspath(path))
    # check path validity
    if not (os.path.isdir(absolutepaths[-1]) or os.path.isfile(absolutepaths[-1])) :
        raise NameError("Invalid path.")

# take the first path in the input list as reference path
referencepath = absolutepaths[0]

# if referencepath is the path to a file, referencepath should be cleaned by the file name
if os.path.isfile(referencepath):
    referencepath = os.path.dirname(referencepath)

# find the base bzr repository and the corresponding mountpath
if os.path.isdir(referencepath) :
    mountpath = referencepath
    checkpath = os.path.join(mountpath, ".bzr")
    while not (os.path.exists(checkpath) or (mountpath == "/")) :
        mountpath = os.path.dirname(mountpath)
        checkpath = os.path.join(mountpath, ".bzr")

# if bzr repository was not found, raise an error
if mountpath == "/" :
    raise NameError("No bzr repository found")

# Repository name and local path
repositoryname = os.path.basename(mountpath)
repositorypath = "."

# get the relative path to be used inside the container. If no inputs were
# specified, qbzr command is applied to the base repository
relativepath = ""
if noinputs :
    relativepath = " ."
else:
    for path in absolutepaths :
        relativepath = relativepath + " " + os.path.relpath(path, mountpath)

# in case of a shared repo, mount in docker the upper directory with the main .bzr, 
# but act on the most nested repository (the specific iteration)
checkpath = os.path.dirname(mountpath)
checkpath = os.path.join(checkpath, ".bzr")
if os.path.exists(checkpath) :
    repositoryname = os.path.basename(mountpath)
    repositorypath = os.path.join(repositorypath, repositoryname)
    mountpath = os.path.dirname(mountpath)

# catch who I am in bzr, removing new line char
try :
    bzrwhoami = os.popen("bzr whoami").read()[:-1]
except OSError :
    print("bzr does not know who I am! Please run bzr whoami")
    bzrwhoami = ""

# debug print
#print("Bzr identity:", bzrwhoami)
#print("Mount point:", mountpath)
#print("Repository:", repositoryname)
#print("Relative path:", relativepath)
#print("Qbzr command to execute:", qbzr_cmd)

# full docker command
docker_cmd =   "docker run --rm -e DISPLAY=unix$DISPLAY" \
             + " -v /tmp/.X11-unix:/tmp/.X11-unix" \
             + " -u $(id -u $USER):$(id -g $USER)" \
             + " -v /etc/group:/etc/group:ro" \
             + " -v /etc/passwd:/etc/passwd:ro" \
             + " -v /etc/shadow:/etc/shadow:ro" \
             + " -v /etc/sudoers.d:/etc/sudoers.d:ro" \
             + " -v $HOME/.config/breezy:$HOME/.bazaar:rw" \
             + " -v $HOME/.bzr.log:$HOME/.bzr.log:rw" \
             + " -v " + mountpath + ":/workdir" \
             + " -t " + qbzr_docker_image + ":bionic" \
             + " /bin/bash -c \"bzr whoami \\\"" + bzrwhoami + "\\\"" \
             + " && cd " + repositorypath \
             + " && bzr " + qbzr_cmd + relativepath \
             + "\""

# run the container
try :
    #print(docker_cmd)
    os.system(docker_cmd)
except OSError as err :
    print("OS error: {0}".format(err))
    print("Something went wrong. Check your docker installation.")

#print("all done")
