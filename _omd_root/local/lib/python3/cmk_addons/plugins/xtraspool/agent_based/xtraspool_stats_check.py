#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Shebang only needed for editor!
# (c) 2025-2026 Mattias Schlenker
#
# Check configuration for xtraspool

from cmk.agent_based.v2 import AgentSection, CheckPlugin, Service, Result, State, Metric, check_levels
import itertools
import json

def parse_xtraspool_stats(string_table):
    flatlist = list(itertools.chain.from_iterable(string_table))
    parsed = json.loads(" ".join(flatlist))
    return parsed

def discover_xtraspool_stats(section):
    yield Service()
    
def check_xtraspool_stats(params, section):
    summary = "{level}: {file} ignored, reason: {reason}"
    esummary = "ERROR: {file} unhandled, reason: {reason}"
    ccount = 0
    for k in section["notes"]:
        yield Result(
            state=State(params["notes"]),
            summary=summary.format(level="Note", file=k, reason=section["notes"][k])
        )
        ccount = ccount + 1
    for k in section["warnings"]:
        yield Result(
            state=State(params["warnings"]),
            summary=summary.format(level="Warning", file=k, reason=section["warnings"][k])
        )
        ccount = ccount + 1
    for k in section["errors"]:
        yield Result(
            state=State(params["errors"]),
            summary=esummary.format(file=k, reason=section["errors"][k])
        )
        ccount = ccount + 1
    if ccount < 1:
        yield Result(state=State.OK, summary="Everything is fine.")

agent_section_xtraspool_stats = AgentSection(
    name = "xtraspool_stats",
    parse_function = parse_xtraspool_stats,
)

check_plugin_xtraspool_stats = CheckPlugin(
    name = "xtraspool_stats",
    service_name = "Xtraspool statistics",
    discovery_function = discover_xtraspool_stats,
    check_function = check_xtraspool_stats,
    check_default_parameters = { 
        "notes": int(State.OK), 
        "warnings": int(State.WARN), 
        "errors": int(State.CRIT) 
    },
    check_ruleset_name = "xtraspool_stats",
)
