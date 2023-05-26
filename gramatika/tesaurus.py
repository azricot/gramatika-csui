
from Levenshtein import distance

import json
import sys


class Tesaurus():

    def __init__(self, sinonim_file):
        self.sinonim_file = sinonim_file
        self.__sinonim_dict = None

    def get_sinonim_dict(self):
        
        if self.__sinonim_dict is None:
            # initialize sinonim_dict if is None
            filename = "tesaurus/sinonim.json" if self.sinonim_file is None else self.sinonim_file

            with open(filename) as sinonim_file:
                sinonim_data = json.load(sinonim_file)	

            self.__sinonim_dict = sinonim_data

        return self.__sinonim_dict
    
    def get_sinonim(self, word):
        sinonim_dict = self.get_sinonim_dict()

        if word in sinonim_dict.keys():
            return sinonim_dict[word]['sinonim']
        
        return []
    
    def get_most_similar(self, word):
        most_similar = sys.maxsize
        string_similar = ""
        sinonim_dict = self.get_sinonim_dict()

        for key in sinonim_dict.keys():

            similarity = distance(word, key)
            
            if similarity < most_similar :
                most_similar = similarity
                string_similar = key
                
        return string_similar