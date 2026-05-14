import torch
import argparse
import os
from model import Linear_QNet


def eksportuj_do_onnx(sciezka_wejsciowa, sciezka_wyjsciowa):
    print(f"Rozpoczynam konwersję do formatu ONNX...")

    model = Linear_QNet(11, 256, 3)

    try:
        model.load_state_dict(torch.load(sciezka_wejsciowa, map_location='cpu'))
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {sciezka_wejsciowa}")
        return

    model.eval()
    dummy_input = torch.randn(1, 11)

    torch.onnx.export(
        model,
        dummy_input,
        sciezka_wyjsciowa,
        export_params=True,
        input_names=['stan_gry'],
        output_names=['decyzja']
    )

    print(f"Sukces! Zapisano jako: {sciezka_wyjsciowa}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Eksport AI do ONNX')
    parser.add_argument('--in_path', type=str, required=True, help='Ścieżka do pliku .pth')
    parser.add_argument('--out_path', type=str, required=True, help='Ścieżka do pliku .onnx')
    args = parser.parse_args()

    eksportuj_do_onnx(args.in_path, args.out_path)