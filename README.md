# 🐍 Snake AI - Reinforcement Learning

Kompleksowa platforma do trenowania i ewaluacji agentów sztucznej inteligencji opartych na uczeniu ze wzmocnieniem (Reinforcement Learning). Projekt wykorzystuje bibliotekę **PyTorch** do obliczeń neuronowych oraz **Pygame** jako środowisko fizyczne, a całość zarządzana jest przez nowoczesny interfejs graficzny (**CustomTkinter**).

## 🚀 Funkcjonalności
* **Panel Treningowy MLOps:** Interfejs pozwalający na płynną manipulację hiperparametrami na żywo (Epsilon, Learning Rate).
* **Zarządzanie Modelami:** Możliwość tworzenia nowych architektur oraz kontynuowania treningu bazując na wcześniej zapisanych wagach sieci (`.pth`).
* **Symulacja (Ewaluacja):** Dedykowany tryb testowy z wyłączoną eksploracją, gdzie agent polega w 100% na wyuczonym instynkcie.
* **Gotowość do integracji:** Wbudowany skrypt eksportujący przetrenowane modele do uniwersalnego standardu **ONNX**.

## 🛠️ Instalacja i Uruchomienie (Natywnie - Zalecane dla Windows/macOS)

Najprostsza metoda na uruchomienie aplikacji z pełnym wsparciem dla interfejsu graficznego.

1. Sklonuj repozytorium lub pobierz paczkę ZIP.
2. Otwórz terminal w folderze projektu i zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt