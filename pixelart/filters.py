"""Filtros que convierten una foto en pixel art estilo videojuego retro."""

from abc import ABC, abstractmethod

import numpy as np
from PIL import Image

# Paletas de colores retro: cada color es (rojo, verde, azul).
PALETTES = {
    "gameboy": [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)],
    "blanco_y_negro": [(0, 0, 0), (255, 255, 255)],
    "retro": [
        (0, 0, 0), (255, 255, 255), (136, 0, 0), (170, 255, 238),
        (204, 68, 204), (0, 204, 85), (0, 0, 170), (238, 238, 119),
        (221, 136, 85), (102, 68, 0), (255, 119, 119), (51, 51, 51),
        (119, 119, 119), (170, 255, 102), (0, 136, 255), (187, 187, 187),
    ],
}


class Filter(ABC):
    """Molde de todos los filtros: reciben una imagen y devuelven otra."""

    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Devuelve una imagen nueva con el filtro aplicado."""


class Pixelate(Filter):
    """Convierte la foto en cuadraditos grandes."""

    def __init__(self, pixel_size: int = 10) -> None:
        if pixel_size < 1:
            raise ValueError("El tamaño del pixel debe ser 1 o más.")
        self.pixel_size = pixel_size

    def apply(self, image: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        small_width = max(1, width // self.pixel_size)
        small_height = max(1, height // self.pixel_size)
        # Achicamos promediando (BOX) y agrandamos sin suavizar (NEAREST)
        small = Image.fromarray(image).resize((small_width, small_height), Image.BOX)
        big = small.resize((width, height), Image.NEAREST)
        return