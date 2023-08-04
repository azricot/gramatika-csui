from gramatika import GramatikaDataset

import argparse
import os


def arg_file_ext_validation(parser, choices, filename):
    ext = os.path.splitext(filename)[1][1:]
    if ext not in choices:
       parser.error("file extension is not one of {}".format(choices))
    return filename

def get_args():
    parser = argparse.ArgumentParser(
        description="Create Indonesian Synthetic Dataset"
    )

    ## Required parameters
    parser.add_argument("-in", "--input_filename",
                        default=None,
                        type=str,
                        required=True,
                        help="The input filename. Input file should be a text file containing list of data in CoNLL-U format.")
    parser.add_argument("-out", "--output_filename",
                        default=None,
                        type=str,
                        required=True,
                        help="The output filename.")
    
    # Optional Arguments
    parser.add_argument("--sinonim_file",
                        default=None,
                        type=lambda fn:arg_file_ext_validation(parser, ("json"), fn),
                        help="The file containing sinonyms. Should be in json format.")
    parser.add_argument("--max_error_in_sentence",
                        default=6,
                        type=int,
                        help="The maximum number of error in each sentence")
    parser.add_argument("--max_same_error_in_sentence",
                        default=2,
                        type=int,
                        help="The maximum number of the same type of error in each sentence")
    parser.add_argument("--no_error_sentence_ratio",
                        default=0,
                        type=float,
                        help="The estimated ratio of data/sentence which will have no error")
    # parser.add_argument("--",
    #                     default=128,
    #                     type=int,
    #                     help="")
    # parser.add_argument("--",
    #                     action='store_true',
    #                     help="")
    # parser.add_argument('--', type=str, default='',choices=["",])

    args = parser.parse_args()

    return args


def main():
    args = get_args()

    GramatikaDataset(args).generate_dataset()

if __name__ == "__main__":
    main()