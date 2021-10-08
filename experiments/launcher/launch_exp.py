import yaml
from fire import Fire
import uuid
from itertools import product
import subprocess
import wandb
from collections import namedtuple
Condition = namedtuple("Condition", ["key", "value"])

yml_counter = 0

def gen_yaml_files(tmp_dir, name, parameters):
	global yml_counter
	param_prod = parse_params_list(tmp_dir, name, parameters)
	ds = [dict(x) for x in param_prod]
	file_names = []
	for d in ds:
		file_name = f'{tmp_dir}/{name}_{yml_counter}.yml'
		yml_counter += 1
		file_names.append(file_name)
		with open(file_name, 'w') as file:
			yaml.dump(d, file)
	print(f'Saving {len(ds)} temp yaml files')
	return file_names

def is_valid(param_list):
	"""param_list is a list of tuples [(key, value, condition), ...]"""
	conds = [x[2] for x in param_list]
	for cond in conds:
		if cond is not None:
			for x in param_list:
				if x[0] == cond.key:
					if x[1] != cond.value:
						return False
	return True

def parse_params_list(tmp_dir, name, parameters):
	param_list = []
	for param_name in parameters:
		param_list.append(parse_param(tmp_dir, name, param_name, parameters[param_name]))
	param_prod = list(product(*param_list))
	# param_prod = filter(is_valid, param_prod)
	return param_prod

def parse_param(tmp_dir, name, param_name, v):
	if isinstance(v, dict):
		if 'value' in v:
			values = [v['value']]
		elif 'values' in v:
			values = v['values']
		elif 'yaml' in v:
			values = gen_yaml_files(tmp_dir, name, v['yaml'])
		elif 'dict' in v:
			# BEHAVIOR ONLY DEFINED FOR YAML FILES
			param_prod = parse_params_list(tmp_dir, name, v['dict'])
			values = [dict(x) for x in param_prod]

		if 'prefix' in v:
			values = [v['prefix'] + val for val in values]
	else:
		values = [v]
	# elif 'if' in v:
	# 	print(v)
	# 	values
	# 	conds = v['condition']
	# 	key = cond['parameter']
	# 	value = cond['equals']
	# 	cond = Condition(key=key, value=value)

	return list(map(lambda x: (param_name, x), values))


def main(config_file, tmp_dir='experiments/launcher/tmp', cluster='q'):
	with open(config_file, 'r') as file:
		config = yaml.safe_load(file)
		command = config['command']
		entity = config['entity']
		project = config['project']

		name = config['name'] + '-' + str(uuid.uuid4())

		# these params are entered as command line arguments
		# TODO: yml global counter
		parameter_sets = filter(lambda x: x not in ['command', 'entity', 'project', 'name'], config.keys())

		commands = []
		for p_key in parameter_sets:

			parameters = config[p_key]
			
			param_prod = parse_params_list(tmp_dir, name, parameters)
			param_prod = [map(lambda x: f'--{x[0]} {x[1]}', p) for p in param_prod]
			
			commands += [f'{command} {" ".join(p)}' for p in param_prod]

		print(commands)

		jobs_file = tmp_dir + '/' + name
		with open(jobs_file, 'w') as file:
			file.write('\n'.join(commands))

		if cluster == 'q':
			command = f'sbatch --array=0-{len(commands) - 1} experiments/launcher/bash_launcher_q {jobs_file} {name}'
		elif cluster == 'v':
			command = f'sbatch --array=0-{len(commands) - 1} experiments/launcher/bash_launcher_v {jobs_file} {name}'
		elif cluster == 'v_deadline':
			command = f'sbatch --array=0-{len(commands) - 1} experiments/launcher/bash_launcher_v_deadline {jobs_file} {name}'

		print(f'Running command: {command}')

		process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()
		print(output, error)

		print(f'GROUP NAME: {name}')

		print(f'Wandb link: https://wandb.ai/{entity}/{project}/groups/{name}')

if __name__ == '__main__':
	Fire(main)