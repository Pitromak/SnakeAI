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
#PREDKOSC = 500      to + linijka 136

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
        self.licznik_klatek = 0

    def _postaw_jedzenie(self):
        x = random.randint(0, (SZEROKOSC - ROZMIAR_BLOKU) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
        y = random.randint(0, (WYSOKOSC - ROZMIAR_BLOKU) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
        self.jedzenie = [x, y]
        if self.jedzenie in self.waz:
            self._postaw_jedzenie()

    def play_step(self, akcja):
        self.licznik_klatek += 1

        # Mierzymy starą odległość (Odległość Manhattan)
        odleglosc_stara = abs(self.glowa[0] - self.jedzenie[0]) + abs(self.glowa[1] - self.jedzenie[1])

        # 1. Zostawiamy tylko awaryjne zamykanie okna na krzyżyk
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. Tłumaczymy decyzję AI na nowy kierunek
        # akcja to tablica [Prosto, W prawo, W lewo] np. [0, 1, 0]
        kierunki_zegara = ['PRAWO', 'DOL', 'LEWO', 'GORA']
        idx = kierunki_zegara.index(self.kierunek)  # Sprawdzamy gdzie patrzymy teraz

        if akcja[0] == 1:
            nowy_kierunek = kierunki_zegara[idx]  # [1,0,0] -> Jedź prosto
        elif akcja[1] == 1:
            nowy_kierunek = kierunki_zegara[(idx + 1) % 4]  # [0,1,0] -> Skręt w prawo
        else:  # akcja[2] == 1
            nowy_kierunek = kierunki_zegara[(idx - 1) % 4]  # [0,0,1] -> Skręt w lewo

        self.kierunek = nowy_kierunek

        # 3. Przesunięcie głowy (tu stary kod zostaje bez zmian)
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
        # 2. Mierzymy nową odległość i oceniamy ruch
        odleglosc_nowa = abs(self.glowa[0] - self.jedzenie[0]) + abs(self.glowa[1] - self.jedzenie[1])

        if odleglosc_nowa < odleglosc_stara:
            nagroda = 1  # Ciepło! Zbliżasz się do celu.
        else:
            nagroda = -1  # Zimno! Oddalasz się od celu.

        self.waz.insert(0, self.glowa.copy())

        # Nowe wywołanie kolizji w play_step
        game_over = False
        # NOWY KOD - Wąż umiera jeśli uderzy w ścianę,
        # ALBO jeśli zrobi więcej ruchów niż 100 * długość jego ciała bez jedzenia
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
        #self.clock.tick(PREDKOSC)

        return nagroda, game_over, self.wynik

    def is_collision(self, punkt=None):
        if punkt is None:
            punkt = self.glowa

        # 1. Uderzenie w ściany
        if punkt[0] > SZEROKOSC - ROZMIAR_BLOKU or punkt[0] < 0 or punkt[1] > WYSOKOSC - ROZMIAR_BLOKU or punkt[1] < 0:
            return True

        # 2. Uderzenie we własny ogon
        if punkt in self.waz[1:]:
            return True

        return False


if __name__ == '__main__':
    gra = GraSnake()
    while True:
        # Wymuszamy na wężu ciągłą jazdę prosto: [Prosto, Prawo, Lewo]
        akcja_testowa = [1, 0, 0]

        # Pamiętaj, że teraz odbieramy 3 rzeczy!
        nagroda, koniec, aktualny_wynik = gra.play_step(akcja_testowa)

        if koniec:
            break

    print('Koniec gry! Twój wynik:', aktualny_wynik)
    pygame.quit()