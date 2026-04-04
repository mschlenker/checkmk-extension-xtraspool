#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Shebang only needed for editor!
# (c) 2025-2026 Mattias Schlenker
#
# Bakery configuration for xtraspool

import json
from pathlib import Path
from typing import Iterable, TypedDict, List

from .bakery_api.v1 import (
    OS,
    Plugin,
    PluginConfig,
    Scriptlet,
    register,
    FileGenerator,
    ScriptletGenerator,
    quote_shell_string,
)

def get_linux_cfg_lines(conf):
    config = json.dumps(conf)
    return config.splitlines()

def get_xtraspool_plugin_files(conf):
    yield Plugin(
        base_os = OS.LINUX,
        source = Path('xtraspool.py'),
        target = Path('xtraspool.py')
    )
    yield PluginConfig(
        base_os = OS.LINUX,
        lines = get_linux_cfg_lines(conf),
        target = Path('xtraspool.json'),
        include_header = False
    )

register.bakery_plugin(
    name = "xtraspool",
    files_function = get_xtraspool_plugin_files,
)
