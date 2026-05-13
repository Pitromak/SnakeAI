import pygame
import random

pygame.init()
pygame.font.init()

# 1. Konfiguracja kolorów
BIAŁY = (255, 255, 255)
CZERWONY = (200, 0, 0)
ZIELONY = (0, 255, 0)
CZARNY = (0, 0, 0)
SZARY = (50, 50, 50)  # Nowy kolor na obramowanie

# 2. Ustawienia wymiarów (Logika gry)
SZEROKOSC = 640  # Rozmiar samej czarnej planszy, po której biega wąż
WYSOKOSC = 480
ROZMIAR_BLOKU = 20
PREDKOSC = 15

# 3. Ustawienia okna (Renderowanie)
MARGIN_GORA = 60  # Więcej miejsca na górze na napis "Wynik"
MARGIN_BOKI = 30  # Mniejsze marginesy po bokach i na dole

# Całkowity rozmiar okna to plansza + marginesy
SZEROKOSC_OKNA = SZEROKOSC + 2 * MARGIN_BOKI
WYSOKOSC_OKNA = WYSOKOSC + MARGIN_GORA + MARGIN_BOKI


class GraSnake:
    def __init__(self):
        # Tworzymy powiększone okno programu
        self.display = pygame.display.set_mode((SZEROKOSC_OKNA, WYSOKOSC_OKNA))
        pygame.display.set_caption('Snake dla AI')
        self.clock = pygame.time.Clock()
        self.czcionka = pygame.font.SysFont('arial', 25)
        self.reset()

    def reset(self):
        self.kierunek = 'PRAWO'
        self.glowa = [SZEROKOSC / 2, WYSOKOSC / 2]
        self.waz = [self.glowa.copy(), [self.glowa[0] - ROZMIAR_BLOKU, self.glowa[1]],
                    [self.glowa[0] - (2 * ROZMIAR_BLOKU), self.glowa[1]]]
        self.wynik = 0
        self.jedzenie = None
        self._postaw_jedzenie()

    def _postaw_jedzenie(self):
        x = random.randint(0, (SZEROKOSC - ROZMIAR_BLOKU) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
        y = random.randint(0, (WYSOKOSC - ROZMIAR_BLOKU) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
        self.jedzenie = [x, y]
        if self.jedzenie in self.waz:
            self._postaw_jedzenie()

    def play_step(self):
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
        self.waz.insert(0, self.glowa.copy())

        game_over = False
        # Logika kolizji pozostaje BEZ ZMIAN - wąż dalej myśli, że gra toczy się w oknie 640x480
        if (self.glowa[0] > SZEROKOSC - ROZMIAR_BLOKU or self.glowa[0] < 0 or
                self.glowa[1] > WYSOKOSC - ROZMIAR_BLOKU or self.glowa[1] < 0 or
                self.glowa in self.waz[1:]):
            game_over = True
            return game_over, self.wynik

        if self.glowa == self.jedzenie:
            self.wynik += 1
            self._postaw_jedzenie()
        else:
            self.waz.pop()

        # ==========================================
        # NOWE RYSOWANIE Z MARGINESAMI
        # ==========================================

        # 1. Tło całego okna (nasza szara ramka)
        self.display.fill(SZARY)

        # 2. Czarna plansza wewnątrz ramki (przesunięta o marginesy)
        pygame.draw.rect(self.display, CZARNY, [MARGIN_BOKI, MARGIN_GORA, SZEROKOSC, WYSOKOSC])

        # 3. Wąż (przesuwamy rysowanie każdego kawałka o marginesy)
        for segment in self.waz:
            pygame.draw.rect(self.display, ZIELONY,
                             pygame.Rect(segment[0] + MARGIN_BOKI, segment[1] + MARGIN_GORA, ROZMIAR_BLOKU,
                                         ROZMIAR_BLOKU))

        # 4. Jedzenie (przesuwamy rysowanie o marginesy)
        pygame.draw.rect(self.display, CZERWONY,
                         pygame.Rect(self.jedzenie[0] + MARGIN_BOKI, self.jedzenie[1] + MARGIN_GORA, ROZMIAR_BLOKU,
                                     ROZMIAR_BLOKU))

        # 5. Wynik rysujemy na szarym marginesie u góry
        tekst_wyniku = self.czcionka.render(f'Wynik: {self.wynik}', True, BIAŁY)
        self.display.blit(tekst_wyniku, [MARGIN_BOKI, 15])

        pygame.display.flip()
        self.clock.tick(PREDKOSC)

        return game_over, self.wynik


if __name__ == '__main__':
    gra = GraSnake()
    while True:
        koniec, aktualny_wynik = gra.play_step()
        if koniec:
            break

    print('Koniec gry! Twój wynik:', aktualny_wynik)
    pygame.quit()