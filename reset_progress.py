import csv
import os

def create_files(subdirectory):
        # Dictionary of files and their default contents
        files_with_contents = {
            "progress_to_criterion.txt": "",
            "progress_to_trial.txt": "",
            "progress_to_trials.txt": "0",
            "set-ix.txt": "0",
            "set-neg.txt": "grey___image357.jpg",
            "set-pos.txt": "pink___image811.jpg",
            "set-timestamp.txt": "1729541129.171029",
            "side_tracking.txt": "",
            "task-ix.txt": "0",
            "TI-phase.txt": "learning",
            "TI-set-ix.txt": "1",
            "TI-set-neg.txt": "pink___image1233.jpg",
            "TI-set-pos.txt": "white___image815.jpg",
            "TI-set-timestamp.txt": "",
            "TouchTrain-size.txt": "150"
        }

        print('resetting progress files for '+str(subdirectory)+'...')
        # Create the subdirectory if it doesn't exist
        os.makedirs(os.path.join("_progress",subdirectory), exist_ok=True)

        # Create each file with default content
        for file_name, content in files_with_contents.items():
            file_path = os.path.join(os.path.join("_progress", subdirectory), file_name)
            with open(file_path, 'w') as f:
                f.write(content)
        print('sucessfully reset progress files for '+str(subdirectory)+'.')

monkeys = []
with open('primate_params.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if row:  # Make sure the row is not empty
            monkeys.append(row[0])

monkeys = monkeys[1:]




for monkey in monkeys:
    create_files(monkey)
