"""
UPDATE:
07/19: [Improved]filter out the sizes if within 5-words distance in front of it contains some trigger words
07/19: [Improved]at the end of decimal can have some puncutation & within digits can have space "4. 1 cm"
07/23: "DCIS"&"adenoma" become the trigger word as "cancer" in context or preceeding context to filtering out FP
07/23: [Worse]apply stop word within following text 
07/23: add "margin:" into stop word, make stop distance <= 5
07/23: stop index matched with every matched index, set the 30> char distance should >0
07/23: end of unit can have some puncutation
07/23: str.find() return first occurence of stop words, but we need to compare all of them
09/13: (suba or subb or subc) in string will only check whether suba in string, correct ans is (suba in str) or (subb in str) or (subc in str)
09/15: rather than use nltk sent spliter, better to use context window (previous is correct)
09/28: triple appends when not in res yet, otherwise might double count
11/25: to add: FIBROTHECOMA
"""
import re
import string
from args_0928 import create_parser

parser = create_parser()
args = parser.parse_args()

# Regular expressions cheat sheet: https://shenxiaobing.com/posts/2019/python-regular-expression-cheatsheet/
VALUE_REGEX = r"\d+(?:\.(\s)?\d+)?(\.)?" # 07/19
UNIT_REGEX = r"\s*(mm|cm)(\.)?"
DIM_REGEX = r"\s*[x\*](\.)?\s*"#09/29
FRONT_REGEX = r"(?:(?<=\b)|(?<=\(|\[|\{))"
BACK_REGEX = r"(?:(?=\b)|(?=\,|\.|\?|!|\)|\]|\}))"
FULL_REGEX = (FRONT_REGEX + VALUE_REGEX + r"(?:" + UNIT_REGEX + r")?" +
              r"(?:" + DIM_REGEX + VALUE_REGEX + r"(?:" + UNIT_REGEX + r")?)?" +
              r"(?:" + DIM_REGEX + VALUE_REGEX + r"(?:" + UNIT_REGEX + r")?)?" +
              UNIT_REGEX + BACK_REGEX)
FULL_PATTERN = re.compile(FULL_REGEX, re.IGNORECASE)


SIZE_STOP_WORD_ARRAY = ["distance", "from", "superior", "inferior", "anterior", "posterior", "margin","located", "margin:", "margin.", "located", "according to. criteria,", "nodule", "lymph nodes,","quadrant",\
                        "pt1a:","pt1:","pt1c:","free.","pt1b2.","pt1a.","pt1.","pt1c.","pt1b2:","pt1b1:","pt1b1.","pt1b3:","pt1b3.","pt2:","pt2.","pt2a","pt1a","pt1","pt1c","pt1b2","pt1b1","pt1b3",\
                            "distal", "metastatic", "lymph", "invasion", "invade", "invades", "metastasis", "invading", "invading."] # "second largest", "additional dimension", "additional dimensions"

# # // stop word window
# args.STOP_WORD_DISTANCE = 30 # stop_end ~ match_start
# args.MATCH_THEN_STOP_CHAR_DISTANCE = 7 # match_end ~ stop_start
# args.STOP_WORD_DISTANCE = 5 
# # // tumor window
# args.PRECEDING_WORD = -10
# args.FOLLOWING_WORD = 10


def find_all_occurrences(low_text, stop_lst):
    """str.find(word,start) find word in str from start ind
    """
    res = []
    for stop_word in stop_lst:  
        start = 0
        while True:
            stop_start_ind = low_text.find(stop_word, start)
            stop_end_ind = stop_start_ind + len(stop_word) -1
            if stop_start_ind == -1:
                break
            res.append((stop_start_ind, stop_end_ind))
            start = stop_end_ind+1
    return res

def exclude_stop_word(low_text, match, stop_indices):
    """
    Determine whether this match mention should be exclude based on
        by calcuating the distance
    @ARGS: 
    stop_indices: [(start_ind_stop, end_ind_stop), ...]
    """
    skip = False
    for stop_indexs in stop_indices:
        stop_start_ind, stop_end_ind = stop_indexs

        if stop_end_ind < match.start():
            if (stop_end_ind - match.start()) > args.STOP_WORD_DISTANCE:
                continue
        if match.end() < stop_start_ind:
            if (match.end() - stop_start_ind) > args.MATCH_THEN_STOP_CHAR_DISTANCE:
                continue 

        if match.end() < stop_start_ind:
            curr_dist_str = low_text[match.end():stop_start_ind] 
        if match.start() > stop_end_ind:
            curr_dist_str = low_text[stop_end_ind:match.start()]
        if (len(curr_dist_str.split()) <= args.STOP_WORD_DISTANCE):
            # print(f"Trigger Stop Word {low_text[stop_start_ind:stop_end_ind]}")
            skip = True
            # print(f"skip since len of stop word to matched mention > {args.STOP_WORD_DISTANCE}, which is: {len(curr_dist_str.split())}")
            break 
    return skip

        

# 09/26 Remove Punctuation which Concatate before or after Size
def remove_punc(size):
    while size[0] in string.punctuation:
        size = size[1:]
    while size[-1] in string.punctuation:
        size = size[:-1]
    return size
        

# for reuse 
def add_sentence_sizes(sentence_text, debug_mode=False):
    res = []
    low_text = sentence_text.lower()
    low_text = low_text.strip()
    stop_indices = find_all_occurrences(low_text, SIZE_STOP_WORD_ARRAY)
    # print(f"- stop word lst {[low_text[pair[0]:pair[1]] for pair in stop_indices]}")
    full_matcher = FULL_PATTERN.finditer(low_text)
    
    for match in full_matcher:
        skip_lst = []
        skip = exclude_stop_word(low_text, match, stop_indices)
        skip_lst.append(skip)
        if not any(skip_lst):
            precedingText = sentence_text[0:match.start()]
            followingText = sentence_text[match.end():]
            precedingTextLst = precedingText.strip().lower().split(" ")
            followingTextLst = followingText.strip().lower().split(" ")
            context = precedingTextLst[args.PRECEDING_WORD:]
            followingContext = followingTextLst[:args.FOLLOWING_WORD] #2
            # print(context, followingContext)
            for word in context:
                if ("tumor" in word) or ("carcinoma" in word) or ("DCIS" in word) or ("adenoma" in word) or ("liposarcoma" in word) or ("liposarcoma," in word)\
                    or ("tumour" in word) or ("adenocarcinoma"in word) or ("leiomyomas" in word) or ("sarcoma" in word) or ("leiomyomas" in word):
                    size = sentence_text[match.start():match.end()].lower()
                    size = remove_punc(size)
                    if (match.start(),match.end(), size) not in res:
                        if debug_mode:
                            print("Found size:", (match.start(),match.end()), size)
                        res.append((match.start(), match.end(),size))
            for followingWord in followingContext:
                if ("tumor" in followingWord) or ("carcinoma" in followingWord) or ("DCIS" in followingWord) or ("liposarcoma" in followingWord) or ("liposarcoma," in followingWord)\
                    or ("tumour" in followingWord) or ("adenocarcinoma"in followingWord) or ("leiomyomas" in followingWord) or ("sarcoma" in followingWord) or ("leiomyoma" in followingWord):
                    size = sentence_text[match.start():match.end()].lower() 
                    size = remove_punc(size)
                    if (match.start(),match.end(), size) not in res:
                        if debug_mode:
                            print("Found size:", (match.start(),match.end()), size)
                        res.append((match.start(), match.end(),size))
    # res = list(set(res))
    # if not debug_mode:
    #     print([word for _,_,word in res])
    return res 

if __name__ == "__main__":
    print("test case")
    print("TRUE")
    true_lst = ["D20--RANDOM TUMOR. INFERIOR-EDG D21--UPPER INNER QUADRANT 2. CM.EROM GROSS TUMOR",
        "tumor is 6 mm. ",
                "carcinoma is 6 mm. ",
                "After measuring, the tumor was found to be 5.3cm in diameter, with dimensions of 3 cm x 2 cm x 1.5 cm.",
                "Total Tumor size (1.4 cm x 1.9 cm)",
                "Total Tumor size 1.4 X 1.4 X 1.9 cm",
                "INVASIVE DUCTAL CARCINOMA, 2.8 * 1.4 * 1.9 mm",
                "THE LARGEST FOCUS OF INVASIVE TUMOR MEASURES 3.5 CM IN GREATEST. THE SECOND LARGEST MEASURES 2.5 CM AND IS SEEN IN THE LOWER OUTER.",
                "circumscribed, 3 X 2.9 X 2.8 cm tan-white to grey black tumor mass.",
                "circumscribed, 3 X 2.9 X 2.8 cm tan-white to grey black tumor mass."]
    for pos in true_lst:
        add_sentence_sizes(pos, debug_mode=True)
        ### FN: 
        # 1. "After measuring, the tumor was found to be 5.3cm in diameter, with dimensions of 3 cm x 2 cm x 1.5 cm." -> since word distance between the trigger word






    print("FALSE")
    # false_lst = ["According to. criteria, a tumor mass greater than 5 mm involving the ovarian parenchyma. ",
    #              "INVASIVE DUCTAL CARCINOMA, 2.1 CM LEFT BREAST_URI",
    #     "from the lateral margin. The tumor is located 7.5 cm from the overlying. skin. The specimen is photographed.",
    #     "distance of invasive carcinoma from closest margin: 6 mm. - Specify margin: stapeled margin.",
    #     "with dimensions of 3 cm x 2 cm x 1.5 cm.",
    #     "within 1 cm of the superior and. 5 mm of the",
    #     "tumor range 2 to . ",
    #     ". DUCTAL CARCINOMA IN SITU IS <0.1 CM (1MM) FROM INFERIOR MARGIN."
    # ]
    false_lst = ["from the lateral margin. The tumor is located 7.5 cm ","tumor is located 7.5 cm","tumor 7.5 cm from the overlying","from the lateral margin. The tumor is located 7.5 cm from the overlying. skin."] # from margin
    i = 0
    for neg in false_lst:
        print(f"{'~'*5} example {i} {'~'*5}")
        print(neg)
        add_sentence_sizes(neg, debug_mode=True)
        i += 1
    ### FP:
    # 1."INVASIVE DUCTAL CARCINOMA, 2.1 CM LEFT BREAST_URI" -> since if i add "left" "right" into stop words, the algo in real test will be lower, so remove here


    print('tiplied results:::::')
    test = "CLINICAL HISTORY: Outside hospital left ovarian mass increased CA125, abdominal swelling. GROSS EXAMINATION: A. ""Omentum"", received fresh for frozen and placed in formalin on'. at. is a 19 x 9 x 2 cm fragment of yellow adipose tissue that is firm,. solid and multinodular. Sectioning of the specimen reveals a tan-yellow, firm. parenchyma with some mucous. A representative section was submitted in frozen. in AF1 and submitted in A1. Another representative section will be submitted. as A2. A portion of the specimen was sent for research. B. ""Uterus, cervix, bilateral tubes and ovaries"", received fresh and placed in. formalin on. a 92.6 gram, previously opened hysterectomy. specimen with uterus and cervix, bilateral tubes, and ovaries. The uterus is. 4.5 cm from cornu to cornu, 2.1 cm from anterior to posterior, and 9.1 cm from. superior to inferior. The cervix measures 2.7 cm in diameter with a 1.1 cm. round patent os. The endometrium is grossly unremarkable. The anterior. endometrium measures 1.1 cm from cornu to cornu and 4.5 cm in length. The. posterior endometrium is 0.9 cm from cornu to cornu and 4.1 cm in length. The. ectocervix is tan smooth and glistening with areas of pinpoint hemorrhage. The. endocervical canal also has a 1.8 x 1.5 x 0.5 cm clear mucous deposit. The. uterine serosa is smooth tan and glistening with multiple nodular adhesions. that range in size from 0.2 to 0.4 cm in diameter. There is also an adherent. tan-brown cauterized mass that is adhesed to the serosa, fallopian tube, and. left ovary. The right fallopian tube is also studded with multiple 0.1 to 0.3. cm nodules. The left ovary is extensively adherent to uterus. It is 4.1. x. 3.2 x 2.5 cm and is tan-white and cerebriform with a disrupted capsule that. has tumor grossly extending out of the capsule. The right fallopian tube is. studded with grossly apparent tumor nodules that range in size from 0.1 to 0.3. cm. The left and right parametria are also grossly studded with tumor nodules. that range in size from 0.1 to 0. cm in diameter. The tumor grossly appears. to be adherent to the tube and uterus, and possibly invades the myometrium. The disrupted capsule with the tumor extruding from it is inked. The left. fimbriated tube is 6.1 cm long x 0.4 cm in diameter with a pinpoint patent. lumen, but the tube is stenosed and strictured. The right fimbriated tube is. 4.1 cm long x 0.5 cm in diameter with a pinpoint patent lumen and a strictured. tube. The right ovary is tan-white and cerebriform and is 2.5 x 1.9 x 1.2 cm. The outer surface of the right ovary does not appear to be grossly involved. The right ovary on sectioning is firm tan-white with a hemorrhagic center. The. left ovary on sectioning reveals a heterogeneous parenchyma that is. hemorrhagic, necrotic, and with tumor grossly extending outside the capsule. BLOCK SUMMARY: B1- representative section of anterior cervix. B2- - representative section of posterior cervix. B3- anterior full thickness endometrium. B4- possible tumor to normal myometrium, anterior. B5- posterior full thickness with additional section to serosal nodule. B6- left parametrium. B7- right parametrium. B8- left fallopian tube. B9- right fallopian tube. B10-11- right ovary. B12-15- left ovary with capsule disruption. B17-18- adherent left ovary to uterus. C. ""Left gutter"", received fresh and placed in formalin on. is a 5.5 x 4.2 x 2.5 cm fragment of yellow fibroadipose tissue with some. vessels present. The specimen is firm and nodular with some areas of. cauterized tissue. A representative section is submitted in C1-2. D. ""Omentum # 2"", received fresh and placed in formalin on. is a 12 x 11.5 x 2.4 cm aggregate of yellow fibroadipose tissue with some. solid nodular areas. Representative sections are submitted in B1. E. ""Small bowel nodule"", received fresh and placed in formalin on. is a 5 x 2.9 x 2.4 cm fragment of tan-white tissue that is firm and. has a large nodular area that covers most of the specimen. A representative. section is submitted in E1. INTRA OPERATIVE CONSULTATION: A. ""Omentum"" AF1 (rep) - adenocarcinoma with papillary features (Dr. MICROSCOPIC EXAMINATION: Microscopic examination is performed. PATHOLOGIC STAGE: PROCEDURE: Exploratory laparotomy, total abdominal hysterectomy, bilateral. salpingo-oophorectomy, infragastric omentectomy, removal abdominal wall mass,. and optimal tumor debulking to less than 1 cm of maximal residual disease. PATHOLOGIC STAGE (AJCC 7th Edition) : pT3c pNX pMX. NOTE: Information on pathology stage and the operative procedure is. transmitted to this Institution's Cancer Registry as required for. accreditation by the Commission on Cancer. Pathology stage is based solely. upon the current tissue specimen being evaluated, and does not incorporate. information on any specimens submitted separately to our Cytology section,. past pathology information, imaging studies, or clinical or operative. findings. Pathology stage is only a component to be considered in determining. the clinical stage, and should not be confused with nor substituted for it. The exact operative procedure is available in the surgeon's operative report. DIAGNOSIS: A. OMENTUM (RESECTION) : INVOLVED BY HIGH GRADE PAPILLARY SEROUS ADENOCARCINOMA. B. UTERUS, CERVIX, BILATERAL FALLOPIAN TUBES AND OVARIES (TOTAL HYSTERECTOMY. AND BILATERAL SALPINGO-OOPHORECTOMY) : LEFT OVARY: TYPE: PAPILLARY SEROUS ADENOCARCINOMA. SEE NOTE. TUMOR GRADE: HIGH GRADE. TUMOR SIZE: 4.1 X 3.2 X 2.5 CM. SEROSA: DISRUPTED CAPSULE WITH TUMOR PRESENT MOSTLY ON SURFACE, BUT ALSO. WITHIN PARENCHYMA. SEE NOTE. UTERUS: CERVIX: NO DIAGNOSTIC ABNORMALITY. ENDOMETRIUM: ATROPHIC. LEFT FALLOPIAN TUBE: ACUTE SALPINGITIS AND SEROSITIS. RIGHT OVARY SURFACE SEROSAL ADHESIONS AND MESOTHELIAL HYPERPLASIA WITH. DETACHED FRAGMENTS OF CARCINOMA. SPECIMENS WITH METASTATIC/IMPLANTED TUMOR: RIGHT FALLOPIAN TUBE, LEFT. PARAMETRIUM, MYOMETRIUM AND SEROSA. NOTE: The tumor seen in the left ovary involves predominantly the ovarian. surface with only limited parenchymal involvement. Per clinical history, the. bulk of this tumor is present within the peritoneum/omentum. According to. criteria, a tumor mass greater than 5 mm involving the ovarian parenchyma. should be staged as an ovarian primary, which is the case in this material. Having said that, we suspect that in this particular case, a peritoneal origin. is more likely. Clinical correlation is highly recommended. C. LEFT GUTTER (RESECTION) : INVOLVED BY HIGH GRADE PAPILLARY SEROUS ADENOCARCINOMA. D. OMENTUM #2 (RESECTION) : INVOLVED BY HIGH GRADE PAPILLARY SEROUS ADENOCARCINOMA. E. SMALL BOWEL NODULE (RESECTION) : INVOLVED BY HIGH GRADE PAPILLARY SEROUS ADENOCARCINOMA. I certify that I personally conducted the diagnostic evaluation of the above. specimen (s) and have rendered the above diagnosis (es). Attending MD:"
    add_sentence_sizes(test, debug_mode=True)