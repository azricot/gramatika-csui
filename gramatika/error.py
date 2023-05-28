
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
        if len(sinonims) == 0:
            sinonims = sentence.dataset.get_sinonim(token.lemma) # if sinonym of token.form is not found, then search sinonym for its lemma

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

    list_CCONJ = ['dan', 'atau', 'melainkan', 'sedangkan', 'serta', 'tetapi']

    list_conjunction_error_substitution = {
        # ---- CCONJ
        "dan" : list_CCONJ,
        "atau" : list_CCONJ,
        "melainkan" : list_CCONJ,
        "sedangkan" : list_CCONJ,
        "serta" : list_CCONJ,
        "tetapi" : list_CCONJ,
        "padahal" : list_CCONJ,

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

        token_form_lower = token.form.lower()

        if (
            token_form_lower in self.always_treat_as_CONJ_list 
            and len(self.list_conjunction_error_substitution[token_form_lower]) > 0
        ):
            self.original_token_list = [token]
            self.error_token_list = random.choice(self.list_conjunction_error_substitution[token_form_lower]).split(" ")

            self.error_type = "|||R:CONJ|||"
            self.related_token_id = [token.id]



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

            # Token After (if there is any) will be added to related_token 
            token_id_after = token.id + 1
            if sentence.does_token_id_exists(token_id_after):
                token_after = sentence.get_token_by_id(token_id_after)
                self.related_token_id = [token.id, token_after.id]
                


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
        token = self.token
        sentence = self.sentence

        if token.upos == 'NOUN':

            # Get synonym of token form
            # if sinonym of token.form is not found, then search sinonym for its lemma
            sinonims = sentence.dataset.get_sinonim(token.form)
            if len(sinonims) == 0:
                sinonims = sentence.dataset.get_sinonim(token.lemma)

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
        token = self.token
        sentence = self.sentence

        if token.upos == 'VERB':

            # Get synonym of token form
            # if sinonym of token.form is not found, then search sinonym for its lemma
            sinonims = sentence.dataset.get_sinonim(token.form)
            if len(sinonims) == 0:
                sinonims = sentence.dataset.get_sinonim(token.lemma)

            # Only add error if there is sinonims
            if len(sinonims) > 0:
                self.original_token_list = [token]
                self.error_token_list = random.choice(sinonims).split(" ")

                self.error_type = "|||R:VERB|||"
                self.related_token_id = [token.id]


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
        token = self.token
        sentence = self.sentence

        token_id_after = token.id + 1
        token_after = None
        if sentence.does_token_id_exists(token_id_after):
            token_after = sentence.get_token_by_id(token_id_after)

        if token.upos == 'NOUN' and token_after and token_after.upos == 'PRON':
            self.original_token_list = [token, token_after]
            self.error_token_list = [token_after.form, token.form]

            self.error_type = "|||R:WO|||"
            self.related_token_id = [token.id, token_after.id]