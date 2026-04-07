# Wiktionary Term Fetcher

This is the repository of a library to fetch all the available
nouns, adjectives or verbs from either [Wikidata](https://www.wikidata.org)
or [Wiktionary](https://en.wiktionary.org), in different languages.

* When this library is used in Wikidata mode (default since version 0.2.0), the
Wikidata SPARQL query endpoint is used to fetch

* When this library is used in Wiktionary mode (deprecated since version 0.2.0),
  standard Wiktionary API is used. Some false positives (words which
  are not of the required type) can be included.
  
In both cases, the generated file uses UTF-8 encoding, and it stores each word in a single line.

## Usage

The allowed parameters are these:

```bash
# wiktionary-fetcher --help
usage: wiktionary-fetcher [-h] [--lang LANG] [--terms {nouns,verbs,adjectives}]
                   [--fetcher {wikidata,wiktionary}]
                   output

Wiktionary term fetcher

positional arguments:
  output                Output file. If the name is '-', standard output will
                        be used

optional arguments:
  -h, --help            show this help message and exit
  --lang LANG           Language to be queried from. In Wikidata mode, any
                        valid shortcut can be used. In Wiktionary mode,
                        shortcuts for some common languages (en, es, ca, de,
                        fr) are accepted. In this last mode, you can also use
                        any valid language name being used in English
                        Wiktionary (for instance, 'French' or 'Basque').
                        (default: en)
  --terms {nouns,verbs,adjectives}
                        Terms type to be queried from either Wikidata or
                        Wiktionary (default: nouns)
  --fetcher {wikidata,wiktionary}
                        Which fetcher should be used (default: wikidata)
```

Usual patterns are

```bash
wiktionary-fetcher --lang en --terms verbs english_verbs.txt
wiktionary-fetcher --lang Japanese --terms nouns japanese_nouns.txt
```
