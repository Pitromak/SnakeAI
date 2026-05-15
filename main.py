import pygame
import random

pygame.init()
pygame.font.init()

# 1. Konfiguracja kolorów
BIAŁY = (255, 255, 255)
CZERWONY = (200, 0, 0)
ZIELONY = (0, 255, 0)
CZARNY = (0, 0, 0)
SZARY = (50, 50, 50)

# 2. Ustawienia wymiarów (Logika gry)
SZEROKOSC = 640
WYSOKOSC = 480
ROZMIAR_BLOKU = 20

# 3. Ustawienia okna (Renderowanie)
MARGIN_GORA = 60
MARGIN_BOKI = 30

SZEROKOSC_OKNA = SZEROKOSC + 2 * MARGIN_BOKI
WYSOKOSC_OKNA = WYSOKOSC + MARGIN_GORA + MARGIN_BOKI


class GraSnake:
    def __init__(self):
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
        self.licznik_klatek = 0

    def _postaw_jedzenie(self):
        x = random.randint(0, (SZEROKOSC - ROZMIAR_BLOKU) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
        y = random.randint(0, (WYSOKOSC - ROZMIAR_BLOKU) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
        self.jedzenie = [x, y]
        if self.jedzenie in self.waz:
            self._postaw_jedzenie()

    def play_step(self, akcja):
        self.licznik_klatek += 1
        odleglosc_stara = abs(self.glowa[0] - self.jedzenie[0]) + abs(self.glowa[1] - self.jedzenie[1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        kierunki_zegara = ['PRAWO', 'DOL', 'LEWO', 'GORA']
        idx = kierunki_zegara.index(self.kierunek)

        if akcja[0] == 1:
            nowy_kierunek = kierunki_zegara[idx]
        elif akcja[1] == 1:
            nowy_kierunek = kierunki_zegara[(idx + 1) % 4]
        else:
            nowy_kierunek = kierunki_zegara[(idx - 1) % 4]

        self.kierunek = nowy_kierunek

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
        odleglosc_nowa = abs(self.glowa[0] - self.jedzenie[0]) + abs(self.glowa[1] - self.jedzenie[1])

        if odleglosc_nowa < odleglosc_stara:
            nagroda = 1
        else:
            nagroda = -1

        self.waz.insert(0, self.glowa.copy())

        game_over = False
        if self.is_collision() or self.licznik_klatek > 100 * len(self.waz):
            game_over = True
            nagroda = -10
            return nagroda, game_over, self.wynik

        if self.glowa == self.jedzenie:
            self.wynik += 1
            nagroda = 10
            self._postaw_jedzenie()
            self.licznik_klatek = 0
        else:
            self.waz.pop()

        self.display.fill(SZARY)
        pygame.draw.rect(self.display, CZARNY, [MARGIN_BOKI, MARGIN_GORA, SZEROKOSC, WYSOKOSC])

        for segment in self.waz:
            pygame.draw.rect(self.display, ZIELONY,
                             pygame.Rect(segment[0] + MARGIN_BOKI, segment[1] + MARGIN_GORA, ROZMIAR_BLOKU,
                                         ROZMIAR_BLOKU))

        pygame.draw.rect(self.display, CZERWONY,
                         pygame.Rect(self.jedzenie[0] + MARGIN_BOKI, self.jedzenie[1] + MARGIN_GORA, ROZMIAR_BLOKU,
                                     ROZMIAR_BLOKU))

        tekst_wyniku = self.czcionka.render(f'Wynik: {self.wynik}', True, BIAŁY)
        self.display.blit(tekst_wyniku, [MARGIN_BOKI, 15])

        pygame.display.flip()

        return nagroda, game_over, self.wynik

    def is_collision(self, punkt=None):
        if punkt is None:
            punkt = self.glowa

        if punkt[0] > SZEROKOSC - ROZMIAR_BLOKU or punkt[0] < 0 or punkt[1] > WYSOKOSC - ROZMIAR_BLOKU or punkt[1] < 0:
            return True

        if punkt in self.waz[1:]:
            return True

        return False