import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Raíz del proyecto
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "binance")