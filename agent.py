import torch
import os
import random
import numpy as np
import argparse
from collections import deque
from main import GraSnake, ROZMIAR_BLOKU
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    # Dodajemy start_eps i lr jako argumenty z domyślnymi wartościami
    def __init__(self, start_eps=300, lr=0.001):
        self.n_games = 0
        self.epsilon = 0
        self.start_eps = start_eps  # Zapisujemy wartość z suwaka do pamięci agenta
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        # Inicjalizacja modelu
        self.model = Linear_QNet(11, 256, 3)

        # Przekazujemy nasze nowe LR (z suwaka) do trenera!
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
        # Wąż zapisuje wspomnienie do notatnika (max 100,000 wspomnień)
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        # "Sen" węża. Kiedy zginie, analizuje do 1000 losowych wspomnień naraz
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        # Nauka na bieżąco, klatka po klatce
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # Tuta wchodzi wartość z suwaka!
        self.epsilon = self.start_eps - self.n_games
        final_move = [0, 0, 0]

        # Na początku gry (epsilon > 0) wąż wykonuje losowe ruchy, żeby "wyczuć" fizykę świata
        if random.randint(0, 400) < self.epsilon or random.randint(0, 100) < 2:
            move = random.randint(0, 2)
            final_move[move] = 1
        # Potem zaczyna ufać swojej sztucznej inteligencji
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)  # Pytamy mózg o decyzję!
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


# === GŁÓWNA PĘTLA TRENINGOWA ===
def train(start_eps, lr, load_path, save_name):
    historia_wynikow = []
    historia_srednich = []
    calkowity_wynik = 0
    record = 0

    agent = Agent(start_eps=start_eps, lr=lr)
    gra = GraSnake()

    # 1. LOGIKA WCZYTYWANIA: Ładujemy tylko, jeśli podano konkretną ścieżkę
    if load_path and os.path.exists(load_path):
        agent.model.load_state_dict(torch.load(load_path))
        print(f"Kontynuuję naukę na bazie: {load_path}")
    else:
        print("Brak pliku bazowego. Tworzę czysty mózg od zera!")

    # ... reszta kodu zostaje bez zmian, aż do momentu bicia rekordu ...

    print("Rozpoczynam trening AI...")

    while True:
        # 1. Zobacz co się dzieje
        state_old = agent.get_state(gra)

        # 2. Wybierz ruch
        final_move = agent.get_action(state_old)

        # 3. Wykonaj ruch i sprawdź efekty (Nagroda)
        reward, done, score = gra.play_step(final_move)
        state_new = agent.get_state(gra)

        # 4. Trenuj na gorąco (Krótka pamięć)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # 5. Zapisz wspomnienie na później
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:  # Gdy wąż zginie
            gra.reset()
            agent.n_games += 1

            # Trenuj w nocy (Długa pamięć - przetwarzanie tysiąca zdarzeń)
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save(file_name=save_name)

            print(f'Gra: {agent.n_games} | Wynik: {score} | Rekord: {record}')

            # === NOWY KOD - WYKRES ===
            historia_wynikow.append(score)
            calkowity_wynik += score
            srednia = calkowity_wynik / agent.n_games
            historia_srednich.append(srednia)

            # Odpalamy rysowanie z pliku helper.py!
            plot(historia_wynikow, historia_srednich)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trenowanie AI Snake')
    parser.add_argument('--eps', type=int, default=300, help='Faza losowości')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')

    # NOWE ARGUMENTY
    parser.add_argument('--load_path', type=str, default='', help='Ścieżka do wczytania')
    parser.add_argument('--save_name', type=str, default='model.pth', help='Nazwa do zapisu')

    args = parser.parse_args()

    print(f"--- TRENING: EPS: {args.eps} | LR: {args.lr} | ZAPIS DO: {args.save_name} ---")

    train(start_eps=args.eps, lr=args.lr, load_path=args.load_path, save_name=args.save_name)