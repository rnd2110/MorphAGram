import re
from collections import defaultdict

from constants import *

def convert_string_to_hex(string):
    """
    This function converts a regular string into its HEX representation.
    :param string: regular string
    :return: HEX representation
    """

    try:
        hex_chars = []
        for char in list(string):
            hex_char = char.encode('utf-16').hex()
            hex_chars.append(hex_char)
        return ' '.join(hex_chars)
    except:
        print(ERROR_MESSAGE)
        return None


def convert_hex_to_string(hex):
    """
    This function converts a HEX string into its regular representation.
    :param hex: HEX string
    :return: regular representation
    """

    try:
        string = bytes.fromhex(hex).decode('utf-16')
        # Remove trailing new line character if necessary.
        if list(string)[0] == '\x00':
            return str(list(string)[1])
        else:
            return string
    except:
        print(ERROR_MESSAGE)
        return None


def sort_unique(sequence):
    """
    This function sorts a list and removes duplicates.
    :param sequence: a list
    :return: sorted and unique elements
    """
    try:
        sequence.sort()
        seen = set()
        return [x for x in sequence if not (x in seen or seen.add(x))]
    except:
        print(ERROR_MESSAGE)
        return None

def to_lower_case(text, language):
    """
    This function converts a given text into its lowercased form, with special handling for Turkish.
    :param text: the text to lowercase
    :param language: the language of the processed text (or None)
    :return: lowercased text
    """

    if language and (language.lower() == "turkish" or language.upper() == "TUR"):
        text = text.replace('I', 'ı')
        text = text.replace('İ', 'i')
    text = text.lower()
    return text

def to_upper_case(text, language):
    """
    This function converts a given text into its uppercased form, with special handling for Turkish.
    :param text: the text to uppercase
    :param language: the language of the processed text (or None)
    :return: uppercased text
    """

    if language and (language.lower() == "turkish" or language.upper() == "TUR"):
        text = text.replace('ı', 'I')
        text = text.replace('i', 'İ')
    text = text.upper()
    return text

def get_morphs_from_tree(tree, nonterminals):
    """
    This function gets the different nonterminals from a morphological parse tree.
    :param tree :a line in the segmentation output
    Example: "(Word (Prefix#110 ^^^ (Chars (Char fffe6200) (Chars (Char fffe6500))))
    (Stem#52 (Chars (Char fffe6300) (Chars (Char fffe6f00) (Chars (Char fffe6d00)))))
    (Suffix#1109 (Chars (Char fffe6500) (Chars (Char fffe7300))) $$$))
    :param nonterminals: nonterminals to patse
    :return: a map of nonterminals and their terminal values (characters), an index-based
    dictionary dictionary of segmentation nonterminals and an index-based dictionary of
    segmentation-tokens
    """

    try:
        morphs = defaultdict(list)
        parts = tree.split()
        tokens = {}
        extracted_nonterminals = {}
        # Loop over each nonterminal.
        for nonterminal in set(nonterminals):
            read = False
            count = 0
            current_chars = []
            # Read the components of the current tree.
            for index, part in enumerate(parts):
                if not read and re.match('^\(?' + nonterminal + '(#[0-9]+)?$', part):
                    read = True
                # Read the characters.
                elif read and re.match('^([a-f\d]{4,8})\)*$', part):
                    hex_str = part.replace(')', '')
                    current_chars.append(convert_hex_to_string(hex_str))
                if read:
                    # Keeo track of the parentheses.
                    count += part.count('(')
                    count -= part.count(')')
                    if count <= 0:
                        # Detect the current morph.
                        if len(current_chars) > 0:
                            morph = ''.join(current_chars)
                            morphs[nonterminal].append(morph)
                            extracted_nonterminals[index] = nonterminal
                            tokens[index] = morph
                        read = False
                        count = 0
                        current_chars = []
        return morphs, extracted_nonterminals, tokens
    except:
        print(ERROR_MESSAGE)
        return None, None, None

def is_new_sentence(previous_word):
    """
    This function runs heuristics to detect if a token starts a new sentence.
    :param previous_word: the previous word to the underlying token
    :return: True (new sentence) or False (not a new sentence0
    """
    return not previous_word or re.match('^[\"\“\”\'\‘\’\`\′\՛\·\.\ㆍ\•\?\？\!\؟\。\፨\።\፧\—\‥\…]+$', previous_word)


