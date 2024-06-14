from utils import *
from constants import *

def process_words(word_list_file):
    """
    This function reads a file of words and produces word-level and character-level information.
    :param word_list_file: a file of words, one per line. '#' and '//' are used for comments.
    :return: a list of unique words, a list of unique words in the HEX representation and a
    list of unique characters in the HEX representation
    """

    try:
        words = []
        encoded_words = []
        hex_chars = []
        #Loop over the file and process word by word.
        with open(word_list_file, 'r', encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                #Ignore comment lines.
                if not line or line.startswith('#') or line.startswith('//'):
                    continue
                word = line
                words.append(word)
                #Covert the word to its HEX representation.
                encoded_word = convert_string_to_hex(word)
                encoded_words.append(encoded_word)
                #Keep track of the unique characters (in the HEX representation).
                hex_chars.extend(encoded_word.split())
        #Sort the outputs.
        words.sort()
        encoded_words.sort()
        hex_chars = sort_unique(hex_chars)
        return set(words), set(encoded_words), hex_chars
    except:
        print(ERROR_MESSAGE)
        return None, None, None


def write_encoded_words(encoded_words, output_path):
    """
    This function writes a list of encoded words (in the HEX representation) into a file.
    :param encoded_words: a list of encoded words
    :param output_path: output path
    """

    try:
        with open(output_path, 'w') as fout:
            fout.writelines('^^^ %s $$$\n' % word for word in encoded_words)
    except:
        print(ERROR_MESSAGE)


def read_grammar(grammar_file):
    """
    This function reads a grammar file and returns a map of the grammar rules.
    :param grammar_file: the path of a grammar file
    :return: grammar map. The keys represent the unique LHS terms, while
    the values are a list of the RHS terms of the corresponding keys
    """

    try:
        grammar = defaultdict(list)
        #Loop over the file and process rule by rule.
        with open(grammar_file, 'r', encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                #Ignore comment lines.
                if not line or line.startswith('#') or line.startswith('//'):
                    continue
                #Read the current rule.
                columns = line.partition('-->')
                key = columns[0].strip()
                value = columns[2].strip()
                grammar[key].append(value)
        return grammar
    except:
        print(ERROR_MESSAGE)
        return None


def write_grammar(grammar, output_path):
    """
    This function writes a grammar map into a file.
    :param grammar: grammar map
    :param output_path: output path
    """

    try:
        with open(output_path, 'w', encoding="utf-8") as fout:
            for key in grammar:
                for value in grammar[key]:
                    fout.write(key + ' --> ' + value + '\n')
    except:
        print(ERROR_MESSAGE)


def add_chars_to_grammar(grammar, hex_chars):
    """
    This function writes a grammar map into a file - Default AG parameters: 1, 1
    :param grammar: grammar map
    :param hex_chars: a lust of encoded characters (in the HEX representation)
    :return: grammar map with encoded characters
    """

    try:
        grammar['1 1 Char'].extend(hex_chars)
        return grammar
    except:
        print(ERROR_MESSAGE)
        return None

def prepare_cascaded_grammar(grammar, segmentation_path, n, in_prefix_nonterminal, in_suffix_nonterminal, out_prefix_nonterminal, out_suffix_nonterminal, concerntration_param_alphaa, concerntration_param_alphab):
    """
    This function seeds a grammar tree with prefixes and suffixes read from the output of some grammar.
    :param grammar: grammar map
    :param segmentation_path: PYAGS segmentation output path
    :param in_prefix_nonterminal: the prefix nonterminal to read from the output
    :param in_suffix_nonterminal: the suffix nonterminal to read from the output
    :param n: the number of most frequent affixes to extract and seed
    :param out_prefix_nonterminal: the prefix nonterminal to seed the prefixes into
    :param out_suffix_nonterminal: the suffix nonterminal to seed the suffixes into
    :param concerntration_param_alphaa: concentration parameter αA
    :param concerntration_param_alphab: concentration parameter αB
    :return: cascaded grammar map
    """

    try:
        _, prefixes, suffixes = get_top_affixes(segmentation_path, n, in_prefix_nonterminal, in_suffix_nonterminal)
        #Seed the grammar with the prefixes.
        if concerntration_param_alphaa == 0 and concerntration_param_alphab == 0:
            grammar[out_prefix_nonterminal].extend([convert_string_to_hex(prefix) for prefix in prefixes])
        else:
            grammar[str(concerntration_param_alphaa) + ' ' + str(concerntration_param_alphab) + ' ' + out_prefix_nonterminal].extend([convert_string_to_hex(prefix) for prefix in prefixes])
        #Seed the grammar with the suffixes.
        if concerntration_param_alphaa == 0 and concerntration_param_alphab == 0:
            grammar[out_suffix_nonterminal].extend([convert_string_to_hex(suffix) for suffix in suffixes])
        else:
            grammar[str(concerntration_param_alphaa) + ' ' + str(concerntration_param_alphab) + ' ' + out_suffix_nonterminal].extend([convert_string_to_hex(suffix) for suffix in suffixes])
        return grammar
    except:
        print(ERROR_MESSAGE)
        return None


def prepare_scholar_seeded_grammar(grammar, lk_path, out_prefix_nonterminal, out_suffix_nonterminal, concerntration_param_alphaa, concerntration_param_alphab):
    """
    This function seeds a grammar tree with prefixes and suffixes read from an LK file (LK stands for Loinguistic Knowledge).
    :param grammar: grammar map
    :param lk_path: linguistic-knowledge file path (see examples under data)
    :param out_prefix_nonterminal: the prefix nonterminal to seed the prefixes into
    :param out_suffix_nonterminal: the suffix nonterminal to seed the suffixes into
    :param concerntration_param_alphaa: concentration parameter αA
    :param concerntration_param_alphab: concentration parameter αB
    :return: scholar-seeded grammar map
    """

    try:
        #Read the prefixes and suffixes from the file.
        prefixes, suffixes = read_linguistic_knowledge(lk_path)
        #Seed the grammar with the prefixes.
        if concerntration_param_alphaa == 0 and concerntration_param_alphab == 0:
            grammar[out_prefix_nonterminal].extend([convert_string_to_hex(prefix) for prefix in prefixes])
        else:
            grammar[str(concerntration_param_alphaa) + ' ' + str(concerntration_param_alphab) + ' ' + out_prefix_nonterminal].extend([convert_string_to_hex(prefix) for prefix in prefixes])
        #Seed the grammar with the suffixes.
        if concerntration_param_alphaa == 0 and concerntration_param_alphab == 0:
            grammar[out_suffix_nonterminal].extend([convert_string_to_hex(suffix) for suffix in suffixes])
        else:
            grammar[str(concerntration_param_alphaa) + ' ' + str(concerntration_param_alphab) + ' ' + out_suffix_nonterminal].extend([convert_string_to_hex(suffix) for suffix in suffixes])
        return grammar
    except:
        print(ERROR_MESSAGE)
        return None


def read_linguistic_knowledge(lk_file):
    """
    This function reads the prefixes and suffixes in an LK file (LK stands for Linguistic Knowledge).
    :param lk_path: linguistic-knowledge file path (see examples under data)
    :return: lists of prefixes and suffixes o be seeded
    """

    try:
        prefixes = []
        suffixes = []
        read_prefixes = False
        read_suffixes = False
        #Loop over the lines in the file.
        with open(lk_file, 'r', encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                if len(line) == 0:
                    continue
                #Read prefixes.
                if line == LK_PREFIXES:
                    read_prefixes = True
                    read_suffixes = False
                #Read suffixes.
                elif line == LK_SUFFIXES:
                    read_prefixes = False
                    read_suffixes = True
                elif line.startswith('###'):
                    break
                else:
                    #Read a merker line.
                    if read_prefixes:
                        prefixes.append(line)
                    elif read_suffixes:
                        suffixes.append(line)
            return prefixes, suffixes
    except:
        print(ERROR_MESSAGE)
        return None, None


def get_top_affixes(segmentation_output_path, count, prefix_nonterminal, suffix_nonterminal):
    """
    This function generates top n affixes from a PYAGS segmentation output
    :param segmentation_output_path: PYAGS segmentation output path
    :param count: an integer indicating how many of the top affixes to return.
    :param prefix_nonterminal: the prefix nonterminal to read
    :param suffix_nonterminal: the suffix nonterminal to read
    :return: top n affixes, all prefixes, and all suffixes
    """

    try:
        prefix_counter = defaultdict(int)
        suffix_counter = defaultdict(int)
        with open(segmentation_output_path, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                #Search for a nonterminal match with a morph RegEx given as input.
                morphs, _, _ = get_morphs_from_tree(line, [prefix_nonterminal, suffix_nonterminal])
                #Separate into respective affix counter.
                for nonterminal in morphs:
                    for morph in  morphs[nonterminal]:
                        is_prefix = (nonterminal == prefix_nonterminal)
                        if is_prefix:
                            prefix_counter[morph] += 1
                        else:
                            suffix_counter[morph] += 1

        #Return top n affixes.
        #Sort prefixes.
        prefix_list_sorted = sorted(prefix_counter.items(), key=lambda x: x[1], reverse=True)
        suffix_list_sorted = sorted(suffix_counter.items(), key=lambda x: x[1], reverse=True)

        n_affixes = []
        p = 0  #index for prefix_list_sorted
        s = 0  #index for suffix_list_sorted

        #Final list of x prefixes and y suffixes such that x+y=n.
        prefix_x = []
        suffix_y = []

        #If prefix and suffix lists were empty, return empty lists.
        if len(prefix_list_sorted) == len(suffix_list_sorted) == 0:
            return n_affixes, prefix_x, suffix_y

        #Get top affixes.
        total_count = len(prefix_list_sorted) + len(suffix_list_sorted)
        if count > total_count:
            count = total_count
        while count > 0:
            if p == len(prefix_list_sorted) and s == len(suffix_list_sorted):
                break
            if len(prefix_list_sorted) > 0 and (len(suffix_list_sorted) == 0 or s == len(suffix_list_sorted) or prefix_list_sorted[p][1] > suffix_list_sorted[s][1]):
                n_affixes.append(prefix_list_sorted[p][0])
                prefix_x.append(prefix_list_sorted[p][0])
                p += 1
            else:
                n_affixes.append(suffix_list_sorted[s][0])
                suffix_y.append(suffix_list_sorted[s][0])
                s += 1
            count -= 1
        return n_affixes, prefix_x, suffix_y
    except:
        print(ERROR_MESSAGE)
        return None, None, None
