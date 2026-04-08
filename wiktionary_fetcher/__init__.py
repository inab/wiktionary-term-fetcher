#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wiktionary_fetcher, a library to fetch all the available
# nouns, adjectives or verbs from wiktionary, in different languages.
# Copyright (C) 2022-2026 Barcelona Supercomputing Center, José M. Fernández
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

__author__ = "José M. Fernández <https://orcid.org/0000-0002-4806-5140>"
__copyright__ = "© 2022-2026 Barcelona Supercomputing Center (BSC), ES"
__license__ = "LGPL-2.1"

# https://www.python.org/dev/peps/pep-0396/
__version__ = "0.2.1"

import argparse
import enum
import gzip
import http
import json
import logging
import shutil
import sys
import tempfile
import time

from typing import (
    cast,
    NamedTuple,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Iterator,
        Mapping,
        MutableMapping,
        Optional,
        Sequence,
        TextIO,
        Tuple,
        Union,
    )

    from typing_extensions import (
        Final,
        TypeAlias,
        TypedDict,
    )

    class SPARQLResultHead(TypedDict):
        vars: Sequence[str]

    class SPARQLResultResults(TypedDict):
        bindings: Sequence[Mapping[str, Mapping[str, str]]]

    class SPARQLResult(TypedDict):
        head: SPARQLResultHead
        results: SPARQLResultResults


import urllib.parse
import urllib.request


class ArgTypeMixin(enum.Enum):
    @classmethod
    def argtype(cls, s: "str") -> "enum.Enum":
        try:
            return cls(s)
        except:
            raise argparse.ArgumentTypeError(f"{s!r} is not a valid {cls.__name__}")

    def __str__(self) -> "str":
        return str(self.value)


class TermType(ArgTypeMixin):
    """
    The different term types
    """

    Noun = "nouns"
    Verb = "verbs"
    Adjective = "adjectives"


# noun => https://www.wikidata.org/wiki/Q1084
# verb => https://www.wikidata.org/wiki/Q24905
# adjective => https://www.wikidata.org/wiki/Q34698
TermType2Wikidata: "Final[Mapping[TermType, str]]" = {
    TermType.Noun: "wd:Q1084",
    TermType.Verb: "wd:Q24905",
    TermType.Adjective: "wd:Q34698",
}


class Lang(ArgTypeMixin):
    English = "en"
    Spanish = "es"
    Catalan = "ca"
    German = "de"
    French = "fr"


class WiktionarySetup(NamedTuple):
    lang: "Lang"
    category_prefix: "str"


if TYPE_CHECKING:
    TermFetcherProc: TypeAlias = Callable[
        [Union[str, Lang], Union[str, TermType]], Iterator[str]
    ]

WiktionarySetupsList: "Final[Tuple[WiktionarySetup, ...]]" = (
    WiktionarySetup(lang=Lang.English, category_prefix="English"),
    WiktionarySetup(lang=Lang.Spanish, category_prefix="Spanish"),
    WiktionarySetup(lang=Lang.Catalan, category_prefix="Catalan"),
    WiktionarySetup(lang=Lang.German, category_prefix="German"),
    WiktionarySetup(lang=Lang.French, category_prefix="French"),
)

WiktionarySetups: "Final[Mapping[Lang, WiktionarySetup]]" = {
    the_setup.lang: the_setup for the_setup in WiktionarySetupsList
}

WiktionaryEndpointBase: "Final[str]" = "https://en.wiktionary.org/w/api.php"
WiktionaryDumpsIndex: "Final[str]" = "https://dumps.wikimedia.org/index.json"

# Global logger for this module
logger = logging.getLogger(__name__)


def fetch_terms_from_wiktionary(
    lang: "Union[str, Lang]",
    term_type: "Union[str, TermType]",
) -> "Iterator[str]":
    import user_agent

    # Normalize the term type
    if not isinstance(term_type, TermType):
        term_type = TermType(term_type)

    # Normalize the language
    setup: "Optional[WiktionarySetup]"
    try:
        if not isinstance(lang, Lang):
            lang = Lang(lang)

        setup = WiktionarySetups.get(lang)
    except ValueError:
        # We are assuming it is a bare language name
        setup = None

    if setup is None:
        category_prefix = lang.value if isinstance(lang, Lang) else lang
    else:
        category_prefix = setup.category_prefix

    query_params: "Optional[MutableMapping[str, str]]" = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:" + category_prefix + "_" + term_type.value,
        "cmprop": "title",
        "cmlimit": "max",
        "format": "json",
    }

    # Now, build the query link
    while query_params is not None:
        req = urllib.request.Request(
            WiktionaryEndpointBase,
            method="POST",
            data=urllib.parse.urlencode(query_params).encode("utf-8"),
            headers={
                "User-Agent": user_agent.generate_user_agent()
                + f" {__name__}/{__version__}",
            },
        )
        with urllib.request.urlopen(req) as resp:
            json_terms = json.load(resp)
            for term_ent in json_terms.get("query", {}).get("categorymembers"):
                if term_ent.get("ns") == 0:
                    term = term_ent.get("title")
                    if ":" not in term:
                        yield term

            # Last
            cmcontinue = json_terms.get("continue", {}).get("cmcontinue")

        if cmcontinue is None:
            query_params = None
        else:
            query_params["cmcontinue"] = cmcontinue


DEFAULT_MAX_RETRIES: "Final[int]" = 5
DEFAULT_REQUEST_DELAY: "Final[float]" = 0.25
DEFAULT_USER_AGENT: "Final[str]" = f"wiktionary-term-fetcher/{__version__} (https://github.com/inab/wiktionary-term-fetcher/)"
WIKIDATA_SPARQL_ENDPOINT: "Final[str]" = "https://query.wikidata.org/sparql"


# This method is borrowed and adapted from
# https://github.com/inab/opeb-pub-enricher/blob/4a1d53d0bb147ac57b2a3395c716658af7d7555a/opeb_pub_enricher/wikidata_enricher.py#L134-L206
def _retriableSPARQLQuery(
    theQuery: "str",
    request_delay: "float" = DEFAULT_REQUEST_DELAY,
    max_retries: "int" = DEFAULT_MAX_RETRIES,
    sparql_endpoint: "str" = WIKIDATA_SPARQL_ENDPOINT,
    user_agent: "str" = DEFAULT_USER_AGENT,
) -> "SPARQLResult":
    import SPARQLWrapper

    if max_retries < 0:
        max_retries = DEFAULT_MAX_RETRIES
    if request_delay <= 0.0:
        request_delay = DEFAULT_REQUEST_DELAY

    logger.debug(f"SPARQL Query {theQuery}")

    retries = 0
    results: "SPARQLResult" = {"head": {"vars": []}, "results": {"bindings": []}}
    while retries <= max_retries:
        retryexc: "Optional[BaseException]" = None
        retrymsg = None
        retrysecs = None

        # https://www.mediawiki.org/w/index.php?title=Topic:V1zau9rqd4ritpug&topic_showPostId=v33czgrn0vmkzwkg#flow-post-v33czgrn0vmkzwkg
        sparql = SPARQLWrapper.SPARQLWrapper(sparql_endpoint, agent=user_agent)
        sparql.setRequestMethod(SPARQLWrapper.POSTDIRECTLY)

        sparql.setQuery(theQuery)
        sparql.setReturnFormat(SPARQLWrapper.JSON)
        try:
            results = cast("SPARQLResult", sparql.query().convert())

            # Avoiding to hit the server too fast
            time.sleep(request_delay)

            break
        except SPARQLWrapper.SPARQLExceptions.EndPointInternalError as sqe:
            retryexc = sqe
            retrymsg = "endpoint internal error"

            # Using a backoff time of 2 seconds when 500 or 502 errors are hit
            retrysecs = 2 + 2**retries
        except http.client.IncompleteRead as ir:
            retryexc = ir
            retrymsg = "incomplete read"

            # Using a backoff time of 2 seconds when 500 or 502 errors are hit
            retrysecs = 2 + 2**retries
        except urllib.error.HTTPError as he:
            retryexc = he
            if he.code == 429:
                retrysecs = he.headers.get("Retry-After")
                if retrysecs is not None:
                    # We add half a second, as the server sends only the integer part
                    # and some corner 0 seconds cases have happened
                    retrysecs = float(retrysecs) + 0.5
                    retrymsg = "code {}".format(he.code)
            elif he.code == 504:
                retrymsg = "code {}".format(he.code)

                # Using a backoff time of 2 seconds when 500 or 502 errors are hit
                retrysecs = 2 + 2**retries
        except BaseException as be:
            retryexc = be

        retries += 1
        if (retrysecs is not None) and (retries <= max_retries):
            logger.debug(f"Retry {retries} waits {retrysecs} seconds, due {retrymsg}")

            time.sleep(retrysecs)
        else:
            if retryexc is None:
                retryexc = Exception("Untraced sparql ERROR")

            logger.error("Query with ERROR: " + theQuery)

            raise retryexc
    return results


SPARQL_QUERY_TEMPLATE: "Final[str]" = """\
SELECT DISTINCT ?lemma WHERE {{
  ?lang wdt:P9060 {0!r}.
  ?lexemeId dct:language ?lang;
    wikibase:lexicalCategory {1};
    wikibase:lemma ?lemma.
}}
"""


def fetch_terms_from_wikidata(
    lang: "Union[str, Lang]",
    term_type: "Union[str, TermType]",
) -> "Iterator[str]":
    # Normalize the term type
    if not isinstance(term_type, TermType):
        term_type = TermType(term_type)

    # We need this for the next SPARQL query
    term_type_code = TermType2Wikidata[term_type]

    # Normalize the language
    setup: "Optional[WiktionarySetup]"
    try:
        if not isinstance(lang, Lang):
            lang = Lang(lang)

        setup = WiktionarySetups.get(lang)
    except ValueError:
        # We are assuming it is a bare language name
        setup = None

    # We are working with the ISO-3166-1 Alpha-2 and derivates used
    # by the annotations of languages within Wikidata
    if setup is None:
        iso_lang = lang.value if isinstance(lang, Lang) else lang
    else:
        iso_lang = setup.lang.value

    results = _retriableSPARQLQuery(
        SPARQL_QUERY_TEMPLATE.format(iso_lang, term_type_code)
    )

    # Shortcut: the name of the key to be looked at
    result_vars = results.get("head", {}).get("vars", [])
    result_bindings = results.get("results", {}).get("bindings", [])
    if len(result_vars) > 0 and len(result_bindings) > 0:
        lemma_key = result_vars[0]
        for binding in result_bindings:
            result_in_binding = binding.get(lemma_key)
            if (
                result_in_binding is not None
                and result_in_binding.get("xml:lang") == iso_lang
            ):
                the_value = result_in_binding.get("value")
                if the_value is not None:
                    yield the_value


# See https://stackoverflow.com/a/36502089

DEFAULT_TERM_FETCHER: "Final[str]" = "wikidata"
AvailableFetchers: "Mapping[str, TermFetcherProc]" = {
    DEFAULT_TERM_FETCHER: fetch_terms_from_wikidata,
    "wiktionary": fetch_terms_from_wiktionary,
}


def store_terms(
    lang: "Union[str, Lang]",
    term_type: "Union[str, TermType]",
    outH: "TextIO",
    term_fetcher: "TermFetcherProc" = fetch_terms_from_wikidata,
) -> "int":
    num_terms = 0
    for term in term_fetcher(lang, term_type):
        outH.write(term)
        outH.write("\n")
        num_terms += 1

    return num_terms
