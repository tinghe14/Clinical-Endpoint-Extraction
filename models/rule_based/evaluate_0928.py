import pandas as pd 
import os 
import sys
sys.path.append("/Users/tinghe/Desktop/phd research/NCI_rule/Tumor Size")
sys.path.append("/Users/tinghe/Desktop/phd research/NCI_rule/Tumor Size/deepphe")
import extract_tumor_size_0913 as extract_tumor_size
import extract_tumor_size_java as extract_tumor_size_java
from collections import Counter
from contextlib import redirect_stdout
from args_0928 import create_parser

parser = create_parser()
args = parser.parse_args()


def convert(x):
    if isinstance(x, float):
        pass 
    else:
        return x.split(";")

FINAL = "/Users/tinghe/Desktop/phd research/NCI_rule/Tumor Size/tcga_reports_from_columbia/split_seed_TCGA_Reports.csv"
final = pd.read_csv(FINAL,nrows=303) #skiprows=list(range(203)), nrows=100
final = final.iloc[203:303] #[203:303] #[:203]
final["convert_gold"] = final["gold"].apply(convert)
final.drop_duplicates(subset="Unnamed: 0",keep="first",inplace=True)
# final = final.head(100)

def evaluate(BIO=False):
    TP_ALL, FP_ALL, FN_ALL = 0, 0, 0
    output_dct = dict()
    # with open('/Users/tinghe/Desktop/phd research/NCI_rule/Tumor Size/output.txt', 'a') as f:
    #     with redirect_stdout(f):
    for _, line in final.iterrows():
        text = line["text"]
        output_dct[line['Unnamed: 0']] = dict()
        labels = line["convert_gold"]
        if labels is None or len(labels) == 0:
            labels = []
        else:
            labels = [word.lower() for word in labels]
        
        # tumor size found by algo
        if args.MODEL == "['own']":
            pred_triple = extract_tumor_size.add_sentence_sizes(text)
        elif args.MODEL == "['deepphe']":
            pred_triple = extract_tumor_size_java.add_sentence_sizes(text)
        else:
            print("ERROR: none of this model!!!", f"{args.MODEL}", f"{len(args.MODEL)}", f"{type(args.MODEL)}")
        label_count = Counter(labels)
        predictions = [triple[2] for triple in pred_triple]
        prediction_count = Counter(predictions)
        inds = [(triple[0], triple[1]) for triple in pred_triple]

        
        word_lst = text.split(" ")
        bio_lst = ["O"] * len(word_lst)
        if BIO == True and len(pred_triple) != 0:
            for item in pred_triple:
                start, end = item[0], item[1]
                while text[start-1] != " ":
                    start -= 1
                while text[end] != " ":
                    end += 1
                word_start = len(text[:start].split(" ")) -1
                word_end = len(text[:end].split(" "))
                bio_lst[word_start:word_end-1] = ["I_tumorSize"] * (word_end-word_start)
                bio_lst[word_start] = "B_tumorSize"
                # print(text[start:end], word_lst[word_start:word_end])

        # True Positives (TP): Items that appear in both, counted by the minimum occurrences in both lists
        TP_items = label_count & prediction_count  # Intersection of counts
        TP = sum(TP_items.values())  # Sum of the minimum counts of matched items
        if TP > 0:
            TP_ALL += TP

        # False Positives (FP): Items in predictions that are not in labels or over-predicted
        FP_items = Counter(predictions) - Counter(labels)  # Items in predictions but not in labels
        FP = sum(FP_items.values())
        if FP > 0:
            FP_ALL += FP

        # False Negatives (FN): Items in labels that are not in predictions or under-predicted
        FN_items = Counter(labels) - Counter(predictions)  # Items in labels but not in predictions
        FN = sum(FN_items.values())
        if FN > 0: 
            FN_ALL += FN 

        output_dct[int(line["Unnamed: 0"])] = {
            "gold":labels, 
            "pred": predictions ,
            "TP": TP_items,
            "FP": FP_items, 
            "FN": FN_items,
            "word_lst": word_lst,
            "bio_lst":bio_lst,
            "filename":line['patient_filename'],
            "inds": inds,
        }

        # print(sorted(output_dct.keys()))
        
    precision = TP_ALL / (TP_ALL + FP_ALL)
    recall = TP_ALL /(TP_ALL + FN_ALL)
    if precision+recall == 0:
        f1 = 0
    else:
        f1 = (precision*recall*2)/(precision+recall)
    

    # sorting output format
    sorted(output_dct)
    if BIO == False:
        print("*"*10)
        print(f"--MODEL={args.MODEL}",
            f"--STOP_THEN_MATCH_CHAR_DISTANCE={args.STOP_THEN_MATCH_CHAR_DISTANCE}",
            f"--MATCH_THEN_STOP_CHAR_DISTANCE={args.MATCH_THEN_STOP_CHAR_DISTANCE}",
            f"--STOP_WORD_DISTANCE={args.STOP_WORD_DISTANCE}",
            f"--PRECEDING_WORD={args.PRECEDING_WORD}",
            f"--FOLLOWING_WORD={args.FOLLOWING_WORD}")
        
        for key in output_dct.keys():
            print("~"*5,f"{key, output_dct[key]['filename']}","~"*5)
            print(f'gold : {output_dct[key]["gold"]}')
            print(f'pred : {output_dct[key]["pred"]}')
            # print(f'ind: {output_dct[key]["inds"]}')
            
            if len(output_dct[key]["TP"]) > 0:
                print(f'TP : {output_dct[key]["TP"]}')
            if len(output_dct[key]["FP"]) > 0:
                print(f'FP : {output_dct[key]["FP"]}')
            if len(output_dct[key]["FN"]) > 0:
                print(f'FN : {output_dct[key]["FN"]}')

        print(f"total TP:{TP_ALL}, FP:{FP_ALL}, FN:{FN_ALL}")
        print("precision is {} and recall is {} and F1 is {}".format(precision, recall, f1))
    else:
        for key in output_dct.keys():
            print("~"*5,f"{key, output_dct[key]['filename']}","~"*5)
            for ind in range(len(output_dct[key]["word_lst"])):
                print(f"{output_dct[key]['word_lst'][ind]} \t {output_dct[key]['bio_lst'][ind]}")


def main():
    evaluate(BIO=False)


if __name__ == "__main__":
    main()

# python -u "/Users/tinghe/Desktop/phd research/NCI_rule/Tumor Size/evaluate_0927.py" --STOP_THEN_MATCH_CHAR_DISTANCE=30 --MATCH_THEN_STOP_CHAR_DISTANCE=7 --STOP_WORD_DISTANCE=3 --PRECEDING_WORD=-10 --FOLLOWING_WORD=1 > for_remove_FP.txt