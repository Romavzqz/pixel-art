"""Tests de los filtros de pixel art."""

import numpy as np
import pytest

from pixelart.filters import PALETTES, PaletteReducer, Pixelate, Vivid


def make_image() -> np.ndarray:
    """Crea una imagen de prueba de 40x40 con cuatro colores en cuadrantes."""
    image = np.zeros((40, 40, 3), np.uint8)
    image[:20, :20] = (200, 30, 30)
    image[:20, 20:] = (30, 200, 30)
    image[20:, :20] = (30, 30, 200)
    image[20:, 20:] = (240, 240, 240)
    return image


def test_pixelate_keeps_size() -> None:
    """Pixelar no cambia el tamaño de la foto."""
    image = make_image()
    result = Pixelate(pixel_size=8).apply(image)
    assert result.shape == image.shape


def test_pixelate_makes_squares_of_one_color() -> None:
    """Cada cuadradito de 10x10 queda de un solo color."""
    image = np.random.default_rng(0).integers(0, 256, (40, 40, 3), dtype=np.uint8)
    result = Pixelate(pixel_size=10).apply(image)
    square = result[:10, :10].reshape(-1, 3)
    assert (square == square[0]).all()


def test_pixelate_rejects_invalid_size() -> None:
    """Un tamaño de pixel menor a 1 da error."""
    with pytest.raises(ValueError):
        Pixelate(pixel_size=0)


@pytest.mark.parametrize("palette", list(PALETTES))
def test_palette_reducer_uses_only_palette_colors(palette: str) -> None:
    """Después de reducir, solo quedan colores de la paleta elegida."""
    result = PaletteReducer(palette).apply(make_image())
    used = {tuple(color) for color in result.reshape(-1, 3).tolist()}
    assert used <= set(PALETTES[palette])


def test_palette_reducer_rejects_unknown_palette() -> None:
    """Una paleta que no existe da error."""
    with pytest.raises(ValueError):
        PaletteReducer("sepia")


def test_vivid_makes_colors_stronger() -> None:
    """Vivid aumenta la diferencia entre el canal más alto y el más bajo."""
    image = np.full((10, 10, 3), (120, 100, 90), np.uint8)
    result = Vivid().apply(image)
    before = int(image[0, 0].max()) - int(image[0, 0].min())
    after = int(result[0, 0].max()) - int(result[0, 0].min())
    assert after > before


def test_filters_do_not_modify_original() -> None:
    """Ningún filtro cambia la imagen que recibe."""
    image = make_image()
    copy = image.copy()
    for pixel_filter in [Vivid(), Pixelate(5), PaletteReducer("gameboy")]:
        pixel_filter.apply(image)
    assert np.array_equal(image, copy)