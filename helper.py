import matplotlib.pyplot as plt
from IPython import display

# Włączamy tryb interaktywny dla wykresu
plt.ion()


def plot(wyniki, srednie_wyniki):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()  # Czyścimy stary wykres

    # Konfiguracja wyglądu
    plt.title('Trenowanie Węża...')
    plt.xlabel('Liczba Gier')
    plt.ylabel('Wynik')

    # Rysowanie dwóch linii (niebieska i pomarańczowa)
    plt.plot(wyniki, label='Pojedynczy wynik')
    plt.plot(srednie_wyniki, label='Średnia z wszystkich gier')

    plt.ylim(ymin=0)  # Wykres zaczyna się od zera

    # Dodanie cyferek na samym końcu linii
    plt.text(len(wyniki) - 1, wyniki[-1], str(wyniki[-1]))
    plt.text(len(srednie_wyniki) - 1, srednie_wyniki[-1], str(srednie_wyniki[-1]))

    plt.legend()
    plt.show(block=False)
    plt.pause(0.1)  # Dajemy systemowi ułamek sekundy na wyrysowanie zmian