#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    choices=['qlog', 'qcommit', 'qshelve', 'qannotate', 'qdiff', 'qadd', 'qconflicts'], help="command of qbzr")
parser.add_argument("path", metavar='path', nargs=1, \
    help=" relative path to file or folder which is inside a bzr repository")
args = parser.parse_args()

# inputs
qbzr_cmd = args.qbzr_cmd[0] # command of qbzr
path = args.path[0] # path to file or folder

# get absolute path
absolutepath = os.path.abspath(path)

# check path validity
if not (os.path.isdir(absolutepath) or os.path.isfile(absolutepath)) :
    raise NameError("Invalid path.")

# if absolutepath is the path to a file, absolutepath should be cleaned by the file name
filename = ""
if os.path.isfile(absolutepath):
    filename = os.path.basename(absolutepath)
    absolutepath = os.path.dirname(absolutepath)

# find the base bzr repository
if os.path.isdir(absolutepath) :
    mountpath = absolutepath
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

# get the relative path to be used inside the container
relativepath = "." + absolutepath.replace(mountpath, "")

# if shared repo, need to mount the upper directory
checkpath = os.path.dirname(mountpath)
checkpath = os.path.join(checkpath, ".bzr")
if os.path.exists(checkpath) :
    repositoryname = os.path.basename(mountpath)
    repositorypath = os.path.join(repositorypath, repositoryname)
    mountpath = os.path.dirname(mountpath)
    
# append the filename to the relative path
relativepath = relativepath + "/" + filename

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
docker_cmd = "docker run --rm -e DISPLAY=unix$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v " \
             + mountpath + ":/workdir -t " + qbzr_docker_image + ":bionic /bin/bash -c \"bzr whoami \\\"" \
             + bzrwhoami + "\\\" && cd " + repositorypath + " && bzr " + qbzr_cmd + " " + relativepath + "\""

# run the container
try :
    os.system(docker_cmd)
except OSError as err :
    print("OS error: {0}".format(err))
    print("Something went wrong. Check your docker installation.")

#print("all done")
