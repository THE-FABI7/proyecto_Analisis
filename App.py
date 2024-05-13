import sys
from pathlib import Path

# Añadir el directorio src al sys.path para acceder a los módulos dentro de src
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

from models.UIManager import UIManager

if __name__ == "__main__":
    ui_manager = UIManager()
    ui_manager.run()