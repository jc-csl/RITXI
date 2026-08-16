---
dataset_info:
  features:
    - name: move_id
      dtype: string
    - name: description
      dtype: string
    - name: duration_seconds
      dtype: float64
    - name: has_audio
      dtype: bool
  splits:
    - name: train
      num_examples: 1
      num_bytes: 5220765
  download_size: 5220765
  dataset_size: 5220765
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/*.json
task_categories:
  - robotics
language:
  - en
tags:
  - reachy_mini_community_moves
pretty_name: happy_dance • Reachy Mini Moves
license: apache-2.0
---

# happy_dance • Reachy Mini Moves

Community-contributed Marionette recordings captured on Reachy Mini.

- **Moves uploaded:** 1
- **Total motion time:** 20.0 seconds
- **Audio tracks:** 1
- **Last updated:** 2026-05-11T09:49:12Z

Files live under `data/` — each move ships as a JSON trajectory (Reachy Mini emotions schema) plus an optional WAV recorded directly from the robot.

## How this dataset was produced

These takes were recorded with the Marionette Reachy Mini app. Pick the moves to share, set your Hugging Face username, run `huggingface-cli login` once locally, then hit **Synchronize to Hugging Face dataset** inside Marionette. The app packages the selected files, generates this README, and uploads them to `ShivanshVikram/happy-dance`.

## Selected moves

| Move | Duration | Audio | Recorded at (UTC) |
| --- | --- | --- | --- |
| `attention-3` | 20.0s | Yes | 2026-05-11 09:49 |

## Reuse

- Cite this dataset as `ShivanshVikram/happy-dance`.
- Keep the `reachy_mini_community_moves` tag when sharing derivatives so the community can discover related sets.
