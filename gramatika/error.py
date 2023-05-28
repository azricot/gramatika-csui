
from abc import ABC, abstractmethod

import string
import random


class Error(ABC):
    error_type: str
    max_ratio: float

    def __init__(self, token, sentence):
        super().__init__()
        self.token = token
        self.sentence = sentence

        self.error_type = ""
        self.original_token_list = []
        self.error_token_list = []
        self.related_token_id = []

        self.generate_error()

    @abstractmethod
    def generate_error(self):
        pass

    def is_valid(self):
        return self.error_type and len(self.original_token_list) and len(self.error_token_list)
    
    def get_original_form(self):
        return " ".join([token.form for token in self.original_token_list])
    
    def get_error_form(self):
        return " ".join([error_form for error_form in self.error_token_list if error_form != ""])
    
    def get_len_error_token_list(self):
        return len([error for error in self.error_token_list if error != ""])
    
    def get_len_original_token_list(self):
        return len([original for original in self.original_token_list if original != ""])
    
    def get_edit_offset(self):
        # edit offset = length of error - length of original
        return self.get_len_error_token_list() - self.get_len_original_token_list()

    def get_ratio(self):
        dataset = self.sentence.dataset
        total_error_on_dataset = dataset.get_total_error()

        if total_error_on_dataset > 0:
            return dataset.error_dict[self.error_type_id]["count"] / total_error_on_dataset
        else:
            return 0
        
    def is_below_max_ratio(self):
        return self.get_ratio() < self.max_ratio


class AdjectiveError(Error):

    error_type_id = "ADJ"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        sinonims = sentence.dataset.get_sinonim(token.form)

        if token.upos == 'ADJ' and len(sinonims) > 0:
            self.original_token_list = [token]
            self.error_token_list = random.choice(sinonims).split(" ")

            self.error_type = "|||R:ADJ|||"
            self.related_token_id = [token.id]


class AdverbError(Error):

    error_type_id = "ADV"
    max_ratio = 0.1

    adp_for_Adverb = ['secara', 'dengan']

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        token_id_after = token.id + 1
        token_after = None
        if sentence.does_token_id_exists(token_id_after):
            token_after = sentence.get_token_by_id(token_id_after)

        sinonims = sentence.dataset.get_sinonim(token.form)

        if token.upos == 'ADV' and len(sinonims) > 0:
            self.original_token_list = [token]
            self.error_token_list = random.choice(sinonims).split(" ")

            self.error_type = "|||R:ADV|||"

        elif token.upos == 'ADP' and token_after is not None and token_after.upos == 'ADJ' and token.form.lower() in self.adp_for_Adverb:
            self.original_token_list = [token] # Error is deleting, so original token doubled
            self.error_token_list = [""]

            self.error_type = "|||M:ADV|||"

        # Either way (of if condition), token_after will be considered related
        if token_after:
            self.related_token_id = [token.id, token_after.id]
        else:
            self.related_token_id = [token.id]


class ConjunctionError(Error):

    error_type_id = "CONJ"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class DeterminerError(Error):

    error_type_id = "DET"
    max_ratio = 0.1

    penggolong_word_list = ['orang', 'ekor', 'buah', 'batang' , 'bentuk', 'bidang' , 'belah', 'helai', 'bilah', 'utas', 'potong', 'tangkai', 'butir', 'pucuk', 'carik', 'rumpun', 'keping', 'biji', 'kuntum', 'patah', 'laras', 'kerat']

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        if token.upos == 'DET' and token.lemma in self.penggolong_word_list:
            self.original_token_list = [token]
            self.error_token_list = [token.form.replace(token.lemma, random.choice([penggolong for penggolong in self.penggolong_word_list if penggolong != token.lemma]))]

            self.error_type = "|||R:DET|||"
            self.related_token_id = [token.id]

            # Token After will be added to related_token
            token_id_after = token.id + 1
            if sentence.does_token_id_exists(token_id_after):
                token_after = sentence.get_token_by_id(token_id_after)
                self.related_token_id = [token.id, token_after.id]
            else:
                self.related_token_id = [token.id]
                
            


class MorphologyError(Error):

    error_type_id = "MORPH"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class NounError(Error):

    error_type_id = "NOUN"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class NounInflectionError(Error):

    error_type_id = "NOUN:INFL"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
    
        token = self.token
        sentence = self.sentence
        
        if (token.upos=='NOUN' and (token.morf.count('peN+') == 1 or token.morf.count('pe+') == 1 or token.morf.count('per+') == 1) and not token.morf.count('+an') > 0):
            
            self.original_token_list = [token]
            self.error_token_list = [""]
        
            if token.form[:3].lower() == "per":
                self.error_token_list = "pe" + token.lemma
            else :
                self.error_token_list = "per" + token.lemma

            print("halo")
            self.error_type = "|||R:NOUN:INFL|||"
            self.related_token_id = [token.id]
        
        elif (token.upos == 'NOUN' and token.morf.count('peN+') == 1 and token.morf.count('+an') == 1):

            ubah_kata = ""
        
            if token.form[:3].lower() == "pem" or token.form[:3].lower() == "pen":
                ubah_kata = "pe" + token.lemma + "an"
            elif token.form[:3].lower() == "peng":
                ubah_kata = "pe" + token.lemma + "an"
            elif token.form[:3].lower() == "peny":
                ubah_kata = "pen" + token.lemma + "an"
        #else:
          #output = [0]
          #return output
            print("halo")
            self.original_token_list = [token]
            self.error_token_list = [ubah_kata]

            self.error_type = "|||R:NOUN:INFL|||"
            self.related_token_id = [token.id]





class OrthographyError(Error):
    
    error_type_id = "ORTH"
    max_ratio = 0.2

    orth_prefix_types = ["di", "ke", "ter", "ber", "per"]
    orth_suffix_types = ["nya", "lah", "pun", "kah"]
    orthography_types = orth_prefix_types + orth_suffix_types

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        # Whitespace is missing error
        if token.form.lower() in self.orthography_types:
            # Prefix
            if token.form.lower() in self.orth_prefix_types:
                token_id_after = token.id + 1

                if sentence.does_token_id_exists(token_id_after):
                    token_after = sentence.get_token_by_id(token_id_after)

                    self.original_token_list = [token, token_after]
                    self.error_token_list = [token.form + token_after.form]

                    self.error_type = "|||R:ORTH|||"
                    self.related_token_id = [token.id, token_after.id]

            elif token.form.lower() in self.orth_suffix_types:
                token_id_before = token.id - 1

                if sentence.does_token_id_exists(token_id_before):
                    token_before = sentence.get_token_by_id(token_id_before)

                    self.original_token_list = [token_before, token]
                    self.error_token_list = [token_before.form + token.form]

                    self.error_type = "|||R:ORTH|||"
                    self.related_token_id = [token_before.id, token.id]
        
        # Whitespace is unnecessary error
        else:

            for prefix in self.orthography_types:
                if token.morf[0].lower() == prefix.lower():

                    # case of ke-[numeric]
                    if token.form[:3] == "ke-" and token.form[3:].isdigit():
                        self.original_token_list = [token]
                        self.error_token_list = token.form.split("-")
                    elif not token.upos == "NOUN":
                        self.original_token_list = [token]
                        self.error_token_list = [token.form[:len(prefix)], token.form[len(prefix):]]
                    else:
                        continue

                    self.error_type = "|||R:ORTH|||"
                    self.related_token_id = [token.id]

                    break
                # Suffix
                elif token.morf[-1].lower() == prefix.lower():
                    self.original_token_list = [token]
                    self.error_token_list = [token.form[:-len(prefix)], token.form[-len(prefix):]]
                    
                    self.error_type = "|||R:ORTH|||"
                    self.related_token_id = [token.id]

                    break


class ParticleError(Error):

    error_type_id = "PART"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class PrepositionError(Error):

    error_type_id = "PREP"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class PronounError(Error):
    
    error_type_id = "PRON"
    max_ratio = 0.1
    
    persona_pronoun_errors = {
        "tunggal_pertama": [
                "saya", 
                "ku", 
                "aku"
                ]
        ,
        "tunggal_pertama_banyak_eksklusif": [
                "kami"
                ]
        ,
        "tunggal_pertama_banyak_inklusif":[
                "kita"
                ]
        ,
        "tunggal_kedua": [
                "engkau",
                "kamu",
                "anda",
                "dikau"
                ]
        ,
        "tunggal_kedua_jamak":[
                "kalian",
                "kamu sekalian",
                "anda sekalian",
                ]
        ,
        "tunggal_ketiga":[
                "ia",
                "dia",
                "beliau",
                ]
        ,
        "tunggal_kedua_jamak": [
                "mereka"
                ]
    }

    pronomina_penanya = ["siapa","apa","mana","mengapa","kenapa","kapan","di mana", "ke mana", "dari mana", "bagaimana",  "berapa" ]

    list_all_persona_pronoun = list(persona_pronoun_errors.values())
    list_all_persona_pronoun = [item for sublist in list_all_persona_pronoun for item in sublist]
    
    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        if (token.upos == 'PRON' and token.form in self.list_all_persona_pronoun):
            self.error_token_list = random.choice ([value for key, value in self.persona_pronoun_errors.items() if key not in self.list_blacklist_persona_pronoun(token.form)])[0].split(" ")
            self.original_token_list = [token]

            self.error_type = "|||R:PRON|||"
            self.related_token_id = [token.id]

        elif (token.upos == 'PRON' and token.form in self.pronomina_penanya):

            if token.form == "mengapa" or token.form == "kenapa" :
                tmp_pronomina_penanya = pronomina_penanya.copy()
                tmp_pronomina_penanya.pop(tmp_pronomina_penanya.index("mengapa"))
                tmp_pronomina_penanya.pop(tmp_pronomina_penanya.index("kenapa"))
                self.error_token_list = [token.form.replace(token.lemma, random.choice(tmp_pronomina_penanya)).split()]
            else:
                tmp_pronomina_penanya = self.pronomina_penanya.copy()
                tmp_pronomina_penanya.pop(tmp_pronomina_penanya.index(token.lemma))
                self.error_token_list = [random.choice(tmp_pronomina_penanya).split()]

            self.original_token_list = [token]

            self.error_type = "|||R:PRON|||"
            self.related_token_id = [token.id]
    
    def list_blacklist_persona_pronoun(self, kata):
        for key,value in self.persona_pronoun_errors.items():
            if kata in value:
                return [key]
        return []


class PunctuationError(Error):

    error_type_id = "PUNCT"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        
        token = self.token
        sentence = self.sentence
        ada_Anak_Kalimat = 0
        ada_Kalimat_tambahan = 0
        
        if token.deprel in {'advcl', 'obl'} :
            ada_Anak_Kalimat = 1
              
        if token.deprel in {'appos'} :
            ada_Kalimat_tambahan  = 1

        token_id_after = token.id + 1
        token_after = None
        if sentence.does_token_id_exists(token_id_after):
            token_after = sentence.get_token_by_id(token_id_after)

        if (token.upos == 'PUNCT'and token.lemma == "," and token_after != None  and token_after.upos=='CCONJ' and token_after.lemma in {"dan","atau","tetapi","melainkan","sedangkan"}):
            self.original_token_list = [token]
            self.error_token_list = [""]

            self.error_type = "|||M:PUNCT|||"
            self.related_token_id = [token.id]

        elif ((ada_Anak_Kalimat == 1 or ada_Kalimat_tambahan == 1) and token.lemma == ","  ): 
            self.original_token_list = [token]
            self.error_token_list = [""]

            self.error_type = "|||M:PUNCT|||"
            self.related_token_id = [token.id]
            
       


class SpellingError(Error):

    error_type_id = "SPELL"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence
        rand = random.randrange(1,4)
        apakah_akan_dilakukan = random.randrange(1,20)

        if apakah_akan_dilakukan == 1 and rand == 1 and token.form.isalpha() and len(token.form) > 3: ## Erase one char
        
            self.original_token_list = [token]
            index = random.randrange(0, len(token.form)-1)
            self.error_token_list = [token.form[:index] + token.form[index + 1: ]]

            self.error_type = "|||R:SPELL|||"
            self.related_token_id = [token.id]
      
        elif apakah_akan_dilakukan == 1 and rand == 2 and token.form.isalpha() and len(token.form) > 3: ## Add one char
            
            self.original_token_list = [token]
            noise_char = random.choice(string.ascii_lowercase)
            index = random.randrange(0, len(token.form)-1)
            self.error_token_list = [token.form[:index] + noise_char + token.form[index + 1: ]]

            self.error_type = "|||R:SPELL|||"
            self.related_token_id = [token.id]

        elif apakah_akan_dilakukan == 1 and rand == 3 and token.form.isalpha() and len(token.form) > 3: ## Tukar char sebelahnya
            
            self.original_token_list = [token]
            index = random.randrange(1, len(token.form)-2)
            self.error_token_list  = [token.form[:index] + token.form[index+1] + token.form[index]  + token.form[index + 2: ]]
            
            self.error_type = "|||R:SPELL|||"
            self.related_token_id = [token.id]

        elif apakah_akan_dilakukan == 1 and rand == 4 and token.form.isalpha() and len(token.form) > 3 and len(list(filter(lambda x: x in huruf_hidup, token.lemma))) > 0: ## Add one char
            
            self.original_token_list = [token]
            self.error_token_list = [re.sub("[aeiou]","",token.form)]

            self.error_type = "|||R:SPELL|||"
            self.related_token_id = [token.id]


class VerbError(Error):

    error_type_id = "VERB"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class VerbInflectionError(Error):

    error_type_id = "VERB:INFL"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class VerbTenseError(Error):

    error_type_id = "VERB:TENSE"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class WordOrderError(Error):

    error_type_id = "WO"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass