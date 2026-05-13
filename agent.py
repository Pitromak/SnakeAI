import numpy as np

# Importujemy zmienne z naszej gry
from main import GraSnake, ROZMIAR_BLOKU


class Agent:
    def __init__(self):
        pass  # Tu za chwilę dodamy pamięć i sieć neuronową

    def get_state(self, gra):
        glowa = gra.waz[0]

        # Obliczamy koordynaty pól dookoła głowy węża
        punkt_l = [glowa[0] - ROZMIAR_BLOKU, glowa[1]]
        punkt_p = [glowa[0] + ROZMIAR_BLOKU, glowa[1]]
        punkt_g = [glowa[0], glowa[1] - ROZMIAR_BLOKU]
        punkt_d = [glowa[0], glowa[1] + ROZMIAR_BLOKU]

        # Sprawdzamy aktualny kierunek (zwraca True lub False)
        kier_l = gra.kierunek == 'LEWO'
        kier_p = gra.kierunek == 'PRAWO'
        kier_g = gra.kierunek == 'GORA'
        kier_d = gra.kierunek == 'DOL'

        # Tworzymy naszą 11-elementową ankietę
        stan = [
            # 1. Niebezpieczeństwo na wprost
            (kier_p and gra.is_collision(punkt_p)) or
            (kier_l and gra.is_collision(punkt_l)) or
            (kier_g and gra.is_collision(punkt_g)) or
            (kier_d and gra.is_collision(punkt_d)),

            # 2. Niebezpieczeństwo po prawej stronie węża
            (kier_g and gra.is_collision(punkt_p)) or
            (kier_d and gra.is_collision(punkt_l)) or
            (kier_l and gra.is_collision(punkt_g)) or
            (kier_p and gra.is_collision(punkt_d)),

            # 3. Niebezpieczeństwo po lewej stronie węża
            (kier_d and gra.is_collision(punkt_p)) or
            (kier_g and gra.is_collision(punkt_l)) or
            (kier_p and gra.is_collision(punkt_g)) or
            (kier_l and gra.is_collision(punkt_d)),

            # 4. Aktualny kierunek
            kier_l,
            kier_p,
            kier_g,
            kier_d,

            # 5. Położenie jedzenia (względem głowy)
            gra.jedzenie[0] < gra.glowa[0],  # Jedzenie po lewej
            gra.jedzenie[0] > gra.glowa[0],  # Jedzenie po prawej
            gra.jedzenie[1] < gra.glowa[1],  # Jedzenie wyżej
            gra.jedzenie[1] > gra.glowa[1]  # Jedzenie niżej
        ]

        # Konwertujemy listę Prawda/Fałsz na jedynki i zera dla PyTorcha
        return np.array(stan, dtype=int)