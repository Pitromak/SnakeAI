import torch
import pygame
import argparse
from main import GraSnake
from agent import Agent


def play(sciezka_modelu):
    print("Ładowanie mistrza AI...")

    # Inicjujemy grę i naszego Agenta (potrzebujemy go, żeby użyć jego "radaru" get_state)
    gra = GraSnake()
    agent = Agent()

    # 1. ŁADOWANIE MÓZGU
    # Wczytujemy wagi (połączenia neuronowe) z zapisanego pliku na dysku.
    # Używamy map_location='cpu', żeby uniknąć błędów, jeśli trenowałeś na innym sprzęcie.
    try:
        agent.model.load_state_dict(torch.load(sciezka_modelu, map_location='cpu'))
        print(f"Wczytano z: {sciezka_modelu}")
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku: {sciezka_modelu}")
        return

    # 2. TRYB EWALUACJI
    # Zamrażamy model. Mówimy mu: "Koniec nauki, teraz tylko grasz".
    agent.model.eval()

    print("Zaczynamy pokaz! (Zamknij okno gry krzyżykiem, aby przerwać)")

    while True:
        # Zwalniamy grę do ludzkiej prędkości (ok. 15-20 klatek na sekundę),
        # żeby móc podziwiać manewry bez konieczności odblokowywania self.clock w main.py
        pygame.time.delay(60)

        # 3. ZOBACZ CO SIĘ DZIEJE
        # Wąż odczytuje stan (gdzie są ściany, gdzie jedzenie)
        stan = agent.get_state(gra)
        stan_tensor = torch.tensor(stan, dtype=torch.float)

        # 4. PODEJMIJ DECYZJĘ (Czysty instynkt, 0 losowości)
        # Zamiast funkcji get_action z agenta, pytamy mózg bezpośrednio
        decyzja = agent.model(stan_tensor)

        # Wybieramy ruch z najwyższą wartością (pewnością)
        najlepszy_ruch = torch.argmax(decyzja).item()

        akcja = [0, 0, 0]
        akcja[najlepszy_ruch] = 1

        # 5. WYKONAJ RUCH W GRZE
        nagroda, koniec, wynik = gra.play_step(akcja)

        # 6. RESET PO ŚMIERCI (lub po zablokowaniu się)
        if koniec:
            print(f'Koniec gry! Twój agent zdobył: {wynik} punktów.')
            gra.reset()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pokaz AI Snake')
    parser.add_argument('--model_path', type=str, default='model/model.pth', help='Ścieżka do wytrenowanego modelu')
    args = parser.parse_args()

    # Odpalamy grę z przekazaną ścieżką
    play(sciezka_modelu=args.model_path)