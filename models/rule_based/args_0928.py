import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--MODEL",
                        help="choose from own/deepphe/bert", type=str)
    parser.add_argument("--STOP_THEN_MATCH_CHAR_DISTANCE",
                        help="stop char window: stop word in front of the match", type=int)
    parser.add_argument("--MATCH_THEN_STOP_CHAR_DISTANCE",
                        help="stop char window: match in front of the stop word", type=int)
    parser.add_argument("--STOP_WORD_DISTANCE",
                        help="stop word window: num of words between stop word and the match", type=int)
    parser.add_argument("--PRECEDING_WORD",
                        help="size word window: tumor in front of the match", type=int)
    parser.add_argument("--FOLLOWING_WORD",
                        help="size word window: match in front of the tumor", type=int)
    parser.add_argument("-f", "--fff", 
                    help="a dummy argument to fool ipython", default="1")
    return parser


