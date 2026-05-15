import customtkinter as ctk
import os
import threading
import time
import pygame
import torch
import subprocess
import sys
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog

# ZMUSZAMY PYGAME DO DZIAŁANIA W TLE
os.environ["SDL_VIDEODRIVER"] = "dummy"

from main import GraSnake
from agent import Agent


class CentrumDowodzenia(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Snake - Ultimate Command Center")
        self.geometry("1100x750")

        # Flaga do kontrolowania wątku w tle
        self.dziala = False

        # --- GŁÓWNY PODZIAŁ EKRANU ---
        self.grid_columnconfigure(0, weight=1)  # Lewy panel (Zakładki)
        self.grid_columnconfigure(1, weight=2)  # Prawy panel (Gra + Wykres)
        self.grid_rowconfigure(0, weight=1)

        # 1. LEWA STRONA - SYSTEM ZAKŁADEK (Tabview)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tabview.add("🧠 Trening")
        self.tabview.add("🎮 Test")
        self.tabview.add("📦 Zarządzanie")

        self.zbuduj_zakladke_trening()
        self.zbuduj_zakladke_pokaz()
        self.zbuduj_zakladke_zarzadzanie()

        # 2. PRAWA STRONA - WIZUALIZACJE
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=2)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # POKÓJ DLA WĘŻA
        self.game_label = ctk.CTkLabel(self.right_frame, text="System Gotowy. Wybierz tryb.")
        self.game_label.grid(row=0, column=0, pady=(0, 10))

        # POKÓJ DLA WYKRESU
        self.plot_frame = ctk.CTkFrame(self.right_frame, fg_color="#1e1e1e")
        self.plot_frame.grid(row=1, column=0, sticky="nsew")

        self.fig = Figure(figsize=(5, 2), dpi=100, facecolor='#1e1e1e')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.historia_wynikow = []
        self.historia_srednich = []
        self.calkowity_wynik = 0

    # ==========================================
    # BUDOWA ZAKŁADEK
    # ==========================================

    def zbuduj_zakladke_trening(self):
        tab = self.tabview.tab("🧠 Trening")

        ctk.CTkLabel(tab, text="Nazwa nowego modelu:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        self.entry_nazwa = ctk.CTkEntry(tab, placeholder_text="np. mistrz_v1")
        self.entry_nazwa.pack(fill="x", padx=20, pady=(0, 20))

        self.lbl_eps = ctk.CTkLabel(tab, text="Epsilon (Losowość): 80")
        self.lbl_eps.pack(anchor="w", padx=20)
        self.slider_eps = ctk.CTkSlider(tab, from_=0, to=300,
                                        command=lambda v: self.lbl_eps.configure(text=f"Epsilon: {int(v)}"))
        self.slider_eps.set(80)
        self.slider_eps.pack(fill="x", padx=20, pady=(0, 20))

        self.lbl_lr = ctk.CTkLabel(tab, text="Learning Rate: 0.001")
        self.lbl_lr.pack(anchor="w", padx=20)
        self.slider_lr = ctk.CTkSlider(tab, from_=0.0001, to=0.01, number_of_steps=100,
                                       command=lambda v: self.lbl_lr.configure(text=f"LR: {round(v, 4)}"))
        self.slider_lr.set(0.001)
        self.slider_lr.pack(fill="x", padx=20, pady=(0, 30))

        self.btn_start_trening = ctk.CTkButton(tab, text="🚀 START TRENING", fg_color="#28a745", hover_color="#218838",
                                               command=self.start_trening)
        self.btn_start_trening.pack(fill="x", padx=20, pady=5)

        self.btn_stop = ctk.CTkButton(tab, text="🛑 ZATRZYMAJ", fg_color="#dc3545", hover_color="#c82333",
                                      command=self.zatrzymaj_system)
        self.btn_stop.pack(fill="x", padx=20)

    def zbuduj_zakladke_pokaz(self):
        tab = self.tabview.tab("🎮 Test")

        ctk.CTkLabel(tab, text="Tryb Ewaluacji", font=("Arial", 18, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(tab, text="Agent gra na 100% wyuczonych\numiejętności (normalna prędkość).").pack(pady=10)

        self.sciezka_modelu_pokaz = ""
        self.lbl_wybrany_model = ctk.CTkLabel(tab, text="Brak wybranego modelu", text_color="gray")
        self.lbl_wybrany_model.pack(pady=10)

        ctk.CTkButton(tab, text="📁 Wczytaj Model (.pth)", command=self.wybierz_model_do_pokazu).pack(fill="x", padx=20,
                                                                                                     pady=10)

        self.btn_start_pokaz = ctk.CTkButton(tab, text="▶️ ODPAL POKAZ", command=self.start_pokaz)
        self.btn_start_pokaz.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(tab, text="🛑 ZATRZYMAJ", fg_color="#dc3545", hover_color="#c82333",
                      command=self.zatrzymaj_system).pack(fill="x", padx=20)

    def zbuduj_zakladke_zarzadzanie(self):
        tab = self.tabview.tab("📦 Zarządzanie")

        ctk.CTkLabel(tab, text="Eksport do formatu ONNX", font=("Arial", 16, "bold")).pack(pady=(20, 10))

        self.sciezka_in_eksport = ""
        self.sciezka_out_eksport = ""

        self.lbl_eksport_info = ctk.CTkLabel(tab, text="Wybierz plik do konwersji", text_color="gray")
        self.lbl_eksport_info.pack(pady=10)

        ctk.CTkButton(tab, text="📁 Wybierz Model", command=self.wybierz_model_do_eksportu).pack(fill="x", padx=20,
                                                                                                pady=5)
        self.btn_eksport = ctk.CTkButton(tab, text="📦 GENERUJ ONNX", fg_color="#17a2b8", hover_color="#138496",
                                         command=self.uruchom_eksport)
        self.btn_eksport.pack(fill="x", padx=20, pady=15)

    # ==========================================
    # LOGIKA INTERFEJSU
    # ==========================================

    def wybierz_model_do_pokazu(self):
        sciezka = filedialog.askopenfilename(initialdir="./model", title="Wybierz plik modelu",
                                             filetypes=(("Pliki PTH", "*.pth"),))
        if sciezka:
            self.sciezka_modelu_pokaz = sciezka
            self.lbl_wybrany_model.configure(text=os.path.basename(sciezka), text_color="white")

    def wybierz_model_do_eksportu(self):
        sciezka = filedialog.askopenfilename(initialdir="./model", title="Wybierz model do eksportu",
                                             filetypes=(("Pliki PTH", "*.pth"),))
        if sciezka:
            self.sciezka_in_eksport = sciezka
            self.sciezka_out_eksport = sciezka.replace('.pth', '.onnx')
            self.lbl_eksport_info.configure(text=f"Gotowy do eksportu:\n{os.path.basename(self.sciezka_out_eksport)}",
                                            text_color="white")

    def uruchom_eksport(self):
        if not self.sciezka_in_eksport:
            self.lbl_eksport_info.configure(text="BŁĄD: Wybierz model!", text_color="#ff4c4c")
            return

        self.lbl_eksport_info.configure(text="Przetwarzanie...", text_color="#f39c12")
        self.update()

        komenda = [sys.executable, "export.py", "--in_path", self.sciezka_in_eksport, "--out_path",
                   self.sciezka_out_eksport]
        wynik = subprocess.run(komenda)

        if wynik.returncode == 0:
            self.lbl_eksport_info.configure(text="Sukces! Utworzono ONNX.", text_color="#28a745")
        else:
            self.lbl_eksport_info.configure(text="Błąd podczas eksportu.", text_color="#ff4c4c")

    def zatrzymaj_system(self):
        self.dziala = False
        self.game_label.configure(image="", text="System Zatrzymany")

    # ==========================================
    # ZARZĄDZANIE WĄTKAMI I GRĄ
    # ==========================================

    def start_trening(self):
        self.zatrzymaj_system()
        time.sleep(0.1)  # Dajemy chwilę na zamknięcie poprzedniego wątku

        nazwa = self.entry_nazwa.get()
        if not nazwa:
            nazwa = "model_domyslny"

        eps = int(self.slider_eps.get())
        lr = round(self.slider_lr.get(), 4)

        self.dziala = True
        self.historia_wynikow = []
        self.historia_srednich = []
        self.calkowity_wynik = 0

        watek = threading.Thread(target=self.petla_gry, args=("trening", eps, lr, nazwa, None))
        watek.daemon = True
        watek.start()

    def start_pokaz(self):
        if not self.sciezka_modelu_pokaz:
            self.lbl_wybrany_model.configure(text="WYBIERZ MODEL NAJPIERW!", text_color="#ff4c4c")
            return

        self.zatrzymaj_system()
        time.sleep(0.1)

        self.dziala = True
        self.historia_wynikow = []

        watek = threading.Thread(target=self.petla_gry, args=("pokaz", 0, 0, "", self.sciezka_modelu_pokaz))
        watek.daemon = True
        watek.start()

    def petla_gry(self, tryb, eps, lr, nazwa_modelu, sciezka_modelu):
        agent = Agent(start_eps=eps, lr=lr)
        gra = GraSnake()
        record = 0

        # Jeśli tryb pokazu, ładujemy wagi i wymuszamy logikę eksploatacji (brak losowości)
        if tryb == "pokaz" and sciezka_modelu:
            agent.model.load_state_dict(torch.load(sciezka_modelu, map_location='cpu'))
            agent.model.eval()

        while self.dziala:
            stan_stary = agent.get_state(gra)

            if tryb == "pokaz":
                # W trybie pokazu omijamy losowość (epsilon) i od razu pytamy sieć
                stan_tensor = torch.tensor(stan_stary, dtype=torch.float)
                predykcja = agent.model(stan_tensor)
                akcja_idx = torch.argmax(predykcja).item()
                akcja = [0, 0, 0]
                akcja[akcja_idx] = 1
            else:
                akcja = agent.get_action(stan_stary)

            nagroda, koniec, wynik = gra.play_step(akcja)

            if tryb == "trening":
                stan_nowy = agent.get_state(gra)
                agent.train_short_memory(stan_stary, akcja, nagroda, stan_nowy, koniec)
                agent.remember(stan_stary, akcja, nagroda, stan_nowy, koniec)

            # Kradzież klatki do wyświetlenia
            powierzchnia = pygame.display.get_surface()
            if powierzchnia:
                obraz_str = pygame.image.tostring(powierzchnia, "RGB")
                szerokosc, wysokosc = powierzchnia.get_size()
                pil_img = Image.frombytes("RGB", (szerokosc, wysokosc), obraz_str)
                ctk_img = ctk.CTkImage(light_image=pil_img, size=(szerokosc, wysokosc))
                self.after(0, self.aktualizuj_klatke, ctk_img)

            # --- MANIPULACJA CZASEM ---
            if tryb == "pokaz":
                time.sleep(0.05)  # Normalna prędkość (ok. 20 FPS), żebyś mógł to oglądać
            else:
                time.sleep(0.001)  # Prędkość światła dla procesora podczas treningu

            if koniec:
                gra.reset()

                if tryb == "trening":
                    agent.n_games += 1
                    agent.train_long_memory()
                    if wynik > record:
                        record = wynik
                        # Zapisujemy pod nazwą z pola tekstowego
                        if not os.path.exists('model'):
                            os.makedirs('model')
                        agent.model.save(f'{nazwa_modelu}.pth')

                self.historia_wynikow.append(wynik)
                self.calkowity_wynik += wynik
                ilosc_gier = len(self.historia_wynikow)
                self.historia_srednich.append(self.calkowity_wynik / ilosc_gier)
                self.after(0, self.aktualizuj_wykres)

    def aktualizuj_klatke(self, ctk_img):
        self.game_label.configure(image=ctk_img, text="")
        self.game_label.image = ctk_img

    def aktualizuj_wykres(self):
        self.ax.clear()

        # Tytuł i etykiety osi
        self.ax.set_title("Wydajność Agenta", color='white', fontsize=10)
        self.ax.set_xlabel("Liczba gier", color='white', fontsize=9)
        self.ax.set_ylabel("Punkty", color='white', fontsize=9)

        # Rysowanie dwóch linii
        self.ax.plot(self.historia_wynikow, color='#deff9a', linewidth=1, alpha=0.6, label="Pojedyncza gra")
        self.ax.plot(self.historia_srednich, color='#ff9900', linewidth=2, label="Średnia punktów")

        # --- NOWOŚĆ: Numeryczne wartości na końcach linii ---
        if self.historia_wynikow:  # Sprawdzamy, czy mamy już jakieś dane
            ost_idx = len(self.historia_wynikow) - 1
            ost_wynik = self.historia_wynikow[-1]
            ost_srednia = round(self.historia_srednich[-1], 2)  # Zaokrąglenie do 2 miejsc

            # Wklejamy tekst obok ostatnich punktów (kolory dopasowane do linii)
            self.ax.text(ost_idx, ost_wynik, f" {ost_wynik}", color='#deff9a', fontsize=10, fontweight='bold',
                         verticalalignment='bottom')
            self.ax.text(ost_idx, ost_srednia, f" {ost_srednia}", color='#ff9900', fontsize=10, fontweight='bold',
                         verticalalignment='top')

        # Legenda (wyświetlana w lewym górnym rogu)
        self.ax.legend(loc='upper left', fontsize=8, facecolor='#1e1e1e', edgecolor='#555555', labelcolor='white')

        self.canvas.draw()


if __name__ == "__main__":
    app = CentrumDowodzenia()
    app.mainloop()