#!/usr/bin/env python3

from cmk.rulesets.v1 import Label, Title, Help
from cmk.rulesets.v1.form_specs import (
    ServiceState,
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    Topic
)

def _parameter_form():
    return Dictionary(
        help_text = Help(
            "Specify the default states of the Xtraspool statistics service when certain "
            "types of information have been logged."
        ),
        elements = {
            "notes": DictElement(
                parameter_form = ServiceState(
                    title = Title("Service state for notes issued"),
                    help_text = Help(
                        "Notes are encountered when a file was ignored because symlink following "
                        "has been disabled or when a README or hidden file was found and ignored. "
                        "In most cases this has informational value only and you will want to "
                        "keep the state OK."
                    ),
                    prefill = DefaultValue(ServiceState.OK),
                ),
                required = True,
            ),
            "warnings": DictElement(
                parameter_form = ServiceState(
                    title = Title("Service state for warnings issued"),
                    help_text = Help(
                        "Warnings are issued when a file is bigger or older than the limit "
                        "configured. This typically means config has to be adjusted or the script "
                        "creating the spool file has to be checked."
                    ),
                    prefill = DefaultValue(ServiceState.WARN),
                ),
                required = True,
            ),
            "errors": DictElement(
                parameter_form = ServiceState(
                    title = Title("Service state for errors encountered"),
                    help_text = Help(
                        "Errors mean serious configuration issues or files that could not be read "
                        "or could not be parsed as UTF-8 where found."
                    ),
                    prefill = DefaultValue(ServiceState.CRIT),
                ),
                required = True,
            ),
        }
    )

rule_spec_xtraspool_stats = CheckParameters(
    name = "xtraspool_stats",
    title = Title("Xtraspool statistics"),
    topic = Topic.GENERAL,
    parameter_form = _parameter_form,
    condition = HostAndItemCondition(item_title=Title("Xtraspool statistics")),
)
