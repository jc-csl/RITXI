"""Local recorded-move library for Ahootsa.

Reachy Mini SDK 1.9.0 `RecordedMoves` accepts a Hugging Face dataset identifier
and delegates to `snapshot_download`. It does not accept a Windows local path.
This helper keeps the resources inside the application and constructs the
official `RecordedMove` objects directly from local JSON and audio files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from reachy_mini.motion.recorded_move import RecordedMove


SOUND_EXTENSIONS = (
    ".wav",
    ".mp3",
    ".ogg",
    ".oga",
    ".opus",
    ".flac",
    ".m4a",
    ".aac",
)


class LocalRecordedMoves:
    """Load recorded Reachy Mini movements from a local application folder."""

    def __init__(self, dataset_path: str | Path) -> None:
        self.local_path = Path(dataset_path).expanduser().resolve()

        if not self.local_path.is_dir():
            raise FileNotFoundError(
                f"No existe el dataset local: {self.local_path}"
            )

        self.moves: Dict[str, dict] = {}
        self.sounds: Dict[str, Optional[Path]] = {}
        self._process()

    def _json_paths(self) -> List[Path]:
        paths = list(self.local_path.glob("*.json"))
        data_dir = self.local_path / "data"

        if data_dir.is_dir():
            paths.extend(data_dir.glob("*.json"))

        return sorted(set(path.resolve() for path in paths))

    def _process(self) -> None:
        for move_path in self._json_paths():
            move_name = move_path.stem

            try:
                move_data = json.loads(move_path.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                move_data = json.loads(move_path.read_text())

            sound_path = next(
                (
                    candidate
                    for extension in SOUND_EXTENSIONS
                    if (candidate := move_path.with_suffix(extension)).is_file()
                ),
                None,
            )

            self.moves[move_name] = move_data
            self.sounds[move_name] = sound_path

    def get(self, move_name: str) -> RecordedMove:
        """Return the official SDK `RecordedMove` for a local movement."""
        if move_name not in self.moves:
            raise ValueError(
                f"Movimiento {move_name!r} no encontrado en "
                f"{self.local_path}"
            )

        return RecordedMove(
            self.moves[move_name],
            sound_path=self.sounds[move_name],
        )

    def list_moves(self) -> List[str]:
        """List the movement identifiers available in the local dataset."""
        return list(self.moves.keys())
