#!/usr/bin/env python3

from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, Unit, StrictPrecision
from cmk.graphing.v1.perfometers import Closed, FocusRange, Open, Perfometer

metric_xtraspool_warnings = Metric(
    name = "xtraspool_warnings",
    title = Title("Warnings"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.YELLOW,
)

metric_xtraspool_errors = Metric(
    name = "xtraspool_errors",
    title = Title("Errors"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.RED,
)

metric_xtraspool_files_transferred = Metric(
    name = "xtraspool_files_transferred",
    title = Title("Files transferred"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.GREEN,
)

graph_xtraspool_transfer_statistics = Graph(
    name="xtraspool_transfer_statistics",
    title=Title("Outdated packages and security updates"),
    simple_lines=[
        "xtraspool_warnings",
        "xtraspool_errors",
        "xtraspool_files_transferred",
    ],
)
