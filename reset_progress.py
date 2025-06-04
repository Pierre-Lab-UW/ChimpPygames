monkeys = ["GROUP", "TestChip"]

for monkey in monkeys:
    filepath_to_task = "_progress/"+monkey+"/task-ix.txt"
    filepath_to_progress = "_progress/"+monkey+"/progress_to_criterion.txt"
    filepath_to_progress = "_progress/"+monkey+"/progress_to_criterion.txt"
    filepath_to_trials = "_progress/"+monkey+"/progress_to_trials.txt"

    
    with open(filepath_to_task, 'w') as f:
        f.write(str(0))
    with open(filepath_to_progress, 'w') as f:
        f.truncate(0)
    with open(filepath_to_trials, 'w') as f:
        f.truncate(0)
