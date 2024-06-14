import operator
import collections
from itertools import groupby

from utils import *
from constants import *

def generate_grammar(grammar_output_path):
    """
    This function converts a PYAGS output grammar into a grammar that is parsable by CKY.
    This is useful for inductive segmentation.
    The CKY parser is not part of this package, but can be accessed from here:
    http://web.science.mq.edu.au/~mjohnson/Software.htm
    :param grammar_output_path: PYAGS grammar output
    :return: grammar map
    """

    try:
        grammar = []
        rules = defaultdict(int)
        nonterminal_counts = defaultdict(int)
        with open(grammar_output_path, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                if '-->' in line:
                    #Word nonterminal
                    if 'Word' in line:
                        grammar.append(line)
                else:
                    tokens = line.split()
                    key = tokens[0].replace('(', '').replace('#', '')
                    nonterminal_counts[key] += 1
                    values = []
                    terminal = '#' not in ''.join(tokens[1:])
                    para = 0
                    catch = False
                    #Read the parsing.
                    for token in tokens[1:]:
                        if '#' in token and para == 0:
                            catch = True
                            values.append( token.replace('(', '').replace('#', ''))
                        #Detect the characters.
                        elif terminal and re.match('^([a-f\d]{4,8})\)*$', token):
                            hex_str = token.replace(')', '')
                            values.append(convert_hex_to_string(hex_str))
                        elif token == '^^^' or token == '^^^)' or token == '$$$)':
                            values.append(token.replace(')', ''))
                        if catch:
                            para += token.count('(') - token.count(')')
                            if para == 0:
                                catch = False
                    if len(values) > 0:
                        rule = key + ' --> ' + ' '.join(values)
                        rules[rule] += 1

            #Append grammar rules.
            for rule in rules:
                grammar.append(str(rules[rule])+ ' ' +rule)
            for nonterminal_count in nonterminal_counts:
                grammar.append(str(nonterminal_counts[nonterminal_count])+' '+re.sub('\d+$', '', nonterminal_count) + ' --> ' + nonterminal_count)

        return grammar
    except:
        print(ERROR_MESSAGE)
        return None


def parse_segmentation_output(segmentation_output_path, prefix_nonterminal, stem_nonterminal, suffix_nonterminal,
                                normalized_segmentation_output_path, language, min_word_length_to_segment=3):
    """
    This function parses the output of a PYAGS segmentation output and generates
    a segmentation model that is used for the transductive and inductive segmentation
    and writes the segmentation output in a human-readable format.
    The format is compatible with the off-the-shelf evaluation utilities used in MorphoChallenge.
    http://morpho.aalto.fi/events/morphochallenge/
    The function also generates segmentation map that are then used for inductive segmentation.
    The prefixes, stems and suffixes should be either represented by either the same nonterminal
    or three different nonterminals.
    :param segmentation_output_path: a txt file that contains each words' morphology trees
    Stem morph in characters
    :param prefix_nonterminal: prefix nonterminal to parse
    :param stem_nonterminal: stem nonterminal to parse
    :param suffix_nonterminal: suffix nonterminal to parse
    :param normalized_segmentation_output_path: output path for the normalized segmentation
    compatible with evaluation utilities
    :param language: the language of the processed text (or None). This is only needed for the special
    lowercasing and uppercasing of Turkish.
    :param min_word_length_to_segment: integer that represents the minimum length of a
    word to be segmented (in characters)
    :return: a segmentation model: maps of normalized segmentation, morpheme counts, morpheme parsing
    and prefix-suffix compatibility
    If the nonterminals for the prefixes, stems and suffixes are the same (e.g., 'Morph' or 'Compound'),
    the maps for morpheme counts, morpheme parsing and prefix-suffix compatibility are void
    """
    try:
        if not ((stem_nonterminal == prefix_nonterminal and stem_nonterminal == suffix_nonterminal) or
            (stem_nonterminal != prefix_nonterminal and stem_nonterminal != suffix_nonterminal and prefix_nonterminal != suffix_nonterminal)):
            print("The prefixes, stems and suffixes should be either represented by either the same nonterminal or three different nonterminals!")
            return None

        #words and their segmentation
        word_segmentation_map = {}
        word_segmentation_lower_map = {}

        #Complex nonterminals and their counts
        complex_nonterminal_counts = {}
        complex_nonterminal_counts[PREFIX] = defaultdict(int)
        complex_nonterminal_counts[STEM] = defaultdict(int)
        complex_nonterminal_counts[SUFFIX] = defaultdict(int)

        #Complex nonterminals and their compositions (parsing)
        #e.g., 'ings' --> 'ing'+'s'
        complex_nonterminal_compositions = {}
        complex_nonterminal_compositions[PREFIX] = {}
        complex_nonterminal_compositions[STEM] = {}
        complex_nonterminal_compositions[SUFFIX] = {}

        prefix_suffix_compatibility = {}

        with open(segmentation_output_path, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()

                #----------------------------------------------------
                #Special handling for flipped prefixes and suffixes caused by ambiguous grammars
                #This handles AD-HOC nonerminals: Prefix, Stem, Suffix and their combinations (e.g., StemPrefix).
                #if re.match('^.*Suffix.*Char.*Stem.*$', line) or re.match('^.*Stem.*Char.*Prefix.*$', line) or re.match('^.*Suffix.*Char.*Prefix.*$', line):
                #    line = fix_output_line(line)
                #----------------------------------------------------

                if len(line) == 0:
                    continue;

                #Extract the morphemes given the nonterminals.
                morphs, extracted_nonterminals, tokens = get_morphs_from_tree(line, [prefix_nonterminal, stem_nonterminal, suffix_nonterminal])

                #Check that the extracted morphemes are in the correct order
                ordered_extracted_nonterminals = list(collections.OrderedDict(sorted(extracted_nonterminals.items())).values())
                ordered_extracted_nonterminals = [x[0] for x in groupby(ordered_extracted_nonterminals)]
                original_nonterminals = [prefix_nonterminal, stem_nonterminal, suffix_nonterminal]
                original_nonterminals = [x[0] for x in groupby(original_nonterminals)]
                correct_order= ' '.join(ordered_extracted_nonterminals) in ' '.join(original_nonterminals)

                word = ''
                segmented_word = ''
                if not correct_order:
                    ordered_tokens = list(collections.OrderedDict(sorted(tokens.items())).values())
                    word = ''.join(ordered_tokens)
                    segmented_word = ' '.join(ordered_tokens)
                else:
                    complex_prefix_lower = ''
                    complex_prefix_morphs_lower = ''
                    complex_suffix_lower = ''
                    complex_suffix_morphs_lower = ''
                    complex_stem_lower = ''
                    complex_stem_morphs_lower = ''
                    if stem_nonterminal == prefix_nonterminal and stem_nonterminal == suffix_nonterminal:
                        word += ''.join(morphs[stem_nonterminal])
                        segmented_word += ' '.join(morphs[stem_nonterminal])
                    else:
                        #Read the prefixes, and gather prefix information.
                        if prefix_nonterminal in morphs and len(morphs[prefix_nonterminal]) > 0:
                            complex_prefix = ''.join(morphs[prefix_nonterminal])
                            complex_prefix_lower = to_lower_case(complex_prefix, language)
                            if complex_prefix_lower not in complex_nonterminal_compositions[PREFIX]:
                                complex_nonterminal_compositions[PREFIX][complex_prefix_lower] = defaultdict(int)
                            complex_prefix_morphs_lower = ' '.join([to_lower_case(morph, language) for morph in morphs[prefix_nonterminal]])
                            complex_nonterminal_compositions[PREFIX][complex_prefix_lower][complex_prefix_morphs_lower] += 1
                            complex_nonterminal_counts[PREFIX][complex_prefix_lower] += 1
                            word += complex_prefix
                            segmented_word += ' '.join(morphs[prefix_nonterminal])
                        else:
                            complex_prefix_lower = ''
                            complex_nonterminal_counts[PREFIX][''] += 1
                        #Read the stems, and gather stem information.
                        if stem_nonterminal in morphs and len(morphs[stem_nonterminal]) > 0:
                            if len(segmented_word) > 0:
                                segmented_word += ' '
                            complex_stem = ''.join(morphs[stem_nonterminal])
                            complex_stem_lower = to_lower_case(complex_stem, language)
                            if complex_stem_lower not in complex_nonterminal_compositions[STEM]:
                                complex_nonterminal_compositions[STEM][complex_stem_lower] = defaultdict(int)
                            complex_stem_morphs_lower = ' '.join([to_lower_case(morph, language) for morph in morphs[stem_nonterminal]])
                            complex_nonterminal_compositions[STEM][complex_stem_lower][complex_stem_morphs_lower] += 1
                            complex_nonterminal_counts[STEM][complex_stem_lower] += 1
                            word += complex_stem
                            segmented_word += ' '.join(morphs[stem_nonterminal])
                        #Read the suffixes, and gather suffix information.
                        if suffix_nonterminal in morphs and len(morphs[suffix_nonterminal]) > 0:
                            if len(segmented_word) > 0:
                                segmented_word += ' '
                            complex_suffix = ''.join(morphs[suffix_nonterminal])
                            complex_suffix_lower = to_lower_case(complex_suffix, language)
                            if complex_suffix_lower not in complex_nonterminal_compositions[SUFFIX]:
                                complex_nonterminal_compositions[SUFFIX][complex_suffix_lower] = defaultdict(int)
                            complex_suffix_morphs_lower = ' '.join([to_lower_case(morph, language) for morph in morphs[suffix_nonterminal]])
                            complex_nonterminal_compositions[SUFFIX][complex_suffix_lower][complex_suffix_morphs_lower] += 1
                            complex_nonterminal_counts[SUFFIX][complex_suffix_lower] += 1
                            word += complex_suffix
                            segmented_word += ' '.join(morphs[suffix_nonterminal])
                        else:
                            complex_suffix_lower = ''
                            complex_nonterminal_counts[SUFFIX][''] += 1
                        #Record prefix-suffix compatibility.
                        if complex_prefix_lower not in prefix_suffix_compatibility:
                            prefix_suffix_compatibility[complex_prefix_lower] = []
                        if complex_suffix_lower not in prefix_suffix_compatibility[complex_prefix_lower]:
                            prefix_suffix_compatibility[complex_prefix_lower].append(complex_suffix_lower)

                        #Record segmentation information.
                        word_lower = to_lower_case(word, language)
                        word_segmentation_lower_map[word_lower] = {}
                        word_segmentation_lower_map[word_lower][PREFIX] = complex_prefix_morphs_lower
                        word_segmentation_lower_map[word_lower][STEM] = complex_stem_morphs_lower
                        word_segmentation_lower_map[word_lower][SUFFIX] = complex_suffix_morphs_lower

                #Do not segment too short words.
                if len(word) < min_word_length_to_segment:
                    segmented_word = word

                #Store segmentation output.
                if word_segmentation_map.get(word) is None:
                    word_segmentation_map[word] = segmented_word

        #Write segmented words and their eval-formatted segmentation to file system.
        if normalized_segmentation_output_path:
            write_word_segmentations_to_file(word_segmentation_map.items(), normalized_segmentation_output_path)

        segmentation_model = (word_segmentation_lower_map, complex_nonterminal_counts, complex_nonterminal_compositions, prefix_suffix_compatibility)
        return segmentation_model

    except:
        return None


def write_word_segmentations_to_file(word_segmentation, output_path):
    """
    This function writes normalized word segmentation into a file.
    The format is compatible with the off-the-shelf evaluation utilities used in MorphoChallenge.
    http://morpho.aalto.fi/events/morphochallenge/
    :param word_segmentation: a list of words and their normalized segmentation
    :param output_path: output path
    """

    try:
        with open(output_path, "w", encoding='utf-8') as fout:
            for w in word_segmentation:
                fout.write(w[0] + '\t' + w[1] + '\n')
    except:
        print(ERROR_MESSAGE)


def insert_splits(word, count, split_marker, solutions):
    """
    This function splits a given word into all the possible ways.
    The number of chunks is defined as "count".
    :param word: the word to split
    :param count: number of chunks
    :param split_marker: split marker
    :param solutions: output splits
    :return: output splits
    """

    try:
        #If count == 0, no more insertions necessary. Append current solution and return.
        if count == 0 and word not in solutions:
            solutions.append(word)
            return solutions
        if word in solutions:
            return solutions
        #Add a "+" in all possible places
        for i in range(len(word)+1):
            #Construct new split.
            new_split = word[:i] + split_marker + word[i:]
            #Ignore instances of empty stems (for example: "e++xample" will be ignored).
            if split_marker+split_marker in new_split:
                continue
            #Call recursively with a decremented count.
            insert_splits(new_split, count-1, split_marker, solutions)

        return solutions
    except:
        print(ERROR_MESSAGE)
        return None


def segment_text(text, segmentation_model, split_marker, stem_marker, do_not_segment_nonfirst_capitalized_words, language, min_word_length_to_segment=3):
    """
    This function morphologically segments a given text
    :param text: the text to be segmented
    :param segmentation_model: the segmentation model produced by 'parse_segmentation_output'
    :param split_marker: split_marker
    :param stem_marker: a marker that surrounds the stem.
    :param do_not_segment_nonfirst_capitalized_words: if True, the capitalized words that do not appear
    in the beginning of the text are not segmented.
    :param language: the language of the processed text (or None). This is only needed for the special
    lowercasing and uppercasing of Turkish.
    :param min_word_length_to_segment: integer that represents the minimum length of a
    word to be segmented (in characters)
    Note: when both split_marker and stem_marker are set to None, the function does only stemming
    :return: segmented text
    """

    try:
        #Read the segmentation model
        word_segmentation_map = segmentation_model[0]
        complex_nonterminal_counts = segmentation_model[1]
        complex_nonterminal_compositions = segmentation_model[2]
        prefix_suffix_compatibility = segmentation_model[3]

        words = text.strip().split()
        segmented_words = [] #List containing all the segmented replacements of word in original line.
        #Segment word by word.
        previous_word = None
        for index, word in enumerate(words):
            word_lower = to_lower_case(word, language)
            segmented_word = None
            #If the word is too short, do not segment it.
            #If the word is capitalized and is not the first word, while ignore_nonfirst_capitalized_words=True, do not segment it.
            if len(word) != len(word_lower) or len(word) < min_word_length_to_segment or (not is_new_sentence(previous_word) and word[0] != word_lower[0] and do_not_segment_nonfirst_capitalized_words):
                if not split_marker and not stem_marker:
                    segmented_word = word
                else:
                    segmented_word = stem_marker+word+stem_marker
            else:
                #Save the casing of all characters.
                casing = [ch != ch.lower() for ch in word]

                #If the word already exists in the segmentation map, replace with existing segmentation.
                analysis = {}
                if word_lower in word_segmentation_map:
                    analysis = word_segmentation_map[word_lower]
                #If the word is not in the segmentation map, find the best segmentation for it.
                else:
                    analysis[PREFIX] = ''
                    analysis[STEM] = word_lower
                    analysis[SUFFIX] = ''
                    max_score = 0
                    segmentations = []
                    #Generate al the possible splits
                    insert_splits(word_lower, 2, '+', segmentations)
                    for segmentation in segmentations:
                        segments = segmentation.split('+')
                        complex_prefix = segments[0]
                        complex_stem = segments[1]
                        complex_suffix = segments[2]
                        #Ignore words with unseen morphemes.
                        if complex_prefix not in complex_nonterminal_counts[PREFIX] or complex_stem not in complex_nonterminal_counts[STEM] or complex_suffix not in complex_nonterminal_counts[SUFFIX]:
                            continue
                        #Ignore words with incompatible prefix and suffix.
                        if complex_suffix not in prefix_suffix_compatibility[complex_prefix]:
                            continue
                        #Calculate the probability.
                        # score=p(segmentation)=count(prefix)/count_of_all_prefixes+count(stem)/count_of_all_stems+count(suffix)/count_of_all_suffixes
                        complex_prefix_prop = complex_nonterminal_counts[PREFIX][complex_prefix] / len(word_segmentation_map)
                        complex_stem_prop = complex_nonterminal_counts[STEM][complex_stem] / len(word_segmentation_map)
                        complex_suffix_prop = complex_nonterminal_counts[SUFFIX][complex_suffix] / len(word_segmentation_map)
                        score = complex_prefix_prop * complex_stem_prop * complex_suffix_prop
                        #Keep track of the segmentation that gives the highest score.
                        if score > max_score:
                            analysis[PREFIX] = max(complex_nonterminal_compositions[PREFIX][complex_prefix].items(), key=operator.itemgetter(1))[0] if len(complex_prefix) > 0 else ''
                            analysis[STEM] = max(complex_nonterminal_compositions[STEM][complex_stem].items(), key=operator.itemgetter(1))[0]
                            analysis[SUFFIX] = max(complex_nonterminal_compositions[SUFFIX][complex_suffix].items(), key=operator.itemgetter(1))[0]  if len(complex_suffix) > 0 else ''
                            max_score = score

                #Restore the actual casing.
                index = 0
                cased_analysis = {}
                for key in [PREFIX, STEM, SUFFIX]:
                    cased_morphs = []
                    for morph in analysis[key].split():
                        cased_morph = ''
                        for ch in morph:
                           if casing[index]:
                               cased_morph += to_upper_case(ch, language)
                           else:
                               cased_morph += to_lower_case(ch, language)
                           index += 1
                        cased_morphs.append(cased_morph)
                    cased_analysis[key] = ' '.join(cased_morphs)

                #Format the final segmentation.
                if not split_marker and not stem_marker:
                    segmented_word = ''.join(cased_analysis[STEM].split())
                else:
                    split_prefixes = cased_analysis[PREFIX].split()
                    split_stems = cased_analysis[STEM].split()
                    split_suffixes = cased_analysis[SUFFIX].split()
                    segmented_word = split_marker.join(split_prefixes) + stem_marker + split_marker.join(split_stems) + stem_marker + split_marker.join(split_suffixes)
                    segmented_word = segmented_word

            segmented_word = segmented_word.strip()
            segmented_word = re.sub('\s+', ' ', segmented_word)
            segmented_words.append(segmented_word)
            previous_word = word
        segmented_text = ' '.join(segmented_words)
        return segmented_text
    except:
        print(ERROR_MESSAGE)
        return None


def segment_file(input_path, output_path, segmentation_model, split_marker, stem_marker, do_not_segment_nonfirst_capitalized_words, language, min_word_length_to_segment=3, has_id=False):
    """
    This function morphologically segments a given file
    :param input_path: the input text file to segment
    :param output_path: the output text file of segmentation
    :param segmentation_model: the segmentation model produced by 'parse_segmentation_output'
    :param split_marker: split_marker
    :param stem_marker: a marker that surrounds the stem
    :param do_not_segment_nonfirst_capitalized_words: if True, the capitalized words that do not appear
    in the beginning of the lines are not segmented.
    :param language: the language of the processed text (or None). This is only needed for the special
    lowercasing and uppercasing of Turkish.
    :param has_id: whether the input file is a tabular one where the first column is an ID
    that should not be segmented
    :param min_word_length_to_segment: integer that represents the minimum length of a
    word to be segmented (in characters)
    """

    try:
        with open(output_path, "w", encoding='utf-8') as fout:
            with open(input_path, 'r', encoding="utf-8") as fin:
                for line in fin:
                    text = line.strip()
                    id = None
                    if has_id:
                        columns = text.split('\t')
                        id = columns[0].strip()
                        text = columns[1].strip()
                    segmented_line = segment_text(text, segmentation_model, split_marker, stem_marker, do_not_segment_nonfirst_capitalized_words, language, min_word_length_to_segment)
                    fout.write(((id+'\t') if has_id else '') + segmented_line + '\n')
    except:
        print(ERROR_MESSAGE)
