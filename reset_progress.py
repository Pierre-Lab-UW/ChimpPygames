monkeys = ["GROUP", "Testchip"]

for monkey in monkeys:
    filepath_to_task = "_progress/"+monkey+"/task-ix.txt"
    filepath_to_progress = "_progress/"+monkey+"/progress_to_criterion.txt"
    
    with open(filepath_to_task, 'w') as f:
        f.write(str(0))
    with open(filepath_to_progress, 'w') as f:
        f.truncate(0)