from .tesaurus import Tesaurus
from .sentence import Sentence
from .error import (
    AdjectiveError,
    AdverbError,
    ConjunctionError,
    DeterminerError,
    MorphologyError,
    NounError,
    NounInflectionError,
    OrthographyError,
    ParticleError,
    PrepositionError,
    PronounError,
    PunctuationError,
    SpellingError,
    VerbError,
    VerbInflectionError,
    VerbTenseError,
    WordOrderError,
)

from conllu import parse

from tqdm import tqdm
import random


class GramatikaDataset():

    def __init__(self, args):
        self.input_filename = args.input_filename
        self.output_filename = args.output_filename

        self.__sinonim_dict = Tesaurus(args.sinonim_file)

        self.max_error_in_sentence = args.max_error_in_sentence
        self.max_same_error_in_sentence = args.max_same_error_in_sentence
        self.no_error_sentence_ratio = args.no_error_sentence_ratio

        # Initiate all error types
        list_of_all_error_classes = [
            AdjectiveError,
            AdverbError,
            ConjunctionError,
            DeterminerError,
            MorphologyError,
            NounError,
            NounInflectionError,
            OrthographyError,
            ParticleError,
            PrepositionError,
            PronounError,
            PunctuationError,
            SpellingError,
            VerbError,
            VerbInflectionError,
            VerbTenseError,
            WordOrderError,
        ]

        self.error_dict = {}

        for error_class in list_of_all_error_classes:
            self.error_dict[error_class.error_type_id] = {
                "class" : error_class,
                "count" : 0,
            }

        # List of Senteces
        self.sentence_list = []

    def get_total_error(self):
        total = 0
        for error_type_id in self.error_dict.keys():
            total += self.error_dict[error_type_id]["count"]
        return total

    def get_sinonim_dict(self):
        return self.__sinonim_dict
    
    def get_sinonim(self, word):
        return self.get_sinonim_dict().get_sinonim(word.lower())
    
    def get_most_similar(self, word):
        return self.get_sinonim_dict().get_most_similar(word.lower())

    def generate_dataset(self):
        with open(self.input_filename, "r", encoding="utf8", errors='ignore') as file_input:
            output_conll = parse(file_input.read())

        # Shuffle parsed output_conll randomly every time code runs
        # so the resulting dataset will also be randomized
        random.shuffle(output_conll)

        # Create Sentence objects
        for sentence_conll in tqdm(output_conll):
            sentence = Sentence(
                sentence_conll=sentence_conll,
                dataset=self
            )

            if sentence.is_valid():
                # Only save sentence object if it is valid to be saved
                self.sentence_list.append(sentence)

        self.output_dataset()

    def output_dataset(self):
        result = []
        for sentence in self.sentence_list:
            form_list_of_result_tokens = [e.form for e in sentence.token_list]

            error_result_sentence = "S "
            edit_data = ""
            offset_for_edit_id = 0

            for error in sentence.error_list:
                # Acquire Error Result Sentence
                error_id_start = error.original_token_list[0].id
                error_id_end = error.original_token_list[-1].id

                # First original token will be changed to the error form generated
                form_list_of_result_tokens[error_id_start] = error.get_error_form()
                
                # If original token list is more than 1 token (a phrase),
                # only put the error change on the first spot (code above),
                # then the rest will be assigned ""
                # This is done so error_id will not need offset because appending of data
                if len(error.original_token_list) > 1:
                    for i in range(error_id_start + 1, error_id_end + 1):
                        form_list_of_result_tokens[i] = ""

                # edit data information
                edit_id_start = error.original_token_list[0].id + offset_for_edit_id
                edit_id_end = edit_id_start + error.get_len_error_token_list()
                edit_data += f"\nA {edit_id_start} {edit_id_end}{error.error_type}{error.get_original_form()}|||REQUIRED|||-NONE-|||0"
                
                # Add offset = length of error - length of original
                offset_for_edit_id += error.get_edit_offset()

            # Error Result Combination
            # Remember to remove all the empty strings
            error_result_temp =" ".join([result for result in form_list_of_result_tokens if result != ""])
            error_result_sentence += error_result_temp[0].upper() + error_result_temp[1:]

            # Append error result + edit data to result list
            result.append(f"{error_result_sentence}{edit_data}")

        with open(self.output_filename, "w", encoding="utf8") as file_output:
            file_output.write("\n\n".join(result))

        # Write stats of dataset
        output_file_name = self.output_filename[:self.output_filename.rfind(".")]
        stats_filename = f"{output_file_name}_statistics.txt"

        with open(stats_filename, "w", encoding="utf8") as stat_file_output:
            # Total Data
            total_data = len(self.sentence_list)
            total_with_error = len([sentence for sentence in self.sentence_list if sentence.has_error()])
            total_without_error = len([sentence for sentence in self.sentence_list if not sentence.has_error()])
            
            stat_file_output.write(f"Total Kalimat: {total_data}\n")
            stat_file_output.write(f"Total Kalimat dengan Error: {total_with_error} ({total_with_error / total_data * 100:.2f}%)\n")
            stat_file_output.write(f"Total Kalimat tanpa Error: {total_without_error} ({total_without_error / total_data * 100:.2f}%)\n\n")
            
            total_all_error = self.get_total_error()

            # Total Error yang dibangkitkan
            stat_file_output.write(f"Total Error Dibangkitkan: {total_all_error}\n\n")

            stat_file_output.write(f"Total Tiap Jenis Error:\n")
            # Number of and percentage of each error type
            for error_type_id in self.error_dict.keys():
                total_each_error_type = self.error_dict[error_type_id]["count"]
                ratio_each_error_type = total_each_error_type / total_all_error * 100

                stat_file_output.write(f"- {error_type_id}: {total_each_error_type} ({ratio_each_error_type:.2f}%)\n")