#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wiktionary_fetcher, a library to fetch all the available
# nouns, adjectives or verbs from wiktionary, in different languages.
# Copyright (C) 2022 Barcelona Supercomputing Center, José M. Fernández
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import sys
from . import *

def main():
    ap = argparse.ArgumentParser(
        description="Wiktionary term fetcher",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    ap.add_argument('--lang', dest="lang", help=f"Language to be queried from Wiktionary. Shortcuts for some common languages ({', '.join(map(lambda l: l.value, Lang))}) are accepted. You can also use any valid language name being used in English Wiktionary (for instance, 'French' or 'Basque').", default=Lang.English.value)
    ap.add_argument('--terms', dest="terms", help="Terms type to be queried from Wiktionary", type=TermType.argtype, choices=TermType, default=TermType.Noun)
    ap.add_argument('output', help="Output file. If the name is '-', standard output will be used")
    args = ap.parse_args()
    
    print(f"Writing all the {args.terms} in {args.lang} to {args.output}", file=sys.stderr)
    
    if args.output != "-":
        outH = open(args.output, mode="w", encoding="utf-8")
    else:
        outH = sys.stdout
    
    try:
        store_terms(args.lang, args.terms, outH)
    finally:
        # Assuring the stream is properly closed
        if outH != sys.stdout:
            outH.close()

if __name__ == "__main__":
    main()