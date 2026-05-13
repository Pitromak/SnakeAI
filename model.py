import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os


# 1. NASZ MÓZG (Sieć Neuronowa)
class Linear_QNet(nn.Module):
    def __init__(self, rozmiar_wejscia, rozmiar_ukryty, rozmiar_wyjscia):
        super().__init__()
        self.linear1 = nn.Linear(rozmiar_wejscia, rozmiar_ukryty)
        self.linear2 = nn.Linear(rozmiar_ukryty, rozmiar_wyjscia)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    # Funkcja do zapisywania wytrenowanego mózgu do pliku
    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


# 2. NASZ NAUCZYCIEL (Trener)
class QTrainer:
    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr  # Learning Rate (Szybkość uczenia)
        self.gamma = gamma  # Discount Rate (Jak bardzo wąż skupia się na przyszłości)

        # Optymalizator Adam - to on wykonuje czarną robotę i "przekręca gałki" w mózgu
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        # Kryterium błędu MSE (Mean Squared Error) - oblicza, jak bardzo AI się pomyliło
        self.criterion = nn.MSELoss()

    def train_step(self, stan, akcja, nagroda, nastepny_stan, koniec_gry):
        # PyTorch wymaga, aby zwykłe liczby z Pythona zamienić na jego własny format (Tensory)
        stan = torch.tensor(stan, dtype=torch.float)
        nastepny_stan = torch.tensor(nastepny_stan, dtype=torch.float)
        akcja = torch.tensor(akcja, dtype=torch.long)
        nagroda = torch.tensor(nagroda, dtype=torch.float)

        # Obsługa sytuacji, gdy trenujemy tylko 1 krok na raz
        if len(stan.shape) == 1:
            stan = torch.unsqueeze(stan, 0)
            nastepny_stan = torch.unsqueeze(nastepny_stan, 0)
            akcja = torch.unsqueeze(akcja, 0)
            nagroda = torch.unsqueeze(nagroda, 0)
            koniec_gry = (koniec_gry,)

        # 1. Zobaczmy, co mózg przewiduje dla obecnego stanu
        pred = self.model(stan)

        # 2. Obliczmy, jaka powinna być IDEALNA odpowiedź na podstawie nagrody
        target = pred.clone()
        for idx in range(len(koniec_gry)):
            Q_new = nagroda[idx]
            if not koniec_gry[idx]:
                # Magiczne równanie Bellmana (serce Deep Q-Learningu)
                Q_new = nagroda[idx] + self.gamma * torch.max(self.model(nastepny_stan[idx]))
            target[idx][torch.argmax(akcja[idx]).item()] = Q_new

        # 3. Powiedzmy optymalizatorowi, żeby skorygował błędy
        self.optimizer.zero_grad()  # Czyścimy starą pamięć
        loss = self.criterion(target, pred)  # Obliczamy pomyłkę
        loss.backward()  # Wypuszczamy sygnał korekcyjny w głąb sieci (Backpropagation)
        self.optimizer.step()  # Aktualizujemy wagi neuronów