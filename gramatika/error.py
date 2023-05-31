
from abc import ABC, abstractmethod

import string
import random
import re


class Error(ABC):

    konsonan_luluh = ['k', 't', 's', 'p']
    huruf_hidup = ['a', 'i', 'u', 'e', 'o']

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
        # Is error valid or not (is error generated correctly)
        return self.error_type and len(self.original_token_list) and len(self.error_token_list)
    
    def get_original_form(self):
        # Get Original Token Form in String
        return " ".join([token.form for token in self.original_token_list])
    
    def get_error_form(self):
        # Get Error Form in String
        return " ".join([error_form for error_form in self.error_token_list if error_form != ""])
    
    def get_len_error_token_list(self):
        # Get length of error list (number of token)
        return len([error for error in self.error_token_list if error != ""])
    
    def get_len_original_token_list(self):
        # Get length of original token list (number of token)
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
            self.original_token_list = [token]
            self.error_token_list = [""]

            self.error_type = "|||M:ADV|||"

        # Either way (of if condition), token_after will be considered related
        if token_after:
            self.related_token_id = [token.id, token_after.id]
        else:
            self.related_token_id = [token.id]


class ConjunctionError(Error):

    list_conjunction_error_substitution = {
        # ---- CCONJ
        "dan" : ['atau', 'tetapi'],
        "atau" : ['dan', 'serta', 'tetapi'],
        "melainkan" : ['dan', 'atau', 'sedangkan', 'serta', 'tetapi'],
        "sedangkan" : ['dan', 'atau', 'melainkan', 'serta', 'tetapi'],
        "serta" : ['atau', 'melainkan', 'sedangkan', 'tetapi'],
        "tetapi" : ['dan', 'atau', 'melainkan', 'sedangkan', 'serta'],
        "padahal" : ['dan', 'atau', 'melainkan', 'sedangkan', 'serta', 'tetapi'],

        # ---- SCONJ

        # -- Conjunction concerned with time
        "sejak" : ["ketika", "selagi", "selama", "sewaktu", "setelah", "sebelum", "sesudah", "sehabis", "seusai", "hingga", "sampai"],
        "sedari" : ["ketika", "selagi", "selama", "sewaktu", "setelah", "sebelum", "sesudah", "sehabis", "seusai", "hingga", "sampai"],
        "semenjak" : ["ketika", "selagi", "selama", "sewaktu", "setelah", "sebelum", "sesudah", "sehabis", "seusai", "hingga", "sampai"],
        
        #"begitu" : [],
        #"demi" : [],
        "ketika" : ["sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga", "sampai"],
        "sambil" : ["ketika", "sejak", "sedari", "semenjak", "selagi", "selama", "sementara", "seraya", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga", "sampai"],
        "selagi" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selama", "sementara", "seraya", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga", "sampai"],
        "selama" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "sementara", "seraya", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga", "sampai"],
        "sementara" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "seraya", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga", "sampai"],
        "seraya" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga", "sampai"],
        "sewaktu" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga", "sampai"],
        "tatkala" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga", "sampai"],

        "setelah" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "hingga", "sampai"],
        "sebelum" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "hingga", "sampai"],
        "sehabis" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "hingga", "sampai"],
        #"selesai" : [],
        "sesudah" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "hingga", "sampai"],
        "seusai" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "sesudah", "hingga", "sampai"],

        "hingga" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "sampai"],
        "sampai" : ["ketika", "sejak", "sedari", "semenjak", "sambil", "selagi", "selama", "sementara", "seraya", "sewaktu", "setelah", "sebelum", "sehabis", "sesudah", "seusai", "hingga"],


        # -- The rest of conjunction
        #"asal" : [],
        "asalkan" : ["andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "apabila" : ["andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "jika" : ["andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "jikalau" : ["andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "kalau" : ["andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "manakala" : ["andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        
        "andaikan" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "seandainya" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "sekiranya" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "serumpamanya" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "andai kata" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        
        "agar" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "biar" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "supaya" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],

        "biarpun" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "kendati" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "kendatipun" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "meski" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "meskipun" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "sekalipun" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "sungguhpun" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "walau" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "walaupun" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        
        "alih-alih" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "daripada" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        #"ibarat" : [],
        "laksana" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "seakan-akan" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "sebagai" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "sebagaimana" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "seolah-olah" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "seperti" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        
        "karena" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "sebab" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "oleh karena" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        "oleh sebab" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "maka", "makanya", "sehingga", "sampai", "tanpa", "bahwa"],
        
        "maka" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "tanpa", "bahwa"],
        "makanya" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "tanpa", "bahwa"],
        "sehingga" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "tanpa", "bahwa"],
        "sampai" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "tanpa", "bahwa"],
        #"sampai-sampai" : [],

        "dengan" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "bahwa"],
        "tanpa" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "bahwa"],
        
        "bahwa" : ["asalkan", "apabila", "jika", "jikalau", "kalau", "manakala", "andaikan", "seandainya", "sekiranya", "serumpamanya", "andai kata", "agar", "biar", "supaya", "biarpun", "kendati", "kendatipun", "meski", "meskipun", "sekalipun", "sungguhpun", "walau", "walaupun", "alih-alih", "daripada", "laksana", "seakan-akan", "sebagai", "sebagaimana", "seolah-olah", "seperti", "karena", "sebab", "oleh karena", "oleh sebab", "maka", "makanya", "sehingga", "sampai", "tanpa"],
        
        #"yang" : [],
                        
    }

    error_type_id = "CONJ"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        token_form_lower = token.form.lower()

        if len(self.list_conjunction_error_substitution.get(token_form_lower, [])) > 0:
            self.original_token_list = [token]
            self.error_token_list = random.choice(self.list_conjunction_error_substitution[token_form_lower]).split(" ")

            self.error_type = "|||R:CONJ|||"
            self.related_token_id = [token.id]

            # Token After (if there is any) will be added to related_token 
            token_id_after = token.id + 1
            if sentence.does_token_id_exists(token_id_after):
                token_after = sentence.get_token_by_id(token_id_after)
                self.related_token_id = [token.id, token_after.id]



class DeterminerError(Error):

    error_type_id = "DET"
    max_ratio = 0.1

    penggolong_word_list = ['orang', 'ekor', 'buah', 'batang' , 'bentuk', 'bidang' , 'belah', 'helai', 'bilah', 'utas', 'potong', 'tangkai', 'butir', 'pucuk', 'carik', 'rumpun', 'keping', 'biji', 'kuntum', 'patah', 'laras', 'kerat']
    penggolong_subtitution_choices = ['orang', 'ekor', 'buah', 'batang' , 'bentuk', 'bidang' , 'belah', 'helai', 'bilah', 'utas', 'potong', 'tangkai', 'butir', 'pucuk', 'carik', 'rumpun', 'keping', 'biji', 'kuntum', 'patah']

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        if token.upos == 'DET' and token.lemma in self.penggolong_word_list:
            self.original_token_list = [token]
            self.error_token_list = token.form.replace(token.lemma, random.choice([penggolong for penggolong in self.penggolong_subtitution_choices if penggolong != token.lemma])).split(" ")

            self.error_type = "|||R:DET|||"
            self.related_token_id = [token.id]

            # Token After (if there is any) will be added to related_token 
            token_id_after = token.id + 1
            if sentence.does_token_id_exists(token_id_after):
                token_after = sentence.get_token_by_id(token_id_after)
                self.related_token_id = [token.id, token_after.id]
                


class MorphologyError(Error):

    deprel_nominals = ["nsubj", "obj", "iobj", "obl"]

    error_type_id = "MORPH"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        token_id_after = token.id + 1
        token_after = None
        if sentence.does_token_id_exists(token_id_after):
            token_after = sentence.get_token_by_id(token_id_after)

        token_morf_plus_sign = "+".join(token.morf)
        if (
            (
                token.upos == 'VERB' 
                and token_morf_plus_sign.count('ber+') == 1 
                and token_morf_plus_sign.count('+') == 1
            )
            and not
            (
                token_after is not None and token_after.deprel in self.deprel_nominals
            )
        ):
            self.original_token_list = [token]
            self.error_token_list = sentence.dataset.get_most_similar("pe" + token.lemma + 'an').split(" ")
            
            self.error_type = "|||R:MORPH|||"
            self.related_token_id = [token.id]

        elif (
            token.upos == 'NOUN' 
            and token_morf_plus_sign.count('per+') == 1
            and token_morf_plus_sign.count('+an') == 1
        ):
            self.original_token_list = [token]
            self.error_token_list = sentence.dataset.get_most_similar("ber" + token.lemma).split(" ")
            
            self.error_type = "|||R:MORPH|||"
            self.related_token_id = [token.id]


class NounError(Error):

    error_type_id = "NOUN"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        if token.upos == 'NOUN':

            # Get synonym of token form
            sinonims = sentence.dataset.get_sinonim(token.form)

            # Only add error if there is sinonims
            if len(sinonims) > 0:
                self.original_token_list = [token]
                self.error_token_list = random.choice(sinonims).split(" ")

                self.error_type = "|||R:NOUN|||"
                self.related_token_id = [token.id]


class NounInflectionError(Error):

    error_type_id = "NOUN:INFL"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
    
        token = self.token
        
        if (token.upos=='NOUN' and (token.morf.count('peN') == 1 or token.morf.count('pe') == 1 or token.morf.count('per') == 1)):
            
            prefix = ""

            if token.form[:3].lower() == "per":
                prefix = random.choice(["pen", "pe"])
            elif token.form[:3].lower() == "pen":
                prefix = random.choice(["per", "pe"])
            elif token.form[:3].lower() == "peng":
                prefix = random.choice(["per", "pen", "pe"])
            elif token.form[:3].lower() == "pem":
                prefix = "pe"
            elif token.form[:3].lower() == "peny":
                prefix = "pen"
            
            ubah_kata = prefix + token.lemma

            if prefix:
                if token.morf.count('an') == 1:
                    if token.lemma[-1] == "a":
                        ubah_kata = ubah_kata + "n"
                    else :
                        ubah_kata = ubah_kata + "an"
            
                self.original_token_list = [token]
                self.error_token_list = ubah_kata.split(" ")

                self.error_type = "|||R:NOUN:INFL|||"
                self.related_token_id = [token.id]





class OrthographyError(Error):
    
    error_type_id = "ORTH"
    max_ratio = 0.1

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

                    # Only generate orth error if the first char of token after is not Capitalized
                    # If capitalized, usually is a place name, etc. which is unlikely in errors
                    # Ex. error sentence: "Saya pergi keJakarta" seldom appears
                    if not token_after.form[0].isupper():
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

    particle_list = ["lah", "kah", "pun"]

    error_type_id = "PART"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        
        # If particle is by itself (not as suffix)
        if token.upos in ["PART"] and token.form.lower() in self.particle_list:
            self.original_token_list = [token]

            particle_substitution_choices = list(set(self.particle_list) - set([token.form.lower()]))
            self.error_token_list = random.choice(particle_substitution_choices).split(" ")
            
            self.error_type = "|||R:PART|||"
            self.related_token_id = [token.id]
        
        # If particle is suffix of a token
        elif token.morf[-1].lower() in self.particle_list:
            self.original_token_list = [token]

            original_particle = token.morf[-1].lower()
            original_without_particle = token.form[:-len(original_particle)]

            particle_substitution_choices = list(set(self.particle_list) - set([original_particle]))
            particle_error_chosen = random.choice(particle_substitution_choices)

            self.error_token_list = [original_without_particle + particle_error_chosen]

            self.error_type = "|||R:PART|||"
            self.related_token_id = [token.id]



class PrepositionError(Error):

    dict_prepositions_errors = {
        "akan" : ["antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "hingga", "ke", "kecuali", "lepas", "oleh", "per", "sampai", "tentang", "sejak", "seperti", "serta", "tanpa", "untuk"],
        "antara" : ["atas", "bagi", "dalam", "dari", "demi", "dengan", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "serta", "tanpa", "tentang", "untuk"],
        "atas" : ["akan", "antara", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "bagi" : ["akan", "antara", "atas", "dalam", "dari", "demi", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "serta"],
        #"buat" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "dalam" : ["akan", "antara", "atas", "bagi", "dari", "demi", "dengan", "di", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "dari" : ["akan", "antara", "atas", "bagi", "dalam", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "demi" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "dengan" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "di" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "hingga" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "ke" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "kecuali" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "lepas" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        #"lewat" : [],
        "oleh" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "pada" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "per" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "sampai" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sejak", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "sejak" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "seperti", "serta", "tanpa", "tentang", "untuk"],
        "seperti" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "serta", "tanpa", "tentang", "untuk"],
        "serta" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "tanpa", "tentang", "untuk"],
        "tanpa" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tentang", "untuk"],
        "tentang" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "untuk"],
        "untuk" : ["akan", "antara", "atas", "bagi", "dalam", "dari", "demi", "dengan", "di", "hingga", "ke", "kecuali", "lepas", "oleh", "pada", "per", "sampai", "sejak", "seperti", "serta", "tanpa", "tentang"],
    }

    always_treat_as_ADP_list = []

    error_type_id = "PREP"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        token_form_lower = token.form.lower()

        if (
            (token.upos in ["ADP"] or token_form_lower in self.always_treat_as_ADP_list) 
            and token_form_lower in self.dict_prepositions_errors 
            and len(self.dict_prepositions_errors[token_form_lower]) > 0
        ):
            self.original_token_list = [token]
            self.error_token_list = random.choice(self.dict_prepositions_errors[token_form_lower]).split(" ")

            self.error_type = "|||R:PREP|||"
            self.related_token_id = [token.id]

            # Token After (if there is any) will be added to related_token 
            token_id_after = token.id + 1
            if sentence.does_token_id_exists(token_id_after):
                token_after = sentence.get_token_by_id(token_id_after)
                self.related_token_id = [token.id, token_after.id]


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

        if (token.upos == 'PRON' and token.form in self.list_all_persona_pronoun):
            self.error_token_list = random.choice(random.choice([value for key, value in self.persona_pronoun_errors.items() if key not in self.list_blacklist_persona_pronoun(token.form)])).split(" ")
            self.original_token_list = [token]

            self.error_type = "|||R:PRON|||"
            self.related_token_id = [token.id]

        elif (token.upos == 'PRON' and token.form in self.pronomina_penanya):

            if token.form == "mengapa" or token.form == "kenapa" :
                tmp_pronomina_penanya = self.pronomina_penanya.copy()
                tmp_pronomina_penanya.pop(tmp_pronomina_penanya.index("mengapa"))
                tmp_pronomina_penanya.pop(tmp_pronomina_penanya.index("kenapa"))
                self.error_token_list = token.form.replace(token.lemma, random.choice(tmp_pronomina_penanya)).split(" ")
            else:
                tmp_pronomina_penanya = self.pronomina_penanya.copy()
                tmp_pronomina_penanya.pop(tmp_pronomina_penanya.index(token.lemma))
                self.error_token_list = random.choice(tmp_pronomina_penanya).split(" ")

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

        if (token.upos == 'PUNCT' and token.lemma == "," and token_after != None  and token_after.upos=='CCONJ' and token_after.lemma in {"dan","atau","tetapi","melainkan","sedangkan"}):
            self.original_token_list = [token]
            self.error_token_list = [""]

            self.error_type = "|||M:PUNCT|||"
            self.related_token_id = [token.id]

        elif ((ada_Anak_Kalimat == 1 or ada_Kalimat_tambahan == 1) and token.lemma == ","): 
            self.original_token_list = [token]
            self.error_token_list = [""]

            self.error_type = "|||M:PUNCT|||"
            self.related_token_id = [token.id]
        
        elif token.upos == 'PUNCT' and token.lemma in ["?", "!"]:
            self.original_token_list = [token]
            self.error_token_list = ["."]

            self.error_type = "|||R:PUNCT|||"
            self.related_token_id = [token.id]

        elif token.upos == 'PUNCT' and token.lemma == ".":
            # Do this 1 in 50 occurence of ".",
            # So PUNCT error will not be saturated by this kind of error
            if random.randrange(1, 50) == 1:
                self.original_token_list = [token]
                self.error_token_list = [""]

                self.error_type = "|||M:PUNCT|||"
                self.related_token_id = [token.id]
            
       


class SpellingError(Error): #Membuat spelling error

    error_type_id = "SPELL"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        
        if token.form.isalpha() and len(token.form) > 3:
            rand = random.randrange(1, 5)
            apakah_akan_dilakukan = random.randrange(1, 100)

            if apakah_akan_dilakukan == 1 and rand == 1: ## Erase one char
            
                self.original_token_list = [token]
                index = random.randrange(0, len(token.form)-1)
                self.error_token_list = [token.form[:index] + token.form[index + 1:]]

                self.error_type = "|||R:SPELL|||"
                self.related_token_id = [token.id]
        
            elif apakah_akan_dilakukan == 1 and rand == 2: ## Add one char
                
                self.original_token_list = [token]

                # Get random noise character which is not the same as the original char
                index = random.randrange(0, len(token.form)-1)
                char_chosen = token.form[index]
                noise_char = char_chosen   # Initially noise char == char chosen
                while noise_char == char_chosen:
                    noise_char = random.choice(string.ascii_lowercase)

                self.error_token_list = [token.form[:index] + noise_char + token.form[index + 1: ]]

                self.error_type = "|||R:SPELL|||"
                self.related_token_id = [token.id]

            elif apakah_akan_dilakukan == 1 and rand == 3: ## Tukar char sebelahnya
                
                self.original_token_list = [token]
                index = random.randrange(1, len(token.form)-2)
                self.error_token_list  = [token.form[:index] + token.form[index+1] + token.form[index]  + token.form[index + 2: ]]
                
                self.error_type = "|||R:SPELL|||"
                self.related_token_id = [token.id]

            elif apakah_akan_dilakukan == 1 and rand == 4 and len(list(filter(lambda x: x in self.huruf_hidup, token.lemma))) > 0:
                
                self.original_token_list = [token]
                self.error_token_list = [(token.form[0] + re.sub("[aeiou]", "", token.form[1:])).replace("ng", "g")]

                self.error_type = "|||R:SPELL|||"
                self.related_token_id = [token.id]


class VerbError(Error):

    error_type_id = "VERB"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        if token.upos == 'VERB':

            # Get synonym of token form
            sinonims = sentence.dataset.get_sinonim(token.form)

            # Only add error if there is sinonims
            if len(sinonims) > 0:
                self.original_token_list = [token]
                self.error_token_list = random.choice(sinonims).split(" ")
                
                self.error_type = "|||R:VERB|||"
                self.related_token_id = [token.id]


class VerbInflectionError(Error):
    
    luluh_exception = ['mempunyai', 'mengkaji']

    error_type_id = "VERB:INFL"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token

        token_form_lower = token.form.lower()
        token_lemma = token.lemma

        # init var
        prefix = ""

        if token.upos == 'VERB' and token.morf[0] != token_lemma:
            if (
                (token_form_lower[:2] == "me" and token_lemma[0] in self.konsonan_luluh and token_lemma[1] in self.huruf_hidup and token_form_lower not in self.luluh_exception)
                or (token_form_lower[:2] == "me" and token_lemma in {'b','f'})
                or (token_form_lower[:2] == "me" and len(list(filter(lambda x: x in self.huruf_hidup, token_lemma))) == 1)
            ):
                # If prefix has substring "me", and the above if conditions apply,
                # then error can be generated by replacing prefix with "men"
                prefix = "men"

            elif token.morf[0] == "ber":
                if token_form_lower[:3] == "ber":
                    prefix = "be"
                else:
                    prefix = "ber"

            elif token.morf[0] == "ter":
                if token_form_lower[:3] == "ter":
                    prefix = "te"
                else:
                    prefix = "ter"

            if prefix:
                try:
                    lemma_and_suffix = "".join(token.morf[token.morf.find(token_lemma):])
                except:
                    lemma_and_suffix = "".join(token.morf[1:])

                self.original_token_list = [token]
                self.error_token_list = (prefix + lemma_and_suffix).split(" ")

                self.error_type = "|||R:VERB:INFL|||"
                self.related_token_id = [token.id]


class VerbTenseError(Error):

    konsonan_luluh_exception = ['dipunyai', 'dikaji'] #bahasa asing

    me_group = ['l', 'm', 'n', 'r', 'w']
    mem_group = ['b', 'p', 'f']
    meng_group = ['k', 'g', 'h', 'o']
    meny_group = ['s']
    menge_group = ['l']
    menge_one_vowel_group = ['c']
    # The rest is men_group ex. t

    deprel_nominals = ["nsubj", "obj", "iobj", "obl", "vocative", "expl", "dislocated", "obl", "vocative", "expl", "dislocated"]

    no_passive_state = ["menjadi", "merupakan"]

    error_type_id = "VERB:TENSE"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        token_lemma = token.lemma
        
        # init var
        error_words = ""
        
        if token.upos == 'VERB' and token.feats and "Voice" in token.feats and token.form.lower() not in self.no_passive_state:

            # Get Form without Prefix (if theres any)
            try:
                lemma_and_suffix_list = token.morf[token.morf.find(token_lemma):]
            except:
                if token.morf[0] != token_lemma:
                    lemma_and_suffix_list = token.morf[1:]
                else:
                    lemma_and_suffix_list = token.morf

            # Get next two tokens
            token_id_after = token.id + 1
            token_after = None
            if sentence.does_token_id_exists(token_id_after):
                token_after = sentence.get_token_by_id(token_id_after)

            token_id_two_after = token.id + 2
            token_two_after = None
            if sentence.does_token_id_exists(token_id_two_after):
                token_two_after = sentence.get_token_by_id(token_id_two_after)

            # Act -> Pass
            # If only next_token is a nominal OR next_two_token is a nominal and next_token supports next_two_token
            if (
                token.feats["Voice"] == "Act" 
                and (
                        (
                            token_after is not None 
                            and token_after.deprel in self.deprel_nominals
                        ) 
                    or  (
                            token_after is not None 
                            and token_two_after is not None 
                            and token_two_after.deprel in self.deprel_nominals 
                            and token_after.head == token_two_after.id
                        )
                    )
            ):
                error_words = "di" + "".join(lemma_and_suffix_list)
            
            # Pass -> Act
            elif token.feats["Voice"] == "Pass":

                lemma_and_suffix = "".join(lemma_and_suffix_list)
                if token_lemma[0] in self.konsonan_luluh and token_lemma[1] in self.huruf_hidup:
                    if lemma_and_suffix_list[0] != token.lemma and lemma_and_suffix_list[0][0] in self.konsonan_luluh:
                        # If Consonant starts second lemma.
                        token_lemma = lemma_and_suffix
                    else:
                        # If not, leburkan konsonan
                        lemma_and_suffix = "".join(lemma_and_suffix_list)[1:]

                if token_lemma[0] in self.me_group:
                    error_words = "me" + lemma_and_suffix
                elif token_lemma[0] in self.mem_group:
                    error_words = "mem" + lemma_and_suffix
                elif token_lemma[0] in self.meng_group:
                    error_words = "meng" + lemma_and_suffix
                elif token_lemma[0] in self.meny_group:
                    error_words = "meny" + lemma_and_suffix
                elif token_lemma[0] in self.menge_group:
                    error_words = "menge" + lemma_and_suffix
                elif token_lemma[0] in self.menge_one_vowel_group and len(list(filter(lambda x: x in self.huruf_hidup, token.lemma))) == 1:
                    error_words = "menge" + lemma_and_suffix
                else:
                    error_words = "men" + lemma_and_suffix

            if error_words:
                self.original_token_list = [token]
                self.error_token_list = error_words.split(" ")

                self.error_type = "|||R:VERB:TENSE|||"
                self.related_token_id = [token.id]



class WordOrderError(Error):

    error_type_id = "WO"
    max_ratio = 0.1

    def __init__(self, token, sentence):
        super().__init__(token, sentence)

    def generate_error(self):
        token = self.token
        sentence = self.sentence

        token_id_after = token.id + 1
        token_after = None
        if sentence.does_token_id_exists(token_id_after):
            token_after = sentence.get_token_by_id(token_id_after)

        if token.upos == 'NOUN' and token_after and token_after.upos in ['PRON', 'ADJ']:
            self.original_token_list = [token, token_after]

            if token.id == 0: # If token is first in sentence
                if token_after.form == token_after.form.upper():
                    # if token_after is all capitalized
                    self.error_token_list = [token_after.form[0].upper() + token_after.form[1:], token.form]
                else:
                    # if token_after is not all capitalized
                    self.error_token_list = [token_after.form[0].upper() + token_after.form[1:], token.form[0].lower() + token.form[1:]]

            else:
                self.error_token_list = [token_after.form, token.form]

            self.error_type = "|||R:WO|||"
            self.related_token_id = [token.id, token_after.id]