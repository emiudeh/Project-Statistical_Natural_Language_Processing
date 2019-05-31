import sys

from word_alignment import morphalyzer

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


def apply_rule(lemma, suffix_rules, prefix_rules):
    
    """Apply rules on word based on the partial to suffix"""
    
    new_suffix = ""
    
    for i in range(0, len(lemma)):
        if lemma[i:len(lemma)] in suffix_rules.keys():
            new_suffix = suffix_rules[lemma[i:len(lemma)]]
            # replaces lemma suffix with inflected suffix
            break
    
    inflected = lemma[0:i] + new_suffix
    

    # get the new prefix
    new_prefix = ""
    
    for i in reversed(range(0, len(lemma))):
        if lemma[0:i] in prefix_rules.keys():
            new_prefix = prefix_rules[lemma[0:i]]
            # replaces lemma prefix with inflected prefix
            break
    
    inflected = new_prefix + inflected[i:len(inflected)]
    
    return inflected


# Read and prepare list of training inputs
f = open(train_filename)
train = f.readlines()
f.close()

train = [tr.replace('\n','') for tr in train]
train = [tr.split() for tr in train]

# Create a dictionary of inflection descriptions
inflection_rules = {}

# Learn inflection rules (NLTK style suffix and prefix rules)
for tr in train:
    mm = morphalyzer(tr[0],tr[1])
    mm.split_words()
    split_lemma = mm.lemma_prstsu
    split_inflection = mm.inflection_prstsu

    if tr[2] not in inflection_rules.keys():
        inflection_rules[tr[2]] = {"suffix":{}, "prefix":{}}

    # Compare lemma st+su and inflection st+su and learn all possible rules
    suffix_rule_list = parse_rules(split_lemma["st"] + split_lemma["su"], split_inflection["st"] + split_inflection["su"])
    for rule in suffix_rule_list:
        if(rule not in inflection_rules[tr[2]]["suffix"].keys()):
            inflection_rules[tr[2]]["suffix"][rule] = suffix_rule_list[rule]
    
    prefix_rule_list = parse_rules(split_lemma["pr"], split_inflection["pr"])
    for rule in prefix_rule_list:
        if(rule not in inflection_rules[tr[2]]["prefix"].keys()):
            inflection_rules[tr[2]]["prefix"][rule] = prefix_rule_list[rule]
    
        
# Apply the rules on new lemmas
# Read and prepare list of testing inputs
f = open(test_filename)
test = f.readlines()
f.close()

test = [te.replace('\n','') for te in test]
test = [te.split() for te in test]

# Decide the number of columns
ncol = len(test[0])

# Calculate accuracy
acc = 0

for te in test:
     
    # Decide if input in 3 or 2 column format
    if(ncol == 2):
        inf_rule_col = 1
    else:
        target_col = 1
        inf_rule_col = 2
    
    # Word and rules
    word = te[0]
    
    try:
        suffix_rules = inflection_rules[te[inf_rule_col]]["suffix"]
    except KeyError:
        suffix_rules = {}
    
    try:
        prefix_rules = inflection_rules[te[inf_rule_col]]["prefix"]
    except KeyError:
        prefix_rules = {}

    # Replace words based on learnt rules
    replacement = None
    
    # inflected_word = apply_suffix_rule(word, suffix_rules)
    inflected_word = apply_rule(word, suffix_rules, prefix_rules)
    
    # Print the inflected word if specfied as command line parameter
    if(print_inf):
        print(inflected_word)
    
    # Calculate accuracy anyway
    if(ncol == 3):
        if(inflected_word == te[target_col]):
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