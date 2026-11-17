"""Filtros que convierten una foto en pixel art estilo videojuego retro."""

from abc import ABC, abstractmethod

import numpy as np
from PIL import Image, ImageEnhance

# Paletas de colores retro: cada color es (rojo, verde, azul).
PALETTES = {
    "gameboy": [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)],
    "blanco_y_negro": [(0, 0, 0), (255, 255, 255)],
    "consola": [
        (0, 0, 0), (29, 43, 83), (126, 37, 83), (0, 135, 81),
        (171, 82, 54), (95, 87, 79), (194, 195, 199), (255, 241, 232),
        (255, 0, 77), (255, 163, 0), (255, 236, 39), (0, 228, 54),
        (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170),
    ],
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
        return np.asarray(big)


class PaletteReducer(Filter):
    """Cambia cada color por el más parecido de una paleta retro."""

    def __init__(self, palette: str = "retro") -> None:
        if palette not in PALETTES:
            raise ValueError(f"Paleta inválida: '{palette}'. Opciones: {list(PALETTES)}")
        self.colors = np.array(PALETTES[palette], dtype=np.int32)

    def apply(self, image: np.ndarray) -> np.ndarray:
        pixels = image.reshape(-1, 3).astype(np.int32)
        # Distancia de cada píxel a cada color de la paleta
        distances = ((pixels[:, None, :] - self.colors[None, :, :]) ** 2).sum(axis=2)
        nearest = distances.argmin(axis=1)
        return self.colors[nearest].reshape(image.shape).astype(np.uint8)


        class Vivid(Filter):
    """Pone los colores más vivos y con más contraste, para que la paleta los reconozca mejor."""

    def __init__(self, saturation: float = 1.8, contrast: float = 1.3) -> None:
        self.saturation = saturation
        self.contrast = contrast

    def apply(self, image: np.ndarray) -> np.ndarray:
        picture = Image.fromarray(image)
        picture = ImageEnhance.Color(picture).enhance(self.saturation)
        picture = ImageEnhance.Contrast(picture).enhance(self.contrast)
        return np.asarray(picture)