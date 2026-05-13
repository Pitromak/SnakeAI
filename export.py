import torch
# Upewnij się, że importujesz klasę swojej sieci z pliku (prawdopodobnie model.py)
from model import Linear_QNet


def eksportuj_do_onnx():
    print("Rozpoczynam konwersję do formatu ONNX...")

    # 1. Zbuduj "pusty" mózg (11 wejść z radaru, 256 ukrytych, 3 wyjścia akcji)
    model = Linear_QNet(11, 256, 3)

    # 2. Wgraj do niego wytrenowaną wiedzę z pliku .pth
    sciezka_pth = 'model/model.pth'
    model.load_state_dict(torch.load(sciezka_pth))

    # Zamrażamy model (bardzo ważne przy eksporcie!)
    model.eval()

    # 3. Tworzymy fałszywy stan gry (tensor z 11 losowymi liczbami)
    # Wymiar to (1, 11) -> 1 oznacza jedną grę naraz, 11 to liczba Twoich czujników
    dummy_input = torch.randn(1, 11)

    # 4. Wykonujemy eksport!
    sciezka_onnx = 'model/model.onnx'
    torch.onnx.export(
        model,  # Model do wyeksportowania
        dummy_input,  # Fałszywe dane, by PyTorch prześledził trasę
        sciezka_onnx,  # Nazwa pliku wyjściowego
        export_params=True,  # Chcemy zapisać wyuczone wagi, nie tylko sam szkielet
        input_names=['stan_gry'],  # Nazywamy piny wejściowe (super przydatne potem w Godocie)
        output_names=['decyzja']  # Nazywamy piny wyjściowe
    )

    print(f"Sukces! Twój uniwersalny model został zapisany jako: {sciezka_onnx}")


if __name__ == '__main__':
    eksportuj_do_onnx()