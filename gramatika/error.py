
from abc import ABC, abstractmethod

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
        pass



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

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class PunctuationError(Error):

    error_type_id = "PUNCT"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


class SpellingError(Error):

    error_type_id = "SPELL"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        pass


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