import numpy as np

class osx_morphalyzer:
    
    """An inherited morphalyzer class for Old Saxon (OSX). 
    Additionally Checks if a verb is strong or weak"""
    
    def __init__(self, lemma, inflection, lemma_type = None):
        
        # Inheriting the morphalyzer init class
        """Initialize the morphalyzer object with lemma and inflection"""
        
        self.lemma_prstsu = {"pr":"","st":"","su":""}
        self.inflection_prstsu = {"pr":"","st":"","su":""}
        
        self._lemma = lemma
        self._inflection = inflection
        
        self._lemma_type = None
        if(lemma_type is not None):
            if(lemma_type not in ["V","N","A"]):
                raise ValueError("Not the right type of word")
            else:
                self._lemma_type = lemma_type
                
                
        self._lemma_type = lemma_type
        
        self._lemma_len = len(lemma)
        self._inflection_len = len(inflection)
        
        self._d = None
        
        self._aligned = False
        
        self._strong_weak = None
        
        self._class = None
        self._stem_type = ""
                
        # Check if this is a strong or weak verb
        if((self._lemma[-3:] == "ian") or (self._lemma[-2:] == "on")):
            self._strong_weak = "weak"
        elif(self._lemma[-2:] == "an"):
            self._strong_weak = "strong"
            
    
    def levenshtein_distance(self):
        
        """Calculate the levenshtein distances between 2 words"""
        
        # Levenshtein matrix
        self._d = np.zeros([self._inflection_len+1, self._lemma_len+1], np.int)
        
        # Source prefixes can be transformed into empty by dropping all characters
        # Ditto for target prefixes
        self._d[0,:] = np.arange(0, self._lemma_len+1)
        self._d[:,0] = np.arange(0, self._inflection_len+1)
        
        
        # Fill up the cost matrix
        for j in range(1,self._inflection_len+1):
            for i in range(1,self._lemma_len+1):
                if(self._lemma[i-1] == self._inflection[j-1]):
                    substitution_cost = 0
                else:
                    substitution_cost = 1
                self._d[j,i] = np.min([self._d[j-1,i]+1, 
                                     self._d[j,i-1]+1, 
                                     self._d[j-1,i-1] + substitution_cost])
    
    def align_words(self):
        
        """Align words form the levenshtein matrix"""
        
        if(self._d is None):
            self.levenshtein_distance()

        self._lemma_align = []
        self._inflection_align = []
        
        # Backward trace through the matrix to find the alignment scheme        
        i = self._lemma_len
        j = self._inflection_len
        
        while((i > 0) or (j > 0)):    
            if(self._lemma[i-1] == self._inflection[j-1]):
                dij = self._d[j-1][i-1]
            else:
                dij = self._d[j-1][i-1] + 1
        
            if(self._d[j][i] == dij):
                i -= 1
                j -= 1
                self._lemma_align.append(self._lemma[i])
                self._inflection_align.append(self._inflection[j])
                
            elif(self._d[j][i] == (1+self._d[j-1][i])):
                self._lemma_align.append("_")
                j -= 1
                self._inflection_align.append(self._inflection[j])
                
            elif(self._d[j][i] == (1+self._d[j][i-1])):
                i -= 1
                self._lemma_align.append(self._lemma[i])
                self._inflection_align.append("_")
                
        self._lemma_align = ''.join(self._lemma_align)[::-1]
        self._inflection_align = ''.join(self._inflection_align)[::-1]               
    
        self._aligned = True
    
    
    def is_strong(self):
        if(self._strong_weak is not None):
            if(self._strong_weak == "strong"):
                return True
            else:
                return False

        return False
    
    def is_weak(self):
        if(self._strong_weak is not None):
            if(self._strong_weak == "weak"):
                return True
            else:
                return False

        return False
    
    def split_words(self):
        
        """Split words if words have been aligned"""
        
        if(not self._aligned):
            self.align_words()
        
        # Prefix for each word is beginning till first match
        alignlen = len(self._lemma_align)
        
        # Till match is found
        first_match = None
        second_match = None
        
        
        # Handle verbs differently from nouns and adjectives
        # For verbs suffix is always on or an or ian
        if(self._lemma_type is not None):
            
            # If verb, the suffix is either ian, on or an
            if(self._lemma_type == "V"):
                
                if(self.is_strong()):
                    for i in range(1, len(self._lemma_align)+1):
                        if(self._lemma_align[-i:].replace("_","") == "an"):
                            second_match = -i-1
                            break
                        
                else:
                    for i in range(1, len(self._lemma_align)+1):
                        if((self._lemma_align[-i:].replace("_","") == "on") or 
                           (self._lemma_align[-i:].replace("_","") == "ian")):
                            second_match = -i-1
                            break
        
        # forward pass through both the strings
        for i in range(alignlen):
            if(self._lemma_align[i] == self._inflection_align[i]):
                if(first_match is None):
                    first_match = i
                else:
                    if(second_match is None):
                        second_match = i
                   
        if(first_match is not None):
        
            if(first_match > 0):
                self.lemma_prstsu["pr"] = self._lemma_align[:first_match]
            else:
                self.lemma_prstsu["pr"] = "_"
            
            if(second_match is not None):
                self.lemma_prstsu["st"] = self._lemma_align[first_match:(second_match+1)]
                self.lemma_prstsu["su"] = self._lemma_align[(second_match+1):]
            else:
                self.lemma_prstsu["st"] = self._lemma_align[first_match:]
                self.lemma_prstsu["su"] = "_"
            
            
            if(first_match > 0):
                self.inflection_prstsu["pr"] = self._inflection_align[:first_match]
            else:
                self.inflection_prstsu["pr"] = "_"
            
            if(second_match is not None):
                self.inflection_prstsu["st"] = self._inflection_align[first_match:(second_match+1)]
                self.inflection_prstsu["su"] = self._inflection_align[(second_match+1):]
            else:
                self.inflection_prstsu["st"] = self._inflection_align[first_match:]
                self.inflection_prstsu["su"] = "_"
        
        else:
            self.lemma_prstsu["st"] = self._lemma_align
            self.inflection_prstsu["st"] = self._inflection_align
    
    
    
    def verb_class(self):
        
        # Classification rules for stem        
        consonants = "bcdfghjklmnpqrstvwxyz" 
        
        stem_rules = {"I":[["ī" + c for c in consonants]],
                      "II":[["io" + c for c in consonants],
                            ["ū" + c for c in consonants]],
                      "III":[["e" + c1 + c2 for c1 in consonants for c2 in consonants],
                             ["i" + c for c in consonants]],
                      "IV":[["er","el","brekan"]],
                      "V":[["e" + c for c in consonants if c not in ["r","l"]]],
                      "VI":[["a" + c for c in consonants]],
                      "VII":[["ō" + c1 + c2 for c1 in consonants for c2 in consonants],
                             ["ā" + c1 + c2 for c1 in consonants for c2 in consonants], 
                             ["ē" + c1 + c2 for c1 in consonants for c2 in consonants],
                             ["a" + c1 + c2 for c1 in consonants for c2 in consonants]]
                        }
        
        key = "VII"
        if(self.is_strong()):
            
            if(not self._aligned):
                self.split_words()
            
            for key in stem_rules.keys():
                if(self._stem_type == ""):
                    for st_part in stem_rules[key]:
                        if(self._stem_type == ""):
                            for part in st_part:
                                if(self.lemma_prstsu["st"].find(part) >= 0):
                                    self._class = key
                                    self._stem_type = part
                                    break
            
        return([key, self._stem_type])