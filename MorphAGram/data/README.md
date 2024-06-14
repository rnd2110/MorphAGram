
#### Grammar Information

Grammar: The name of the grammar as it appears in the publications.
X1: Grammar index in the data directory
X2: Prefix Segmentation Nonterminal
X3: Stem Segmentation Nonterminal
X4: Suffix Segmentation Nonterminal
X5: Seeded Prefix Nonterminal
X6: Seeded Suffix Nonterminal

| Grammar | X1 | X2 | X3 | X4 | X5 | X6 |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| PrStSu | 0 | PrefixMorph | Stem | SuffixMorph | PrefixMorph | SuffixMorph | 
| PrStSu+SM | 1 | PrefixMorph | Stem | SuffixMorph | PrefixMorph | SuffixMorph |
| PrStSu+Co+SM | 2 | PrefixMorphs | Stem | SuffixMorphs | PrefixMorph | SuffixMorph |
| Simple | 3 | Prefix | Stem | Suffix | Prefix | Suffix |
| Simple+SM | 4 | Prefix | Stem | Suffix | Prefix | Suffix |
| Morph+SM | 13 | Morph | Morph | Morph | Morph | Morph |
| PrStSu2a+SM | 15 | PrefixMorph | Stem | SuffixMorph | PrefixMorph | SuffixMorph |
| PrStSu2b+SM | 18 | PrefixMorph | Stem | SuffixMorph | PrefixMorph | SuffixMorph |
| PrStSu2b+Co+SM | 19 | PrefixMorphs | Stem | SuffixMorphs | PrefixMorph | SuffixMorph |

<br />

#### Important Notes

1. Every output file is produced 5 times in 5 separate runs, indicated with the `-1`, `-2`, `-3`, `-4` and `-5` suffixes. The results are the averages over the 5 runs.

2. In the publications, we adapt the seeded affixes (either in the scholar_seeded setting or the cascaded setting - We set both `concentration_param_alphaa` and `concentration_param_alphab` to 1). Further experiments show that when the seeded affixes are of low-quality (e.g., in the cascaded setting or when the affixes are collected by a non-expert of the underlying language), adaptation decreases the performance. However, adaptation helps when the seeded affixes are of high quality.

3. In the publications, we use the PrStSu2b+Co+SM grammar in the first round of the cascaded settings. Further experiments show that PrStSu+SM and PrStSu2a+SM can be used instead as they are as efficient as PrStSu2b+Co+SM and faster in sampling.

4. In the cascaded setups, the affixes are read from the output of the first round of learning based on the nonterminals specified in X2 and X4.

