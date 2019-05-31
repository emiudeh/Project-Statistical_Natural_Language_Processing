import sys

from word_alignment import morphalyzer
from misc_functs import *
import random


cmdargs = sys.argv

# Parse input argments
nargs = len(cmdargs)

# Runtime parameters
train_filename = None
test_filename = None
print_acc = False
print_inf = False

# The first argumnet is always filename
# So, we start with the 2nd one
if(nargs == 1):
    # print("No arguments specified")
    sys.exit(1)

i = 1

while(i < nargs):
    
    try:
        cur_arg = cmdargs[i]
    except IndexError:
        sys.exit(1)
    
    # If first argument is -g, show info and exit
    if(cmdargs[i] == "-g"):
        print("Group L13: Old Saxon")
        print("Ishwar Mudraje, 2572866")
        print("Chukwuemeka Udeh, 2572822")
        print("Kaleem Ullah, 2568967")
        sys.exit(0)

    # Training input file    
    elif(cmdargs[i] == "-tr"):
        try:
            train_filename = cmdargs[i+1]
            i += 2
        except IndexError:
            sys.exit(2)
    
    # Test input file
    elif(cmdargs[i] == "-te"):
        try:
            test_filename = cmdargs[i+1]
            i += 2
        except IndexError:
            sys.exit(2)
    
    # Print accuracy
    elif(cmdargs[i] == "-a"):
        print_acc = True
        i+=1
    
    # Print the output line-by-line
    elif(cmdargs[i] == "-l"):
        print_inf = True
        i+=1
        
    else:
        sys.exit(1)

if((train_filename is None) or (test_filename is None)):
    # print("No files specified for training and testing")
    sys.exit(3)

if(not(print_acc or print_inf)):
    # print("No -a or -l specified")
    sys.exit(4)
    
    
# Function to check if a verb is strong or weak
def is_strong(word):
    if(word[-3:] == "ian"):
        return [False, word[:-3], "ian"]
    elif (word[-2:] == "on"):
        return [False, word[:-2], "on"]
    else:
        return [True, word[:-2], "an"]


def stem_declension(lemma, inflection, rule):
    
    """The rule for stem declension is to change the vowel in between"""
    
    lemma_type = None
            
    class_rules = {"I":["ī"],
                  "II":["io", "ū"],
                  "III":["e", "i"],
                  "IV":["e"],
                  "V":["e"],
                  "VI":["a"],
                  "VII":["ō", "ā", "ē", "a"]}
    
    # Stem declension rule set    
    stem_rules = {"I":{"p1":["ē"],
                       "p2":["i"],
                       "pt":["i"]},
                  "II":{"p1":["ō"],
                        "p2":["u"],
                        "pt":["o"]},
                  "III":{"p1":["a"],
                         "p2":["u"],
                         "pt":["o","u"]},
                  "IV":{"p1":["a"],
                        "p2":["ā"],
                        "pt":["o"]},
                  "V":{"p1":["a"],
                       "p2":["ā"],
                       "pt":["e"]},
                  "VI":{"p1":["ō"],
                       "p2":["ō"],
                       "pt":["a"]},
                  "VII":{"p1":["ē","io"],
                       "p2":["ē","io"],
                       "pt":[""]}}
    
    mm = osm(lemma, inflection)
    mm.split_words()
        
    if(rule.find("PST") >= 0):
        # First and third person are classified as first preterite
        # Second preterite is used for second person tenses
        # Past Participle has a separate rule
        if((rule.find("1") >= 0) or (rule.find("3") >= 0)):
            # 1st preterite
            lemma_type = "p1"
        elif(rule.find("2") >= 0):
            # 2nd preterite
            lemma_type = "p2"
        elif(rule.find("PTCP") >= 0):
            # Past participle
            lemma_type = "pt"
        
        if(lemma_type is not None):
            verb_class, stem_part = mm.verb_class() 
            
            for chrs in class_rules[verb_class]:
                stem_mod  = stem_part.replace(chrs, stem_rules[verb_class][lemma_type][0])
            
            mm.inflection_prstsu["st"] = mm.inflection_prstsu["st"].replace(stem_part,stem_mod)
            inflection = mm.inflection_prstsu["pr"] + mm.inflection_prstsu["st"] + mm.inflection_prstsu["su"]
            inflection = inflection.replace("_","")
        
    return(inflection)

def parse_rules(word1,word2):
    
    """Start from the end and define rules from them"""
    
    rules = {}
    
    i = len(word1)-1
    
    while(i >= 0):
        word_suf1 = word1[i:]
        word_suf2 = word2[i:]
        word_suf1 = word_suf1.replace("_","")
        word_suf2 = word_suf2.replace("_","")
        rules[word_suf1] = word_suf2
        i -= 1
        
    return rules


# Read and prepare list of training inputs
f = open(train_filename)
train = f.readlines()
f.close()

train = [tr.replace('\n','') for tr in train]
train = [tr.split() for tr in train]

# Read and prepare list of testing inputs
f = open(test_filename)
test = f.readlines()
f.close()

test = [te.replace('\n','') for te in test]
test = [te.split() for te in test]


# Create a dictionary of inflection descriptions
# One each for verb and nouns
# Dictionary to store prefix and suffix rules
suffix_rules = {"strong":{}, "weak":{}}

na_inf_rules = get_noun_transformation_dicts(train)[0]

for tr in train:
    
    word = tr[0]
    inf = tr[1]
    rule = tr[2]
    
    # Do for only verbs
    if(rule[0] == "V"):
        strong, word_stem, word_suf = is_strong(word)
        #word_stem_norm = normalize_vowel(word_stem)
        #inf_norm = normalize_vowel(inf)
        if(strong):
            wtype = "strong"
        else:
            wtype = "weak"
            
        # Extract the stem of the inflected word
        inf_stem = inf[0:len(word_stem)]
        # Rest is the suffix
        try:
            inf_suf = inf[len(word_stem):]
        except IndexError:
            inf_suf = ""
        # Add this rule if not already exists
        if(rule not in suffix_rules[wtype].keys()):
            suffix_rules[wtype][rule] = {}
        suffix_rules[wtype][rule][word_suf] = inf_suf
    
acc = 0
cnt = 0

# Decide the number of columns
ncol = len(test[0])
for te in test:
    
    # Decide if input in 3 or 2 column format
    if(ncol == 2):
        target_col = 1
    else:
        target_col = 1
        inf_rule_col = 2
    
    word = te[0]
    inf = te[1]
    # rule = te[2]

    # For only verbs
    if(word[-2:] == "an" or word[-2:] == "on" or word[-3:] == "ian"):
        strong, word_stem, word_suf = is_strong(word)
        if(strong):
            wtype = "strong"
        else:
            wtype = "weak"

        inf_suf = inf[len(word_stem):len(inf)]
        
        chosen_rule = random.sample(suffix_rules[wtype].keys(), 1)[0]

        for key in suffix_rules[wtype]:
            if word_suf in suffix_rules[wtype][key] and suffix_rules[wtype][key][word_suf] == inf_suf:
                chosen_rule = key
                break

        if chosen_rule.find("3") != -1:
            chosen_rule.replace('3', '1')

        # Print the inflected word if specfied as command line parameter
        if(print_inf):
            print(chosen_rule)

        # Calculate accuracy anyway
        if(ncol == 3):
            if(chosen_rule == te[inf_rule_col]):
                acc += 1
        else:
            if(print_acc):
                sys.exit(4)


    else:

        i = 0
        while(i < len(word) and (i < len(inf))):
            word_suf = word[i:]
            inf_suf = inf[i:]
            if word_suf in na_inf_rules:
                chosen_rule = random.sample(na_inf_rules[word_suf].keys(), 1)[0]
                for rule in na_inf_rules[word_suf]:
                    if na_inf_rules[word_suf][rule] == inf_suf:
                        chosen_rule = rule
                        break
            else:
                word_sufs = [ky for ky in na_inf_rules.keys()]
                suf = random.sample(word_sufs,1)[0]
                chosen_rule = random.sample(na_inf_rules[suf].keys(), 1)[0]
            i += 1

        # Print the inflected word if specfied as command line parameter
        if(print_inf):
            print(chosen_rule)

        if(ncol == 3):
            if(chosen_rule == te[inf_rule_col]):
                acc += 1
        else:
            if(print_acc):
                sys.exit(4)

if(print_inf):
    print("")

# Print accuracy if input parameter is specified

if(ncol == 3):
    if(print_acc):
        print("trained on: %s" %train_filename)
        print(" - training instances: %d" %len(train))
        print("tested on: %s" %test_filename)
        print(" - testing instances: %d" %len(test))
        print(" - correct instances: %d" %acc)
        print(" - accuracy: %s" %('{:.3%}'.format(acc/len(test))))
