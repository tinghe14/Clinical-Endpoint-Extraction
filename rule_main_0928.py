import subprocess
import argparse



# Define the sets of values for each argument
STOP_THEN_MATCH_CHAR_DISTANCE_values = [25] #[25, 30, 35, 40]same #25
MATCH_THEN_STOP_CHAR_DISTANCE_values = [7] #[4, 7, 10]same #7
STOP_WORD_DISTANCE_values = [3] #[3, 5, 7]decrease ~[5]smallest -> [1,2,3] #[2,3]
PRECEDING_WORD_values = [-10] #[-10, -9, -8]decrease -> [-10, -12, -13] #[-10]
FOLLOWING_WORD_values = [1] # [2,4,6,10] decrease -> [] #[1,2]
MODEL = ["own"] # need distance

i = 0 

# Iterate through all combinations of values
for STOP_THEN_MATCH_CHAR_DISTANCE in STOP_THEN_MATCH_CHAR_DISTANCE_values:
    for MATCH_THEN_STOP_CHAR_DISTANCE in MATCH_THEN_STOP_CHAR_DISTANCE_values:
        for STOP_WORD_DISTANCE in STOP_WORD_DISTANCE_values:
            for PRECEDING_WORD in PRECEDING_WORD_values:
                for FOLLOWING_WORD in FOLLOWING_WORD_values:
                    i += 1
                    # Construct the command
                    command = [
                        "python", "/Users/tinghe/Desktop/phd research/NCI_rule/Tumor Size/evaluate_0928.py",
                        f"--MODEL={MODEL}",
                        f"--STOP_THEN_MATCH_CHAR_DISTANCE={STOP_THEN_MATCH_CHAR_DISTANCE}",
                        f"--MATCH_THEN_STOP_CHAR_DISTANCE={MATCH_THEN_STOP_CHAR_DISTANCE}",
                        f"--STOP_WORD_DISTANCE={STOP_WORD_DISTANCE}",
                        f"--PRECEDING_WORD={PRECEDING_WORD}",
                        f"--FOLLOWING_WORD={FOLLOWING_WORD}"
                    ]
                    
                    # Run the command
                    # print(f"Running: {' '.join(command)}")
                    subprocess.run(command)
                    num_exps = len(STOP_THEN_MATCH_CHAR_DISTANCE_values)*len(MATCH_THEN_STOP_CHAR_DISTANCE_values)*len(STOP_WORD_DISTANCE_values)*len(PRECEDING_WORD_values)*len(FOLLOWING_WORD_values)
                    # print(f"{'~'*5}Finished run: {i}/{num_exps}{'~'*5}")
