from fire import Fire

def main(i, jobs_file, checkpoint_path=None):
	with open(jobs_file, 'r') as file:
		lines = file.readlines()
		command = lines[i]

	if checkpoint_path is not None:
		command = command + f' --logdir={checkpoint_path}'
	print(command)

if __name__ == '__main__':
	Fire(main)