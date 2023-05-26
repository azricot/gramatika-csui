

class Sentence():
    
    def __init__(self, sentence_conll, dataset):
        self.sentence_conll = sentence_conll
        self.dataset = dataset
        self.token_list = []
        self.error_list = []

        self.init_token_list()

        self.generate_error()

    def init_token_list(self):
        skip_it = 0
        token_index = 0

        for token_id in range(len(self.sentence_conll)):
            # Skip iterations by skip_it value
            if skip_it > 0:
                skip_it -= 1
                continue

            token = self.sentence_conll[token_id]

            if isinstance(token["id"], tuple):
                # If token type tuple, combine all child token to one Token instance
                start_id = token["id"][0]
                end_id = token["id"][-1]
                len_tuple = end_id - start_id + 1

                tokens_in_tuple = []
                for i in range(1, len_tuple+1):
                    # Append n token after token type tuple (with n = len_tuple)
                    tokens_in_tuple.append(self.sentence_conll[token_id+i])

                # For now, main child token will always be the first token in tuple
                main_child_token = tokens_in_tuple[0]

                self.token_list.append(
                    self.Token(
                        token_conll=token,
                        token_index=token_index,
                        token_childs=tokens_in_tuple,
                        main_child_token=main_child_token,
                    )
                )

                skip_it = len_tuple
            else:
                self.token_list.append(
                    self.Token(
                        token_conll=token,
                        token_index=token_index,
                    )
                )

            token_index += 1

    def get_token_by_id(self, id):
        return self.token_list[id]
    
    def does_token_id_exists(self, id):
        return (0 <= id < self.len())
    
    def len(self):
        return len(self.token_list)
    
    def is_valid(self):
        if self.len() > 0:
            return True
        else:
            return False
        
    def has_error(self):
        return len(self.error_list) > 0

    def generate_error(self):
        for token in self.token_list:
            dataset_error_dict = self.dataset.error_dict

            # Try to generate all error for this particular token in sentence
            # If error generated not valid, then don't save to list
            for error_type_id in dataset_error_dict.keys():
                error = dataset_error_dict[error_type_id]["class"](
                    token=token,
                    sentence=self,
                )

                if error.is_valid():
                    self.error_list.append(error)

        self.clean_generated_error()
        self.update_error_count()

    
    def clean_generated_error(self):
        self.filter_by_max_ratio()
        self.clean_collisions()
        self.clean_maximum_error_types_in_sentence()
        self.clean_maximum_error_in_sentence()
        self.resort_for_output()

        # if len(self.error_list):
        #     print("____________________")
        # for error in self.error_list:
        #     print(error.token)
        #     print(error.error_type_id)
        #     print(error.get_ratio())

    def filter_by_max_ratio(self):
        self.error_list = [error for error in self.error_list if error.is_below_max_ratio()]

    def clean_collisions(self):
        error_list_temp = self.error_list
        error_list_result_temp = []

        for token in self.token_list:
            id = token.id

            # Filter to only errors with related id
            error_related_to_id = [error for error in error_list_temp if id in error.related_token_id]
            
            # Sort by ratio (ascending)
            error_related_to_id.sort(key=lambda error : error.get_ratio())

            # If related error exists
            if len(error_related_to_id) > 0:
                # append error with the least in ratio (most needed)
                error_list_result_temp.append(error_related_to_id[0])

                # Remove all related error from main list (because it would collide with selected error above)
                for error in error_related_to_id:
                    error_list_temp.remove(error)
        
        # Assign cleaned collisions list to error_list
        self.error_list = error_list_result_temp

    def clean_maximum_error_types_in_sentence(self):
        types_in_list = {error.error_type_id for error in self.error_list}
        error_list_result_temp = []

        for error_type_id in types_in_list:
            # Get list of error which has current error_type_id
            temp = [error for error in self.error_list if error.error_type_id == error_type_id]
            # Sort by ratio (ascending)
            temp.sort(key=lambda error : error.get_ratio())

            # Only add the same type of errors according to args.max_same_error_in_sentence
            # starting with the least in ratio (most needed)
            error_list_result_temp.extend(temp[:self.dataset.max_same_error_in_sentence])

        # Assign cleaned maximum error types list to error_list
        self.error_list = error_list_result_temp

    def clean_maximum_error_in_sentence(self):
        # Sort by ratio (ascending)
        self.error_list.sort(key=lambda error : error.get_ratio())

        # Only add errors according to args.max_error_in_sentence
        # starting with the least in ratio (most needed)
        self.error_list = self.error_list[:self.dataset.max_error_in_sentence]

    def resort_for_output(self):
        self.error_list.sort(key=lambda error : [token.id for token in error.original_token_list])

    def update_error_count(self):
        for error in self.error_list:
            self.dataset.error_dict[error.error_type_id]["count"] += 1




    class Token():

        def __init__(self, token_conll, token_index, token_childs=[], main_child_token=None):
            self.__id = token_index

            # If id is tuple, child tokens will be combined into one Token object
            if isinstance(token_conll["id"], tuple):
                self.__token_conll = main_child_token   # Save token of child which is the main one
                self.__form = token_conll["form"]       # Save form of token with id type tuple
                
                morf_list = []
                for child in token_childs:
                    child_morf_conllu = child["misc"]["Morf"]

                    # Clean morf string from conllu format (remove '<UPOS>_UPOS')
                    child_morf_cleaned = child_morf_conllu.split("+")
                    for morf_part_idx in range(len(child_morf_cleaned)):
                        child_morf_cleaned[morf_part_idx] = child_morf_cleaned[morf_part_idx].split("<")[0].split("_")[0]

                    morf_list.extend(child_morf_cleaned)

                self.__morf = morf_list

            else: # token is not type tuple
                self.__token_conll = token_conll
                self.__form = self.token_conll["form"]

                morf_list = []
                # Clean morf string from conllu format (remove '<UPOS>_UPOS')
                if token_conll["misc"]["Morf"]:
                    for morf_part in token_conll["misc"]["Morf"].split("+"):
                        morf_list.append(morf_part.split("<")[0].split("_")[0])
                else:
                    morf_list.append("")

                self.__morf = morf_list

            # SpaceAfter Attribute
            if 'SpaceAfter' in self.token_conll['misc']:
                self.__space_after = True
            else:
                self.__space_after = False

        @property
        def token_conll(self):
            return self.__token_conll
        
        @property
        def id(self):
            return self.__id

        @property
        def form(self):
            return self.__form
        
        @property
        def lemma(self):
            return self.token_conll["lemma"]
        
        @property
        def upos(self):
            return self.token_conll["upos"]
        
        @property
        def xpos(self):
            return self.token_conll["xpos"]
        
        @property
        def feats(self):
            return self.token_conll["feats"]
        
        @property
        def head(self):
            return self.token_conll["head"]
        
        @property
        def deprel(self):
            return self.token_conll["deprel"]
        
        @property
        def deps(self):
            return self.token_conll["deps"]
        
        @property
        def morf(self):
            return self.__morf
        
        @property
        def space_after(self):
            return self.__space_after
        
        def __str__(self):
            return self.form