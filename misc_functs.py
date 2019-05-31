import collections

# File with miscellaneous functions used to handle nouns in task2.py

# Ignore umlauted characters
def umlauted(char1, char2):
    same = {'ā': 'a', 'ō': 'o', 'ē': 'e', 'ī': 'i', 'ū': 'u'}
    if char1 in same and same[char1] == char2:
        return True
    if char2 in same and same[char2] == char1:
        return True
    return False

# Get the stem by simply getting least common substring
def get_stem(str1, str2):
    lcs = ""
    longest_temp = ""
    for i in range(0, len(str1)):
        for j in range(0, len(str2)):
            # Ignore umluat changes 
            if str1[i] == str2[j] or umlauted(str1[i], str2[j]):
                (i_temp, j_temp) = (i, j)
                # Find longest possible match between strings
                while i_temp < len(str1) and j_temp < len(str2) and (str1[i_temp] == str2[j_temp] or umlauted(str1[i_temp], str2[j_temp])):
                    longest_temp += str1[i_temp]
                    i_temp += 1
                    j_temp += 1
            lcs = longest_temp if len(longest_temp) > len(lcs) else lcs
            longest_temp = ""
    return lcs


# Use the least common substring algorithm to split words
# into nouns and verbs
def get_word_parts(lemma, inflected):

    lem_st = get_stem(lemma.lower(), inflected.lower())
    temp = lemma.lower()
    pre_cnt = temp.find(lem_st)
    # end block -----

    inf_st = get_stem(inflected.lower(), lemma.lower())
    inf_pre_cnt = inflected.lower().find(inf_st)
    suf_index = len(lem_st)
    return [pre_cnt, suf_index, inf_pre_cnt]


# creates prefix and suffix dictionaries
# for all nouns
def get_noun_transformation_dicts(list_arg):
    suf_dict = collections.defaultdict(dict)
    pre_dict = collections.defaultdict(dict)

    for entry in list_arg:
        (lemma, inflected, inflection) = tuple(entry)
        (pre_cnt, suf_index, inf_pre_cnt) = tuple(get_word_parts(lemma, inflected))
        # populate the suffix dictionary
        i = pre_cnt+suf_index
        y = inf_pre_cnt + suf_index
        while i >= pre_cnt:
            if not inflection in suf_dict[lemma[i:len(lemma)]]:
                suf_dict[lemma[i:len(lemma)]][inflection] = inflected[y:len(inflected)]
            i -= 1
            y -= 1
        # populate the prefix dictionary
        pre_dict[lemma[0:pre_cnt]][inflection] = inflected[0:inf_pre_cnt]
    return[suf_dict, pre_dict]


def inflect_noun(noun_entry, suffix_dict):

    lemma = noun_entry[0]
    inflected = noun_entry[0]
    inflection = noun_entry[2]

    # get the new suffix
    for i in range(0, len(lemma)):
        if lemma[i:len(lemma)] in suffix_dict:
            if inflection in suffix_dict[lemma[i:len(lemma)]]:
                new_suffix = suffix_dict[lemma[i:len(lemma)]][inflection]
                # replaces lemma suffix with inflected suffix
                inflected = lemma[0:i] + new_suffix
            continue

    return inflected


def a_pre_change(verb):
    verb = list(verb)
    vowels = ["a", "e", "i", "o", "u", "io", "ā", "ē", "ī", "ō", "ū"]
    if verb[0] == "a" and verb[2] in vowels:
        verb[0] = "ā"
    return "".join(verb)


