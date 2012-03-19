#!/usr/bin/python

#===- nm.py - Python nm Example ------------------------------*- python -*--===#
#
#                     The LLVM Compiler Infrastructure
#
# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
#===------------------------------------------------------------------------===#

r"""
This file implements a basic version of the ubiquitous UNIX program, nm.

It demonstrates how to use the APIs in llvm.object to extract data from binary
object files. It doesn't strive for feature parity with nm, optimal
performance, or best coding practices. Instead, it serves to show people how
to harness the power of the object file parsing module.
"""

from argparse import ArgumentParser
from operator import attrgetter
from sys import exit

from llvm.object import ObjectFile

argparser = ArgumentParser('Python version of nm')
argparser.add_argument('filename', metavar='FILE', default='a.out',
        help='Object file to read')
argparser.add_argument('-n', '-v', '--numeric-sort', dest='sort_address',
        action='store_true',
        help='Sort symbols numerically by their address.')
argparser.add_argument('--size-sort', dest='sort_size', action='store_true',
        help='Sort symbols by their size.')
argparser.add_argument('-u', '--undefined-only', dest='undefined_only',
        action='store_true', default=False,
        help='Display only undefined symbols.')
argparser.add_argument('--defined-only', dest='defined_only',
        action='store_true', default=False,
        help='Display only symbols that are defined.')

args = argparser.parse_args()

# Parsing our object file is as simple as instantiating an ObjectFile instance.
of = ObjectFile(filename=args.filename)

# The current API requires us to cache attribute lookups. This is unfortunate.
# This is how we work around it.
def cache(symbols):
    for symbol in symbols:
        symbol.cache()
        yield symbol

# The logic here could be more concise if we fully used the dynamic properties
# of Python. Code is intentionally repetitive to make it easier to understand.
symbols = of.get_symbols()
if args.sort_size:
    symbols = sorted(cache(symbols), key=attrgetter('size'))
elif args.sort_address:
    symbols = sorted(cache(symbols), key=attrgetter('address'))

if args.undefined_only:
    for symbol in symbols:
        if not symbol.is_undefined:
            continue

        print '%s %s' % ( symbol.nm_char, symbol.name)

    exit(0)

if args.defined_only:
    for symbol in symbols:
        if symbol.is_undefined:
            continue

        print '%s %s' % ( symbol.nm_char, symbol.name)

    exit(0)

for symbol in symbols:
    print '%s %s %s' % ( hex(symbol.file_offset), symbol.nm_char, symbol.name )
