import customtkinter as ctk
import subprocess
import os
import sys
from tkinter import filedialog # Standardowa biblioteka do okien plików

# Konfiguracja głównego wyglądu
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class CentrumDowodzenia(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Snake AI - Panel Sterowania")
        self.geometry("700x500")

        # Zmienna przechowująca proces uruchomionej gry
        self.aktywny_proces = None

        # --- UKŁAD OKNA (Siatka) ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- MENU BOCZNE ---
        self.menu_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.menu_frame, text="🐍 AI Wąż", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_trening = ctk.CTkButton(self.menu_frame, text="🧠 Panel Treningu", command=self.pokaz_trening)
        self.btn_trening.grid(row=1, column=0, padx=20, pady=10)

        self.btn_pokaz = ctk.CTkButton(self.menu_frame, text="🎮 Testowanie Modelu", command=self.pokaz_gre)
        self.btn_pokaz.grid(row=2, column=0, padx=20, pady=10)

        self.btn_zabij = ctk.CTkButton(self.menu_frame, text="🛑 ZATRZYMAJ WSZYSTKO", fg_color="darkred",
                                       hover_color="red", command=self.zatrzymaj_procesy)
        self.btn_zabij.grid(row=4, column=0, padx=20, pady=(150, 10))

        # --- PANEL GŁÓWNY (Ramka, w której będziemy podmieniać widoki) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Tworzymy widoki
        self.zbuduj_widok_treningu()
        self.zbuduj_widok_gry()

        # Domyślnie pokazujemy trening
        self.pokaz_trening()

        # zmienna przechowująca ścieżkę
        self.sciezka_modelu = "model/model.pth"  # Domyślna ścieżka
        self.sciezka_modelu_gra = "model/model.pth"  # Domyślna ścieżka dla pokazu

    def zbuduj_widok_treningu(self):
        self.frame_trening = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_trening.grid_columnconfigure(0, weight=1)

        tytul = ctk.CTkLabel(self.frame_trening, text="Konfiguracja Hiperparametrów",
                             font=ctk.CTkFont(size=20, weight="bold"))
        tytul.grid(row=0, column=0, pady=(10, 20))

        # Suwaki (Zostawiamy je, działają świetnie)
        self.lbl_eps = ctk.CTkLabel(self.frame_trening, text="Faza losowości (Epsilon): 300")
        self.lbl_eps.grid(row=1, column=0, sticky="w", padx=20)
        self.slider_eps = ctk.CTkSlider(self.frame_trening, from_=0, to=1000, command=lambda v: self.lbl_eps.configure(
            text=f"Faza losowości (Epsilon): {int(v)}"))
        self.slider_eps.set(300)
        self.slider_eps.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.lbl_lr = ctk.CTkLabel(self.frame_trening, text="Szybkość nauki (LR): 0.001")
        self.lbl_lr.grid(row=3, column=0, sticky="w", padx=20)
        self.slider_lr = ctk.CTkSlider(self.frame_trening, from_=0.0001, to=0.01, number_of_steps=100,
                                       command=lambda v: self.lbl_lr.configure(
                                           text=f"Szybkość nauki (LR): {round(v, 4)}"))
        self.slider_lr.set(0.001)
        self.slider_lr.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")

        # --- SEKCJA LOGIKI ZAPISU (PRZEŁĄCZNIK) ---
        self.tryb_treningu = ctk.StringVar(value="Nowy Model")
        self.przelacznik = ctk.CTkSegmentedButton(self.frame_trening, values=["Nowy Model", "Kontynuuj Zapis"],
                                                  variable=self.tryb_treningu, command=self.zmien_tryb_ui)
        self.przelacznik.grid(row=5, column=0, pady=10)

        # Dynamiczna ramka, która będzie się zmieniać
        self.dynamic_frame = ctk.CTkFrame(self.frame_trening, fg_color="transparent")
        self.dynamic_frame.grid(row=6, column=0, pady=10, sticky="ew")
        self.dynamic_frame.grid_columnconfigure(0, weight=1)

        # Opcja A: Nowy Model (Pole tekstowe)
        self.entry_nazwa = ctk.CTkEntry(self.dynamic_frame, placeholder_text="Wpisz nazwę, np. waz_szybki", width=250)

        # Opcja B: Kontynuacja (Przycisk i Etykieta)
        self.sciezka_modelu_trening = ""
        self.btn_browse_trening = ctk.CTkButton(self.dynamic_frame, text="📁 Wybierz plik do kontynuacji",
                                                command=self.wybierz_plik_trening)
        self.lbl_wybrany_trening = ctk.CTkLabel(self.dynamic_frame, text="Nie wybrano pliku", text_color="gray")

        # Inicjalizacja widoku
        self.zmien_tryb_ui("Nowy Model")

        # Przycisk startu
        self.btn_start_trening = ctk.CTkButton(self.frame_trening, text="🚀 ROZPOCZNIJ TRENING", height=40,
                                               command=self.uruchom_agenta)
        self.btn_start_trening.grid(row=7, column=0, padx=20, pady=30, sticky="ew")

    def zbuduj_widok_gry(self):
        self.frame_gra = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_gra.grid_columnconfigure(0, weight=1)

        tytul = ctk.CTkLabel(self.frame_gra, text="Ewaluacja Modelu", font=ctk.CTkFont(size=20, weight="bold"))
        tytul.grid(row=0, column=0, pady=(10, 30))

        opis = ctk.CTkLabel(self.frame_gra,
                            text="Uruchamia plik play.py korzystając z wybranego modelu.\nWąż działa w 100% na własnym instynkcie.")
        opis.grid(row=1, column=0, pady=10)

        # DODANE: Sekcja wyboru pliku
        self.lbl_model_gra = ctk.CTkLabel(self.frame_gra, text="Plik modelu: model.pth (domyślny)", wraplength=300)
        self.lbl_model_gra.grid(row=2, column=0, pady=(20, 0))

        self.btn_browse_gra = ctk.CTkButton(self.frame_gra, text="📁 Wybierz model do testów",
                                            fg_color="transparent", border_width=1, command=self.wybierz_plik_gra)
        self.btn_browse_gra.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Przycisk startu przesunięty na wiersz nr 4
        self.btn_start_gra = ctk.CTkButton(self.frame_gra, text="🎮 URUCHOM SYMULACJĘ", height=50, fg_color="#b85c00",
                                           hover_color="#db6d00", command=self.uruchom_play)
        self.btn_start_gra.grid(row=4, column=0, padx=40, pady=40, sticky="ew")

    # --- FUNKCJE PRZEŁĄCZANIA WIDOKÓW ---
    def pokaz_trening(self):
        self.frame_gra.grid_forget()
        self.frame_trening.grid(row=0, column=0, sticky="nsew")

    def pokaz_gre(self):
        self.frame_trening.grid_forget()
        self.frame_gra.grid(row=0, column=0, sticky="nsew")

    def zmien_tryb_ui(self, tryb):
        # Najpierw chowamy wszystkie elementy dynamiczne
        self.entry_nazwa.grid_forget()
        self.btn_browse_trening.grid_forget()
        self.lbl_wybrany_trening.grid_forget()

        if tryb == "Nowy Model":
            self.entry_nazwa.grid(row=0, column=0, pady=10)
        else:
            self.btn_browse_trening.grid(row=0, column=0, pady=5)
            self.lbl_wybrany_trening.grid(row=1, column=0)

    def wybierz_plik_trening(self):
        sciezka = filedialog.askopenfilename(initialdir="./model", title="Wybierz stary model",
                                             filetypes=(("Pliki PTH", "*.pth"), ("Wszystkie pliki", "*.*")))
        if sciezka:
            self.sciezka_modelu_trening = sciezka
            self.lbl_wybrany_trening.configure(text=f"Wybrano: {os.path.basename(sciezka)}", text_color="white")

    # --- FUNKCJE LOGICZNE (URUCHAMIANIE PROCESÓW) ---
    def uruchom_agenta(self):
        self.zatrzymaj_procesy()
        eps = int(self.slider_eps.get())
        lr = round(self.slider_lr.get(), 4)

        tryb = self.tryb_treningu.get()
        komenda = [sys.executable, "agent.py", "--eps", str(eps), "--lr", str(lr)]

        if tryb == "Nowy Model":
            nazwa = self.entry_nazwa.get().strip()
            if not nazwa:
                nazwa = "nowy_model"  # Zabezpieczenie, jakby uzytkownik zostawił puste pole
            if not nazwa.endswith('.pth'):
                nazwa += '.pth'

            komenda.extend(["--save_name", nazwa])
            print(f"Start: Czysty mózg, zapis do {nazwa}")

        elif tryb == "Kontynuuj Zapis":
            if not self.sciezka_modelu_trening:
                print("BŁĄD: Wybrałeś kontynuację, ale nie wskazałeś pliku!")
                return  # Przerywamy, jeśli nie wskazał pliku

            nazwa_pliku = os.path.basename(self.sciezka_modelu_trening)
            komenda.extend(["--load_path", self.sciezka_modelu_trening, "--save_name", nazwa_pliku])
            print(f"Start: Kontynuacja pliku {nazwa_pliku}")

        self.aktywny_proces = subprocess.Popen(komenda)

    def uruchom_play(self):
        self.zatrzymaj_procesy()
        print(f"Uruchamiam play.py z modelem: {self.sciezka_modelu_gra}")
        # Przekazujemy argument --model_path tak samo jak w treningu
        self.aktywny_proces = subprocess.Popen([sys.executable, "play.py", "--model_path", self.sciezka_modelu_gra])

    def zatrzymaj_procesy(self):
        if self.aktywny_proces is not None:
            print("Zabijam aktywny proces...")
            self.aktywny_proces.terminate()
            self.aktywny_proces = None

    def wybierz_plik(self):
        sciezka = filedialog.askopenfilename(initialdir="./model", title="Wybierz plik modelu",
                                             filetypes=(("Pliki PTH", "*.pth"), ("Wszystkie pliki", "*.*")))
        if sciezka:
            self.sciezka_modelu = sciezka
            nazwa_pliku = os.path.basename(sciezka)
            self.lbl_model.configure(text=f"Plik modelu: {nazwa_pliku}")

    def wybierz_plik_gra(self):
        sciezka = filedialog.askopenfilename(initialdir="./model", title="Wybierz plik modelu do testu",
                                             filetypes=(("Pliki PTH", "*.pth"), ("Wszystkie pliki", "*.*")))
        if sciezka:
            self.sciezka_modelu_gra = sciezka
            nazwa_pliku = os.path.basename(sciezka)
            self.lbl_model_gra.configure(text=f"Plik modelu: {nazwa_pliku}")

if __name__ == "__main__":
    app = CentrumDowodzenia()
    app.mainloop()