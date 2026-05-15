import torch
import random
import numpy as np
from collections import deque
from main import GraSnake, ROZMIAR_BLOKU
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000

class Agent:
    def __init__(self, start_eps=300, lr=0.001):
        self.n_games = 0
        self.epsilon = 0
        self.start_eps = start_eps
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        # Inicjalizacja modelu
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=lr, gamma=self.gamma)

    def get_state(self, gra):
        glowa = gra.waz[0]
        punkt_l = [glowa[0] - ROZMIAR_BLOKU, glowa[1]]
        punkt_p = [glowa[0] + ROZMIAR_BLOKU, glowa[1]]
        punkt_g = [glowa[0], glowa[1] - ROZMIAR_BLOKU]
        punkt_d = [glowa[0], glowa[1] + ROZMIAR_BLOKU]

        kier_l = gra.kierunek == 'LEWO'
        kier_p = gra.kierunek == 'PRAWO'
        kier_g = gra.kierunek == 'GORA'
        kier_d = gra.kierunek == 'DOL'

        stan = [
            # Niebezpieczeństwo na wprost
            (kier_p and gra.is_collision(punkt_p)) or (kier_l and gra.is_collision(punkt_l)) or (
                        kier_g and gra.is_collision(punkt_g)) or (kier_d and gra.is_collision(punkt_d)),
            # Niebezpieczeństwo po prawej
            (kier_g and gra.is_collision(punkt_p)) or (kier_d and gra.is_collision(punkt_l)) or (
                        kier_l and gra.is_collision(punkt_g)) or (kier_p and gra.is_collision(punkt_d)),
            # Niebezpieczeństwo po lewej
            (kier_d and gra.is_collision(punkt_p)) or (kier_g and gra.is_collision(punkt_l)) or (
                        kier_p and gra.is_collision(punkt_g)) or (kier_l and gra.is_collision(punkt_d)),

            kier_l, kier_p, kier_g, kier_d,  # Aktualny kierunek

            gra.jedzenie[0] < gra.glowa[0],  # Jedzenie po lewej
            gra.jedzenie[0] > gra.glowa[0],  # Jedzenie po prawej
            gra.jedzenie[1] < gra.glowa[1],  # Jedzenie wyżej
            gra.jedzenie[1] > gra.glowa[1]  # Jedzenie niżej
        ]
        return np.array(stan, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = self.start_eps - self.n_games
        final_move = [0, 0, 0]

        if random.randint(0, 400) < self.epsilon or random.randint(0, 100) < 2:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move