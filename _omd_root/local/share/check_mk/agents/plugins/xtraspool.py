#!/usr/bin/env python3
# (c) 2025 Mattias Schlenker

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

# Check for forbidden directories and relative directories

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
            raise Exception("FoundDirectoryTraversal")
        elif d == ".ssh":
            raise Exception("TryingToAccessSSH")

# Do not output hidden files and READMEs

def check_filename(dircfg, file):
    if file[0] == '.':
        return [ 'NoteIgnoreHiddenFile' ]
    p = re.compile('^readme', re.IGNORECASE)
    if p.match(file):
        return [ 'NoteIgnoreReadMe' ]
    return []

# Modification time is not determined by filename, but as a per directory
# option read from the config

def check_mtime(dircfg, file):
    errors = []
    maxage = 0
    if 'max_age' in dircfg:
        maxage = int(dircfg['max_age'])
    if maxage == 0:
        return errors
    fmtime = os.path.getmtime(dircfg['directory'] + '/' + file)
    now = time.time()
    if (now - fmtime > maxage):
        errors.append("HintFileTooOld: Last modified {}, max age {}".format(fmtime, maxage))
    return errors

# Check the size of a file

def check_size(dircfg, file):
    errors = []
    maxsize = 0
    if 'ignore_size' in dircfg:
        maxsize = dircfg['ignore_size'] * 1000
    if maxsize == 0:
        return errors
    fsize = os.path.getsize(dircfg['directory'] + '/' + file)
    if fsize > maxsize:
        errors.append("HintFileTooLarge: {} bytes is larger than specified maximum: {}".format(fsize, maxsize)) 
    return errors

# Ignore symlinks if requested

def check_symlink(dircfg, file):
    errors = []
    ignore_symlinks = False
    if 'follow_symlinks' in dircfg:
        if dircfg['follow_symlinks'] == 'ignore':
            ignore_symlinks = True
    if os.path.islink(dircfg['directory'] + '/' + file) and ignore_symlinks :
        errors.append("NoteIsSymlink: Requested to ignore symlinks")
    return errors
       
# Check everything above and log errors

def check_everything(dircfg, file):
    errors = check_symlink(dircfg, file)
    errors = errors + check_size(dircfg, file)
    errors = errors + check_filename(dircfg, file)
    errors = errors + check_mtime(dircfg, file)
    return errors

# Walk through files in a directory and output files
# according to the config for this directory

def dump_all_files(dircfg, errors):
    errors[dircfg['directory']] = {}
    errors[dircfg['directory']]['files'] = []
    dir_cont = []
    try:
        check_forbidden(dircfg)
        check_directory_traversal(dircfg)
        dir_cont = os.listdir(dircfg['directory'])
    except Exception as e:
        errors[dircfg['directory']]['directory'] = str(e)
    buffered = False
    if 'buffering' in dircfg:
        if dircfg['buffering'] == "buffered":
            buffered = True
    for f in dir_cont:
        e = check_everything(dircfg, f)
        # print(e)
        if len(e) < 1:
            if buffered:
                e = dump_buffered(dircfg, f)
            else:
                e = dump_unbuffered(dircfg, f)
        if len(e) > 0:
            errors[dircfg['directory']]['files'].append({ f: e })
    return errors

# Buffered output of a single file

def dump_buffered(dircfg, file):
    errors = []
    lines = []
    inside_piggy = False
    try:
        f = open(dircfg['directory'] + '/' + file, 'r')
        for line in f:
            lines.append(line.strip('\n'))
        f.close()
    except Exception as e:
        errors.append(str(e))
        return errors
    ssr = re.compile('^<<<.+>>>$')
    psr = re.compile('^<<<<.+>>>>$')
    per = re.compile('^<<<<>>>>$')
    if not ssr.match(lines[0]):
        errors.append('ErrorNoAgentSection')
        return errors
    for l in lines:
        if psr.match(l):
            inside_piggy = True
        if per.match(l):
            inside_piggy = False
        print(l)
    if inside_piggy == True:
        print('<<<<>>>>')
        errors.append('WarnFixedPiggybackSection')
    return errors

# Unbuffered output of a single file

def dump_unbuffered(dircfg, file):
    errors = []
    try:
        f = open(dircfg['directory'] + '/' + file, 'r')
    except Exception as e:
        errors.append(str(e))
        return errors
    try:
        for line in f:
            print(line, end='')
    except Exception as e:
        f.close
        errors.append(str(e))
        return errors
    f.close
    return errors

errors = {}
cfgfile = os.environ['MK_CONFDIR'] + '/xtraspool.json'
with open(cfgfile) as f:
    cfg = json.load(f)

for dir in cfg['dirs']:
    errors = dump_all_files(dir, errors)

# Output statistics, to be later used by an agent plugin
print('<<<xtraspool_stats>>>')
print(json.dumps(errors))
