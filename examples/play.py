from fire import Fire
import pygame

from lata.models.cat_vae import ActionForwardModel, CatVAE
from lata.datasets.chunk_dataset import ChunkDataset
import torch
import wandb
import numpy as np
from PIL import Image
import PIL

def main(run_path, dataset_path, window_size, fps):
	wandb.init(project='blast', entity='model-pretraining', config={}, job_type='vis_gen', mode='offline')

	config = wandb.config
	agnt = agent.Agent(config, obs_space, act_space, step)
	
	model_h = wandb.restore('variables.pkl', run_path=run_path)
	action_model.load_state_dict(torch.load(model_h.name, map_location=torch.device(device)))

	model.eval()

	keymap = {
		pygame.K_a: 4,
		pygame.K_d: 3,
		pygame.K_w: 2,
		pygame.K_s: 5,
		pygame.K_SPACE: 1
	}

	s = test_dataset[0][0][0].unsqueeze(0).unsqueeze(0).to(device=device).float()
	hidden = None

	pygame.init()
	screen = pygame.display.set_mode([window_size, window_size])
	clock = pygame.time.Clock()
	running = True

	while running:

		action = None
		pygame.event.pump()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				running = False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
				s = test_dataset[0][0][0].unsqueeze(0).unsqueeze(0).to(device=device).float()
				hidden = None
			elif event.type == pygame.KEYDOWN and event.key in keymap.keys():
				action = keymap[event.key]

		if action is None:
			pressed = pygame.key.get_pressed()
			for key, action in keymap.items():
				if pressed[key]:
					break
			else:
				action = 0

		with torch.no_grad():
			s, hidden = action_model.pred_frame(s, action, hidden)
		s_np = s.numpy()[0][0]
		s_np = (s_np * 255).astype(np.uint8)
		s_np = np.moveaxis(s_np, 0, -1)
		s_np = np.moveaxis(s_np, 0, 1)
		s_np = np.array(Image.fromarray(s_np).resize((window_size, window_size), resample=PIL.Image.NEAREST))

		surface = pygame.surfarray.make_surface(s_np)
		screen.blit(surface, (0, 0))
		pygame.display.flip()
		clock.tick(fps)

	pygame.quit()

Fire(main)