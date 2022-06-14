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

__author__ = 'José M. Fernández <https://orcid.org/0000-0002-4806-5140>'
__copyright__ = '© 2022 Barcelona Supercomputing Center (BSC), ES'
__license__ = 'LGPL-2.1'

# https://www.python.org/dev/peps/pep-0396/
__version__ = '0.1.0'

import argparse
import enum
import json
from typing import Iterator, Mapping, MutableMapping
from typing import NamedTuple, Optional, Union

import urllib.parse
import urllib.request


class ArgTypeMixin(enum.Enum):
    @classmethod
    def argtype(cls, s: str) -> enum.Enum:
        try:
            return cls(s)
        except:
            raise argparse.ArgumentTypeError(
                f"{s!r} is not a valid {cls.__name__}")

    def __str__(self) -> str:
        return str(self.value)

class TermType(ArgTypeMixin):
    """
    The different term types
    """
    Noun = 'nouns'
    Verb = 'verbs'
    Adjective = 'adjectives'

class Lang(ArgTypeMixin):
    English = "en"
    Spanish = "es"
    Catalan = "ca"
    German = "de"

class WiktionarySetup(NamedTuple):
    lang: Lang
    category_prefix: str

EN_setup = WiktionarySetup(
    lang=Lang.English,
    category_prefix="English"
)

ES_setup = WiktionarySetup(
    lang=Lang.Spanish,
    category_prefix="Spanish"
)

CA_setup = WiktionarySetup(
    lang=Lang.Catalan,
    category_prefix="Catalan"
)

DE_setup = WiktionarySetup(
    lang=Lang.German,
    category_prefix="German"
)

WiktionarySetups: Mapping[Lang, WiktionarySetup] = {
    EN_setup.lang: EN_setup,
    ES_setup.lang: ES_setup,
    CA_setup.lang: CA_setup,
    DE_setup.lang: DE_setup,
}

WiktionaryEndpointBase = 'https://en.wiktionary.org/w/api.php'

def fetch_terms(lang: Union[str, Lang], term_type: Union[str, TermType]) -> Iterator[str]:
    # Normalize the term type
    if not isinstance(term_type, TermType):
        term_type = TermType(term_type)
    
    # Normalize the language
    setup: Optional[WiktionarySetup]
    try:
        if not isinstance(lang, Lang):
            lang = Lang(lang)
        
        setup = WiktionarySetups.get(lang)
    except ValueError:
        # We are assuming it is a bare language name
        setup = None
        
    if setup is None:
        category_prefix = lang
    else:
        category_prefix = setup.category_prefix
    
    query_params: Optional[MutableMapping[str, str]] = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:" + category_prefix + "_" + term_type.value,
        "cmprop": "title",
        "cmlimit": "max",
        "format": "json"
    }
    
    # Now, build the query link
    while query_params is not None:
        req = urllib.request.Request(WiktionaryEndpointBase, method="POST", data=urllib.parse.urlencode(query_params).encode("utf-8"))
        with urllib.request.urlopen(req) as resp:
            json_terms = json.load(resp)
            for term_ent in json_terms.get("query", {}).get("categorymembers"):
                if term_ent.get("ns") == 0:
                    term = term_ent.get("title")
                    if (":" not in term):
                        yield term
            
            # Last
            cmcontinue = json_terms.get("continue",{}).get("cmcontinue")
        
        if cmcontinue is None:
            query_params = None
        else:
            query_params['cmcontinue'] = cmcontinue

def store_terms(lang: Union[str, Lang], term_type: Union[str, TermType], outH):
    num_terms = 0
    for term in fetch_terms(lang, term_type):
        outH.write(term)
        outH.write("\n")
        num_terms += 1
    
    return num_terms