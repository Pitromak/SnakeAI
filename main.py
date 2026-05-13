import pygame
import random

pygame.init()
pygame.font.init()

# 1. Konfiguracja kolorów i okna
BIAŁY = (255, 255, 255)
CZERWONY = (200, 0, 0)
ZIELONY = (0, 255, 0)
CZARNY = (0, 0, 0)

SZEROKOSC = 640
WYSOKOSC = 480
ROZMIAR_BLOKU = 20
PREDKOSC = 15  # Im więcej, tym gra działa szybciej


class GraSnake:
    def __init__(self):
        # Ta funkcja odpala się raz, gdy tworzymy grę
        self.display = pygame.display.set_mode((SZEROKOSC, WYSOKOSC))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        #(Czcionka systemowa Arial, rozmiar 25)
        self.czcionka = pygame.font.SysFont('arial', 25)
        self.reset()  # Ustawiamy węża na startowej pozycji

    def reset(self):
        # Resetuje stan gry (przydatne gdy AI zginie i zaczyna od nowa)
        self.kierunek = 'PRAWO'
        self.glowa = [SZEROKOSC / 2, WYSOKOSC / 2]
        # Wąż zaczyna z długością 3 kratek
        self.waz = [self.glowa.copy(), [self.glowa[0] - ROZMIAR_BLOKU, self.glowa[1]],
                    [self.glowa[0] - (2 * ROZMIAR_BLOKU), self.glowa[1]]]
        self.wynik = 0
        self.jedzenie = None
        self._postaw_jedzenie()

    def _postaw_jedzenie(self):
        # Losuje pozycję jabłka na siatce
        x = random.randint(0, (SZEROKOSC - ROZMIAR_BLOKU) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
        y = random.randint(0, (WYSOKOSC - ROZMIAR_BLOKU) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
        self.jedzenie = [x, y]
        # Jeśli jedzenie zrespiło się w wężu, losuj jeszcze raz
        if self.jedzenie in self.waz:
            self._postaw_jedzenie()

    def play_step(self):
        # 1. Pobieranie ruchu od gracza (później tu wpniemy komendy od AI)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.kierunek != 'PRAWO':
                    self.kierunek = 'LEWO'
                elif event.key == pygame.K_RIGHT and self.kierunek != 'LEWO':
                    self.kierunek = 'PRAWO'
                elif event.key == pygame.K_UP and self.kierunek != 'DOL':
                    self.kierunek = 'GORA'
                elif event.key == pygame.K_DOWN and self.kierunek != 'GORA':
                    self.kierunek = 'DOL'

        # 2. Przesunięcie głowy
        x = self.glowa[0]
        y = self.glowa[1]
        if self.kierunek == 'PRAWO':
            x += ROZMIAR_BLOKU
        elif self.kierunek == 'LEWO':
            x -= ROZMIAR_BLOKU
        elif self.kierunek == 'DOL':
            y += ROZMIAR_BLOKU
        elif self.kierunek == 'GORA':
            y -= ROZMIAR_BLOKU

        self.glowa = [x, y]
        self.waz.insert(0, self.glowa.copy())  # Dodajemy nową głowę na przód węża

        # 3. Sprawdzenie czy wąż zginął
        game_over = False
        # Jeśli uderzył w ścianę LUB w samego siebie
        if (self.glowa[0] > SZEROKOSC - ROZMIAR_BLOKU or self.glowa[0] < 0 or
                self.glowa[1] > WYSOKOSC - ROZMIAR_BLOKU or self.glowa[1] < 0 or
                self.glowa in self.waz[1:]):
            game_over = True
            return game_over, self.wynik

        # 4. Sprawdzanie czy zjadł jabłko
        if self.glowa == self.jedzenie:
            self.wynik += 1
            self._postaw_jedzenie()
        else:
            self.waz.pop()  # Usuwamy ogon, jeśli wąż tylko się przesunął (a nie zjadł)

        # 5. Rysowanie wszystkiego na ekranie
        self.display.fill(CZARNY)
        for segment in self.waz:
            pygame.draw.rect(self.display, ZIELONY, pygame.Rect(segment[0], segment[1], ROZMIAR_BLOKU, ROZMIAR_BLOKU))
        pygame.draw.rect(self.display, CZERWONY,
                         pygame.Rect(self.jedzenie[0], self.jedzenie[1], ROZMIAR_BLOKU, ROZMIAR_BLOKU))

        # --- RYSOWANIE WYNIKU ---
        tekst_wyniku = self.czcionka.render(f'Wynik: {self.wynik}', True, BIAŁY)
        # blit nakleja tekst_wyniku na główny ekran na podanych koordynatach [x=0, y=0]
        self.display.blit(tekst_wyniku, [0, 0])
        # -----------------------------------

        pygame.display.flip()
        self.clock.tick(PREDKOSC)

        return game_over, self.wynik


# GŁÓWNA PĘTLA
if __name__ == '__main__':
    gra = GraSnake()

    # Pętla działa tak długo, aż game_over nie zmieni się na True
    while True:
        koniec, aktualny_wynik = gra.play_step()
        if koniec:
            break

    print('Koniec gry! Twój wynik:', aktualny_wynik)
    pygame.quit()