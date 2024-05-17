#! /usr/bin/env python3


import sys

current_word  = None
current_count = 0
word          = ''

for line in sys.stdin:
        (word, count) = line.split('\t', 1)

        count = int(count)
        if word == current_word:
                current_count += count
        else:
                if current_word:
                        print ("%s\t%s" % (current_word, current_count))
                current_count = count
                current_word = word

if word == current_word:
        print ("%s\t%s" % (word, current_count))
