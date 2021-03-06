#!/usr/bin/python

import sys
import string
#import phonetic_algorithms_es

def prepareCorpus(c):
    splitted = c.split("\n")
    filtered = list(filter(None, splitted))
    result = list(map(lambda x : x[0].lower() + x[1:], filtered))
    return result

def reverseCorpus(c):
    reversed_corpus = []
    for line in c:
        words = line.split(" ")
        reversed_corpus.insert(0, " ".join(list(reversed(words))))
    return reversed_corpus

def generateDicts(corpus, span):
    startwords = []
    terminals = {}
    wordstats = {}
    for line in corpus:
        words = line.split(" ")
        length = len(words)
        if(span > 1):
            words = [" ".join(words[i : i + span]) for i in range(0, length, span)]
            length = len(words)
        terminals[words[length - 1]] = True
        startwords.insert(0, words[0])
        for i, word in enumerate(words):
            if i < length - 1:
                if word in wordstats:
                    wordstats[word].insert(0, words[i+1])
                else:
                    wordstats[word] = [words[i+1]]
    return (startwords, terminals, wordstats)

# def generateMetaphoneDict(s):
#     pa = phonetic_algorithms_es.PhoneticAlgorithmsES()
#     word_to_metaphone = {}
#     metaphone_to_words = {}
#     metaphone_matches = {}
#
#     for word in s:
#         word_to_metaphone[word] = pa.metaphone(word)
#
#     for metaphone in word_to_metaphone.values():
#         metaphone_to_words[metaphone] = []
#
#     for word, metaphone in word_to_metaphone.items():
#         for metaphone2 in metaphone_to_words:
#             if metaphone2.endswith(metaphone):
#                 metaphone_to_words[metaphone2].insert(0, word)
#
#     for word, metaphone in word_to_metaphone.items():
#         metaphone_matches[word] = metaphone_to_words[metaphone]
#
#     return metaphone_matches

def stringListJs (l):
    js = "["
    if len(l) == 0:
        return js + "]"

    js += "\"" + l[0] + "\""
    for item in l[1:]:
        js += ",\"" + item + "\""

    return js + "]"

def boolJs (b):
    if b:
        return "true"
    else:
        return "false"

def dictionaryJs (d, p):
    js = "{"
    if not bool(d):
        return js + "}"

    l = list(d.items())
    js += "\"" + l[0][0] + "\":" + p(l[0][1])
    for key, words in l[1:]:
        js += ",\"" + key + "\":" + p(words)

    return js + "}"

def prepareJsVars(suffix, startwords, terminals, wordstats):
    startwords_js = "var startwords" + suffix + "="
    terminals_js = "var terminals"+ suffix + "="
    wordstats_js = "var wordstats"+ suffix + "="

    startwords_js += stringListJs(startwords) + ";\n"
    terminals_js += dictionaryJs(terminals, boolJs) + ";\n"
    wordstats_js += dictionaryJs(wordstats, stringListJs) + ";\n"

    js = startwords_js + terminals_js + wordstats_js
    return js

# def metaphoneMatchesJs(m):
#     metaphone_js = "var metaphone_matches="
#     metaphone_js += dictionaryJs(m, stringListJs) + ";\n"
#     return metaphone_js

def markovJs (suffix):
    markov_js = "var markov" + suffix + "="
    markov_js += "new markov(startwords" + suffix + ","
    markov_js += "terminals" + suffix + ","
    markov_js += "wordstats" + suffix + ");"
    return markov_js

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print ("Specify 2 corpus files: lyrics titles")
        exit()

    with open(sys.argv[1], 'r') as corpus:
        lyrics = corpus.read()

    js = []
    prepared_lyrics = prepareCorpus(lyrics)

    (s, t, w) = generateDicts(prepared_lyrics, 2)
    js.append(prepareJsVars("lyrics", s, t, w))

    with open(sys.argv[2], 'r') as corpus:
        titles = corpus.read()

    prepared_titles = prepareCorpus(titles)

    (s, t, w) = generateDicts(prepared_titles, 1)
    js.append(prepareJsVars("titles", s, t, w))

    # reversed_corpus = reverseCorpus(prepared_corpus)
    #
    # (s, t, w) = generateDicts(reversed_corpus, 1)
    # js.append(prepareJsVars("bw1", s, t, w))

    # metaphone_matches = generateMetaphoneDict(s)
    # js.append(metaphoneMatchesJs(metaphone_matches))

    # (s, t, w) = generateDicts(reversed_corpus, 2)
    # js.append(prepareJsVars("bw2", s, t, w))

    with open("js/markov.js", 'r') as markovjs:
        m = markovjs.read()
        js.append(m)

    js.append(markovJs("lyrics"))
    js.append(markovJs("titles"))

    # js.append(markovJs("bw1"))
    # js.append(markovJs("bw2"))

    with open("js/functions.js", 'r') as cjs:
        cm = cjs.read()
        js.append(cm)

    with open("js/cumbia.js", "w") as cumbia:
        cumbia.write("\n".join(js))
