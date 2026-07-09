"""Alias español para explore_image."""
from __future__ import annotations

from explore_image import ExploreImage as _ExploreImage


class ExplorarImagen(_ExploreImage):
    name = "explorar_imagen"
    description = "Alias español de explore_image. Explora o describe una imagen/cámara con Ollama vision."
