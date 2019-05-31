import numpy as np

class morphalyzer:
    
    def __init__(self, lemma, inflection):
        
        """Initialize the morphalyzer object with lemma and inflection"""
        
        self.lemma_prstsu = {"pr":"","st":"","su":""}
        self.inflection_prstsu = {"pr":"","st":"","su":""}
        
        self._lemma = lemma
        self._inflection = inflection
        
        self._lemma_len = len(lemma)
        self._inflection_len = len(inflection)
        
        self._d = None
        
        self._aligned = False
        
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
        
    def split_words(self):
        
        """Split words if words have been aligned"""
        
        if(not self._aligned):
            self.align_words()
        
        # Prefix for each word is beginning till first match
        alignlen = len(self._lemma_align)
                
        # Till match is found
        first_match = None
        second_match = None
        
        # forward pass through both the strings
        for i in range(alignlen):
            if(self._lemma_align[i] == self._inflection_align[i]):
                if(first_match is None):
                    first_match = i
                else:
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
        
        