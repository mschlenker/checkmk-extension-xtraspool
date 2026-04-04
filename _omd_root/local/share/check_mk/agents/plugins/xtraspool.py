#!/usr/bin/env python3
# (c) 2025-2026 Mattias Schlenker

# This script expects a configuration file $MK_CONFDIR/xtraspool.json
#
# {
#  "dirs": [
#    {
#      "directory": "/tmp/test23",
#      "follow_symlinks": "ignore",
#      "buffering": "buffered",
#      "ignore_size": 64,
#      "max_age": 1800
#    },
#    {
#      "directory": "/tmp/test42",
#      "follow_symlinks": "follow",
#      "buffering": "unbuffered"
#    }
#  ]
# }

import os
import json
import re
import time

# Check for forbidden directories or relative pathnames

def check_forbidden(dircfg):
    if not re.compile('^/').match(dircfg['directory']):
        raise Exception("RelativePathProvided")
    forbidden = [ "^/etc", "^/root" ]
    for d in forbidden:
        r = re.compile(d)
        if r.match(dircfg['directory']):
            raise Exception("ForbiddenDirectory")

# Check for directory traversal

def check_directory_traversal(dircfg):
    ptoks = dircfg['directory'].split('/')
    for d in ptoks:
        if d == "..":
            raise Exception("DirectoryTraversalAttempted")
        elif d == ".ssh":
            raise Exception("TryingToAccessSSH")

# Do not output hidden files and READMEs

def check_filename(dircfg, file):
    if file[0] == '.':
        raise Exception("IgnoreHiddenFile")
    p = re.compile('^readme', re.IGNORECASE)
    if p.match(file):
        raise Exception("IgnoreReadMe")

# Modification time is not determined by filename, but as a per directory
# option read from the config

def check_age(dircfg, file):
    maxage = 0
    if 'max_age' in dircfg:
        maxage = int(dircfg['max_age'])
    if maxage == 0:
        return
    fpath = dircfg['directory'] + '/' + file
    # At this point, the check whether symlinks are allowed has been passed:
    fpath = os.path.realpath(fpath)
    fmtime = os.path.getmtime(fpath)
    now = time.time()
    if (now - fmtime > maxage):
        raise Exception("FileTooOld")

# Check the size of a file

def check_size(dircfg, file):
    maxsize = 0
    if 'ignore_size' in dircfg:
        maxsize = dircfg['ignore_size'] * 1000
    if maxsize == 0:
        return
    fsize = os.path.getsize(dircfg['directory'] + '/' + file)
    if fsize > maxsize:
        raise Exception("FileTooLarge")

# Ignore symlinks if requested

def check_symlink(dircfg, file):
    ignore_symlinks = False
    if 'follow_symlinks' in dircfg:
        if dircfg['follow_symlinks'] == 'ignore':
            ignore_symlinks = True
    if os.path.islink(dircfg['directory'] + '/' + file) and ignore_symlinks :
        raise Exception("IgnoreSymlinks")

# Walk through files in a directory and output files
# according to the config for this directory

def dump_all_files(dircfg, stats):
    # Return on the first error encountered:
    dir_cont = []
    try:
        check_forbidden(dircfg)
        check_directory_traversal(dircfg)
        dir_cont = os.listdir(dircfg['directory'])
    except Exception as e:
        stats["errors"][dircfg['directory']] = str(e)
        return stats
    buffered = False
    if 'buffering' in dircfg:
        if dircfg['buffering'] == "buffered":
            buffered = True
    for f in dir_cont:
        if buffered:
            stats = dump_buffered(dircfg, f, stats)
        else:
            stats = dump_unbuffered(dircfg, f, stats)
    return stats

# Buffered output of a single file

def dump_buffered(dircfg, file, stats):
    fpath = dircfg['directory'] + '/' + file
    # Check whether to ignore file based on attributes
    try:
        check_filename(dircfg, file)
        check_symlink(dircfg, file)
    except Exception as e:
        stats["notes"][fpath] = str(e)
        return stats
    # Check whether the file is too big or too old
    try:
        check_size(dircfg, file)
        check_age(dircfg, file)
    except Exception as e:
        stats["warnings"][fpath] = str(e)
        return stats
    lines = []
    inside_piggy = False
    # Now try to read the whole file as one
    try:
        f = open(fpath, 'r')
        for line in f:
            lines.append(line.strip('\n'))
        f.close()
    except Exception as e:
        stats["warnings"][fpath] = str(e)
        return stats
    ssr = re.compile('^<<<.+>>>$')
    psr = re.compile('^<<<<.+>>>>$')
    per = re.compile('^<<<<>>>>$')
    if not ssr.match(lines[0]):
        stats["warnings"][fpath] = 'ErrorNoAgentSection'
        return stats
    for l in lines:
        if psr.match(l):
            inside_piggy = True
        if per.match(l):
            inside_piggy = False
        print(l)
    if inside_piggy == True:
        print('<<<<>>>>')
        stats["warnings"][fpath] = 'ErrorNoAgentSection'
    return stats

# Unbuffered output of a single file

def dump_unbuffered(dircfg, file, stats):
    fpath = dircfg['directory'] + '/' + file
    # Check whether to ignore file based on attributes
    try:
        check_filename(dircfg, file)
        check_symlink(dircfg, file)
    except Exception as e:
        stats["notes"][fpath] = str(e)
        return stats
    # Check whether the file is too big or too old
    try:
        check_size(dircfg, file)
        check_age(dircfg, file)
    except Exception as e:
        stats["warnings"][fpath] = str(e)
        return stats
    # Now try to read the file line by line, immediately emitting
    try:
        f = open(fpath, 'r')
    except Exception as e:
        stats["errors"][fpath] = str(e)
        return stats
    try:
        for line in f:
            print(line, end='')
    except Exception as e:
        f.close
        stats["errors"][fpath] = str(e)
        return stats
    f.close
    return stats

stats = {
    "notes" : {},
    "warnings" : {},
    "errors" : {}
}
cfgfile = os.environ['MK_CONFDIR'] + '/xtraspool.json'
if not os.path.exists(cfgfile):
    stats["errors"][cfgfile] = "ConfigFileMissing"
else:
    with open(cfgfile) as f:
        cfg = json.load(f)
    for dir in cfg['dirs']:
        stats = dump_all_files(dir, stats)

# Output statistics, to be later used by an agent plugin
print('<<<xtraspool_stats>>>')
print(json.dumps(stats))
