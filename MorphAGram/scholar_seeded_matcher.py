import sys

from preprocessing import *

AFFIX_COUNT = 100

lk_path = sys.argv[1]
segmentation_output_path = sys.argv[2]
prefix_morpheme = sys.argv[3]
suffix_morpheme = sys.argv[4]

# Read linguistic knowledge
lk_prefixes, lk_suffixes = read_linguistic_knowledge(lk_path)

# Read affixes.
_, prefixes, suffixes = get_top_affixes(segmentation_output_path, AFFIX_COUNT, prefix_morpheme, suffix_morpheme)

# Count matches.
match = 0
for prefix in prefixes:
    if prefix in lk_prefixes:
        match += 1
for suffix in suffixes:
    if suffix in lk_suffixes:
        match += 1

print('Matched affixes: '+str(match))
