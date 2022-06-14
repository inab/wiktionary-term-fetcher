# wiktionary_fetcher

This is the repository of a library to fetch all the available
nouns, adjectives or verbs from wiktionary, in different languages.

Standard Wiktionary API is used. Some false positives (words which
are not of the required type) can be included. The generated file
uses UTF-8 encoding, and it stores each word in a single line.

## Usage

The allowed parameters are these:

```bash
# wiktionary-fetcher --help
usage: wiktionary-fetcher [-h] [--lang LANG] [--terms {nouns,verbs,adjectives}] output

Wiktionary term fetcher

positional arguments:
  output                Output file. If the name is '-', standard output will be used

optional arguments:
  -h, --help            show this help message and exit
  --lang LANG           Language to be queried from Wiktionary. Shortcuts for some common languages (en, es, ca, de) are
                        accepted. You can also use any valid language name being used in English Wiktionary. (for instance,
                        'French' or 'Basque'). (default: en)
  --terms {nouns,verbs,adjectives}
                        Terms type to be queried from Wiktionary (default: nouns)
```

Usual patterns are

```bash
wiktionary-fetcher --lang en --terms verbs english_verbs.txt
wiktionary-fetcher --lang Japanese --terms nouns japanese_nouns.txt
```
