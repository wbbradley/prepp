#!/usr/local/bin/python
from os.path import dirname, join, abspath, exists, expanduser, basename
import logging
import os
import sys
import re

logger = logging.getLogger(__name__)

def log(msg):
    logger.info("prepp : info : {}".format(msg))

def error(msg):
    logger.error("prepp : error : {}".format(msg))
    raise Exception(msg)

def usage():
    print "prepp <ext> <filename>"
    sys.exit(1)

if len(sys.argv) != 3:
    usage()

ws_tabs = 1
ws_spaces = 2

def is_uniform(str):
    if len(str) == 0:
        return True
    ch = str[0]
    for c in str:
        if c != ch:
            return False
    return True

def categorize(line, last_indent, last_ws_type):
    prefix = re.match(r"\s*", line).group()
    if not is_uniform(prefix):
        error('line does not have uniform indentation:\n{}\n'.format(line))
    indent = len(prefix)
    if indent > 0:
        line = line.lstrip()
        if prefix[0] == ' ':
            ws_type = ws_spaces
        else:
            ws_type = ws_tabs
    else:
        ws_type = last_ws_type
    return line, indent, ws_type

def get_indent(ws_type, indent):
    if indent > 0:
        if ws_type == ws_tabs:
            prefix = '\t' * indent
        else:
            prefix = ' ' * indent
    else:
        prefix = ''
    return prefix

def is_declaration(line_tokens):
    if line_tokens[0] == 'struct':
        return True
    if line_tokens[0] == 'class':
        return True
    if line_tokens[0] == 'enum':
        return True
    return False

def is_initializer(line_tokens):
    return line_tokens[-1] == '='

def line_needs_semicolon(line):
    if len(line) == 0:
        return False
    line_split = line.split()
    return is_initializer(line_split) or is_declaration(line_split)

def prepp_file(filename, file):
    indent = 0
    ws_type = 0
    line = ''
    line_num = 0
    stack = [False]
    for line in file:
        line_num = line_num + 1
        line = line.rstrip()
        line, next_indent, next_ws_type = categorize(line, indent, ws_type)
        if ws_type == 0:
            ws_type = next_ws_type

        if next_ws_type != ws_type:
            error('{}:{}: found mismatched tabs/spaces {} -> {} at line:\n{}'.format(filename, line_num, ws_type, next_ws_type, line))

        if len(line) == 0:
            continue

        prefix = get_indent(ws_type, next_indent)
        needs_semicolon = line_needs_semicolon(line)
        if next_indent == indent + 1:
            stack.append(needs_semicolon)
            print get_indent(ws_type, indent) + '{'
        elif next_indent > indent + 1:
            error('{}:{}: unexpected multiple indent'.format(filename, line_num))
        elif indent > next_indent:
            while indent > next_indent:
                # TODO print indents
                indent = indent - 1
                stack.pop()
                inner_needs_semicolon = stack[-1]
                print get_indent(ws_type, indent) + '}' + (';' if inner_needs_semicolon else '')
        stack[-1] = needs_semicolon

        print prefix + line

        ws_type = next_ws_type
        indent = next_indent

    while indent > 0:
        # TODO print indents
        indent = indent - 1
        stack.pop()
        inner_needs_semicolon = stack[-1]
        print get_indent(ws_type, indent) + '}' + (';' if inner_needs_semicolon else '')


def prepp_filename(filename):
    try:
        with open(filename) as file:
            prepp_file(filename, file)
    except IOError:
       print("failed to open {}".format(filename))
       sys.exit(1)

target_ext = sys.argv[1]
filename = sys.argv[2]

prepp_filename(filename)
sys.exit(0)
