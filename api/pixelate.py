"""API: recibe una foto y devuelve el pixel art en PNG."""

import io
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import numpy as np
from PIL import Image, ImageOps

# Para poder importar la carpeta pixelart, que está un nivel más arriba
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pixelart.filters import PaletteReducer, Pixelate, Vivid  # noqa: E402

MAX_SIDE = 1200  # las fotos más grandes se achican, así es más rápido


class handler(BaseHTTPRequestHandler):
    """Recibe la foto por POST y devuelve el pixel art."""

    def do_POST(self) -> None:
        try:
            # 1. Leemos las opciones que vienen en el link (?pixel_size=12&palette=retro)
            options = parse_qs(urlparse(self.path).query)
            pixel_size = int(options.get("pixel_size", ["12"])[0])
            palette = options.get("palette", ["retro"])[0]

            # 2. Leemos la foto y la ponemos derecha si el celular la guardó acostada
            length = int(self.headers.get("Content-Length", 0))
            photo = Image.open(io.BytesIO(self.rfile.read(length)))
            photo = ImageOps.exif_transpose(photo).convert("RGB")
            photo.thumbnail((MAX_SIDE, MAX_SIDE))
            image = np.asarray(photo)

            # 3. Aplicamos los filtros uno detrás del otro (polimorfismo)
            for pixel_filter in [Vivid(), Pixelate(pixel_size), PaletteReducer(palette)]:
                image = pixel_filter.apply(image)

            # 4. Devolvemos el resultado como PNG
            buffer = io.BytesIO()
            Image.fromarray(image).save(buffer, format="PNG")
            self._send(200, "image/png", buffer.getvalue())
        except (ValueError, OSError) as error:
            # Foto que no es imagen, o una opción inválida
            self._send(400, "text/plain; charset=utf-8", f"Error: {error}".encode())

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        """Manda la respuesta al navegador."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)