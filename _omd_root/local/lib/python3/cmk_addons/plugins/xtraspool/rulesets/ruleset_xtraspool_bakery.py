#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Shebang only needed for editor!

from cmk.rulesets.v1 import Label, Title, Help
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    Integer,
    SingleChoice,
    SingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    String,
    TimeSpan,
    TimeMagnitude,
    List,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, HostCondition, Topic

#~ def _validate_path(path):
    #~ check_forbidden(path)
    #~ check_directory_traversal(path)
    
#~ def check_forbidden(path):
    #~ if not re.compile('^/').match(path):
        #~ raise Exception("ValidationError")
    #~ forbidden = [ "^/etc", "^/root" ]
    #~ for d in forbidden:
        #~ r = re.compile(d)
        #~ if r.match(path):
            #~ raise Exception("ValidationError")
    
#~ def check_directory_traversal(path):
    #~ ptoks = path.split('/')
    #~ for d in ptoks:
        #~ if d == "..":
            #~ raise Exception("ValidationError")
        #~ elif d == ".ssh":
            #~ raise Exception("ValidationError")

def _form_spec_single_directory(title):
    return List(
        element_template = Dictionary(
            elements = {
                "directory": DictElement(
                    required = True,
                    parameter_form = String(
                        title = Title("Directory"),
                        # custom_validate = [_validate_path],
                    ),
                ),
                "follow_symlinks": DictElement(
                    required = True,
                    parameter_form = SingleChoice(
                        title = Title("Handling of symbolic links"),
                        # prefill = DefaultValue(value=False),
                    elements = {
                            SingleChoiceElement(name="ignore", title=Title("Ignore symlinks")),
                            SingleChoiceElement(name="follow", title=Title("Follow symlinks")),
                        },
                    ),
                ),
                "buffering": DictElement(
                    required = True,
                    parameter_form = SingleChoice(
                        title = Title("Buffering mode"),
                        # prefill = DefaultValue(value=False),
                        help_text = Help("Unbuffered output reads the spool file line by line and immediately emits every line. If a line contains invalid UTF-8, this and all following lines are ignored. With buffered output, the complete file will be read and only emitted if the file is valid UTF-8 and starts with an agent section (\"<<<some_text>>>\"). Further, piggyback sections will be closed and it will be made sure that the last line read contains a newline"),
                        elements = {
                            SingleChoiceElement(name="unbuffered", title=Title("Unbuffered stream output")),
                            SingleChoiceElement(name="buffered", title=Title("Buffered output with basic checks")),
                        },
                    ),
                ),
                "ignore_size": DictElement(
                    required = False,
                    parameter_form = Integer(
                        help_text = Help("Use this especially together with buffered output to ensure reasonable performance."),
                        title = Title("Size limit (use 0 for no limit)"),
                        unit_symbol = 'kB',
                    ),
                ),
                "max_age": DictElement(
                    required = False,
                    parameter_form = TimeSpan(
                        title = Title("Ignore spool files older than (use 0 for no limit)"),
                        displayed_magnitudes=[TimeMagnitude.SECOND, TimeMagnitude.MINUTE, TimeMagnitude.HOUR],
                        prefill=DefaultValue(0.0),
                    ),
                ),
            },
            # migrate=_tuple_do_dict_with_keys("directory", "follow_symlinks", "repair_output"),
        ),
        add_element_label=Label("Add new spool directory"),
        editable_order=False,
        title=title,
    )

def _parameter_form_bakery():
    return Dictionary(
        title = Title("Extra spool directories"),
        elements = {
            "dirs": DictElement(
                required = True,
                parameter_form=_form_spec_single_directory(
                    Title("Specify additional spool directories to retrieve agent output from")
                ),
            ),
        }
    )

rule_spec_xtraspool_bakery = AgentConfig(
    name = "xtraspool",
    title = Title("Extra spool directories"),
    topic = Topic.GENERAL,
    parameter_form = _parameter_form_bakery,
)

