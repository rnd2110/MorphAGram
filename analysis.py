from utils import *
from constants import *

def get_affix_features(segmentation_output_path, prefix_nonterminal, suffix_nonterminal, min_appearance=10):
    """
    This function generates affix-related features, used to run the ML classifiers for the selection
    of the nearly optimal grammars.
    This function is only applicable when the prefixes and suffixes are represented by different nonterminals.
    :param segmentation_output_path: file containing grammar morph tree for each word
    :param prefix_nonterminal: prefix nonterminal to search for
    :param suffix_nonterminal: suffix nonterminal to search for
    :param min_count: minimum count of the morph to be considered
    :return: information for prefixes, suffixes, affixes, complex prefixes, complex suffixes and complex affixes
    The information is: type count, token count, average count per word and average length
    """

    try:
        word_count = 0

        prefix_counter = defaultdict(int)
        suffix_counter = defaultdict(int)
        affix_counter = defaultdict(int)

        complex_prefix_counter = defaultdict(int)
        complex_suffix_counter = defaultdict(int)
        complex_affix_counter = defaultdict(int)

        with open(segmentation_output_path, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                word_count += 1
                #Search for a nonterminal match with a morph RegEx given as input.
                morphs, _, _ = get_morphs_from_tree(line, [prefix_nonterminal, suffix_nonterminal])
                #Separate into respective affix counter.
                complex_prefix = ''
                complex_suffix = ''
                for nonterminal in morphs:
                    #Record prefix, suffix and affix information.
                    for morph in  morphs[nonterminal]:
                        affix_counter[morph] += 1
                        is_prefix = (nonterminal == prefix_nonterminal)
                        if is_prefix:
                            prefix_counter[morph] += 1
                            complex_prefix += morph
                        else:
                            suffix_counter[morph] += 1
                            complex_suffix += morph

                #Record complex prefix, complex suffix and complex affix information.
                if len(complex_prefix) > 0:
                    complex_prefix_counter[complex_prefix] += 1
                    complex_affix_counter[complex_prefix] += 1
                if len(complex_suffix) > 0:
                    complex_suffix_counter[complex_suffix] += 1
                    complex_affix_counter[complex_suffix] += 1

        #Prepare the final output.
        output_dict = {PREFIX: analyze_morph_dict(prefix_counter, word_count, min_appearance),
                       SUFFIX: analyze_morph_dict(suffix_counter, word_count, min_appearance),
                       AFFIX: analyze_morph_dict(affix_counter, word_count, min_appearance),
                       COMPLEX_PREFIX: analyze_morph_dict(complex_prefix_counter, word_count, min_appearance),
                       COMPLEX_SUFFIX: analyze_morph_dict(complex_suffix_counter, word_count, min_appearance),
                       COMPLEX_AFFIX: analyze_morph_dict(complex_affix_counter, word_count, min_appearance)}

        return output_dict
    except:
        print(ERROR_MESSAGE)
        return None

def analyze_morph_dict(morph_dict, word_count, min_appearance):
    """
    This function gets affix-related features given an affix dictionary and word count
    :param morph_dict: dictionary containing morphs and their counts
    :param word_count: total number of words the morph information is generated from
    :param min_count: minimum count of the morph to be considered
    :return: overall information: type count, average count per word, average length
    """

    try:
        type_count = 0
        token_count = 0
        average_length = 0
        for key in morph_dict:
            count = morph_dict[key]
            if count < min_appearance:
                continue
            type_count += 1
            token_count += count
            average_length += len(key)
        average_count_per_word = token_count/word_count
        average_length = average_length/type_count
        return {TYPE_COUNT: type_count,
                AVERAGE_COUNT_PER_WORD: average_count_per_word,
                AVERAGE_LENGTH: average_length}
    except:
        print(ERROR_MESSAGE)
        return None

def analyze_gold(gold_path):
    """
    This function analyzes gold segmentation.
    The analysis is assumed to be applicable to the corresponding language as long as
    the gold is a well representative sample.
    :param gold_path: the path of the gold segmentation
    :return: 1) gold information: word-morph mapping, number of morphs, unweighted/weighted degree of ambiguity,
    average token/type morph length, average number of morphs per word, and max number of morphs in a word, and
    2) morph-information (for each morph): count, frequency and probability (the probability that a sequence of
    characters forms the corresponding morph)
    """

    try:
        gold_word_morphs = {}
        morph_info = {}
        all_text = []
        max_number_of_morphs_per_word = -1
        morph_token_count = 0
        word_count = 0

        #Read the gold file.
        with open(gold_path, 'r', encoding="utf-8") as fin:
            #Read the gold, word by word.
            for line in fin:
                columns = line.strip().split('\t')
                word = columns[0]
                gold_word_morphs[word] = []
                segmentations = columns[1].split(',')
                word_count += len(segmentations)
                #Consider all possible word segmentation
                for segmentation in segmentations:
                    gold_word_morphs[word].append(defaultdict(int))
                    unsegmented_word = segmentation.replace(' ', '') #might be different from word for inflection
                    all_text.append(unsegmented_word)
                    morphs = segmentation.split()
                    #Keep track of the maximum number of morphs per word
                    if len(morphs) > max_number_of_morphs_per_word:
                        max_number_of_morphs_per_word = len(morphs)
                    #Keep track of word-morph mapping and counts and length information.
                    for morph in morphs:
                        if morph not in morph_info:
                            morph_info[morph] = {}
                            morph_info[morph][COUNT] = 0
                        gold_word_morphs[word][-1][morph] += 1
                        morph_info[morph][COUNT] += 1
                        morph_token_count += 1

        total_morph_token_length = 0
        total_morph_type_length = 0
        total_morph_probability = 0
        total_weighted_morph_probability = 0
        all_text_str = ' '.join(all_text)
        #Loop over the morphs.
        for morph in morph_info:
            #Keep track of length information.
            total_morph_token_length += morph_info[morph][COUNT]*len(morph)
            total_morph_type_length += len(morph)
            #Keep track of frequency information.
            morph_info[morph][FREQUENCY] = morph_info[morph][COUNT]/morph_token_count
            #Keep track of probability information.
            morph_probability = morph_info[morph][COUNT]/all_text_str.count(morph)
            morph_info[morph][PROBABILITY] = morph_probability
            total_morph_probability += morph_probability
            total_weighted_morph_probability += morph_info[morph][FREQUENCY]*morph_probability

        morph_type_count = len(morph_info)
        #Calculate the degrees of ambiguity.
        degree_of_ambiguity = 1-2*abs(0.5-(total_morph_probability/morph_type_count));
        weighted_degree_of_ambiguity = 1-2*abs(0.5-total_weighted_morph_probability);

        #Calculate length information.
        average_morph_token_length = total_morph_token_length/morph_token_count
        average_morph_type_length = total_morph_type_length/morph_type_count

        #Calculate the average number of morphs per word.
        average_number_of_morphs_per_word = morph_token_count/word_count

        #Prepare the final gold information.
        gold_info = {MORPH_TYPE_COUNT: morph_type_count,
                     DEGREE_OF_AMBIGUITY: degree_of_ambiguity,
                     WEIGHTED_DEGREE_OF_AMBIGUITY: weighted_degree_of_ambiguity,
                     AVERAGE_MORPH_TOKEN_LENGTH: average_morph_token_length,
                     AVERAGE_MORPH_TYPE_LENGTH: average_morph_type_length,
                     AVERAGE_NUMBER_OF_MORPHS_PER_WORD: average_number_of_morphs_per_word,
                     MAX_NUMBER_OF_MORPHS_PER_WORD: max_number_of_morphs_per_word,
                     SEGMENTATION: gold_word_morphs}

        return gold_info, morph_info
    except:
        print(ERROR_MESSAGE)
        return None, None

def analyze_output(output_path, gold_path):
    """
    This function analyzes the performance of system segmentation given the gold.
    :param output_path: the path of the output segmentation
    :param gold_path: the path of the gold segmentation
    :return: morph-information (for each morph): count, frequency, probability when it appears,
    precision, recall and F1-score
    """

    try:
        #First, analyze the gold.
        gold_info, morph_info = analyze_gold(gold_path)
        gold_word_morphs = gold_info[SEGMENTATION]

        morph_gold_counts = defaultdict(int)
        morph_output_counts = defaultdict(int)
        morph_common_counts = defaultdict(int)

        output_word_morphs = {}
        #Read the output segmentation
        with open(output_path, 'r', encoding="utf-8") as fin:
            for line in fin:
                columns = line.strip().split('\t')
                word = columns[0]
                output_word_morphs[word] = defaultdict(int)
                morphs = columns[1].split()
                for morph in morphs:
                    output_word_morphs[word][morph] += 1

        #Read the gold segmentation
        for word in gold_word_morphs:
            output_segmentation = output_word_morphs[word] if word in output_word_morphs else defaultdict(int)
            #When 2+ gold segmentations are available, consider the one that is closest to the output segmentation.
            selected_gold_segmentation = gold_word_morphs[word][0]
            if len (gold_word_morphs[word]) > 1:
                min_non_match_score = 100
                for gold_segmentation in gold_word_morphs[word]:
                    non_match_score = 0
                    for morph in gold_segmentation:
                        non_match_score += (gold_segmentation[morph] if morph not in output_segmentation else abs(gold_segmentation[morph] - output_segmentation[morph]))
                    if non_match_score < min_non_match_score:
                        min_non_match_score = non_match_score
                        selected_gold_segmentation = gold_segmentation
            #Keep track of the appearance of the morph in the gold, the output and both.
            for morph in selected_gold_segmentation:
                morph_output_counts[morph] += output_segmentation[morph]
                morph_gold_counts[morph] += selected_gold_segmentation[morph]
                morph_common_counts[morph] += (min(selected_gold_segmentation[morph],output_segmentation[morph]) if morph in output_segmentation else 0)

        #Prepare the final morph information.
        for morph in morph_info:
            precision = (morph_common_counts[morph] / morph_output_counts[morph])  if (morph in morph_common_counts and morph in morph_output_counts and morph_output_counts[morph] > 0) else 0
            recall = (morph_common_counts[morph] / morph_gold_counts[morph])  if (morph in morph_common_counts and morph in morph_gold_counts and morph_gold_counts[morph] > 0) else 0
            f1score = (2*recall*precision/(recall+precision)) if recall+precision > 0 else 0
            morph_info[morph][PRECISION] = precision
            morph_info[morph][RECALL] = recall
            morph_info[morph][F1SCORE] = f1score

        return morph_info
    except:
        print(ERROR_MESSAGE)
        return None

