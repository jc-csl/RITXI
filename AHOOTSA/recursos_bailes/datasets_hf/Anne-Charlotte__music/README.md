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
      num_examples: 8
      num_bytes: 49535336
  download_size: 49535336
  dataset_size: 49535336
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
pretty_name: music • Reachy Mini Moves
license: apache-2.0
---

# music • Reachy Mini Moves

            Community-contributed Marionette recordings captured on Reachy Mini.

            - **Moves uploaded:** 8
            - **Total motion time:** 188.8 seconds
            - **Audio tracks:** 8
            - **Last updated:** 2026-03-11T14:01:22Z

            Files live under `data/` — each move ships as a JSON trajectory (Reachy Mini emotions schema) plus an optional WAV recorded directly from the robot.

            ## How this dataset was produced

            These takes were recorded with the Marionette Reachy Mini app. Pick the moves to share, set your Hugging Face username, run `huggingface-cli login` once locally, then hit **Synchronize to Hugging Face dataset** inside Marionette. The app packages the selected files, generates this README, and uploads them to `Anne-Charlotte/music`.

            ## Selected moves

            | Move | Duration | Audio | Recorded at (UTC) |
            | --- | --- | --- | --- |
            | `spice-girls` | 9.3s | Yes | 2026-03-11 14:01 |
| `paint-it-black` | 20.0s | Yes | 2026-03-11 14:00 |
| `las-ketchup` | 15.0s | Yes | 2026-03-11 13:59 |
| `katy-perry-fireworks` | 46.0s | Yes | 2026-03-11 13:56 |
| `eagles-hotel-california` | 26.0s | Yes | 2026-03-11 13:54 |
| `beyonce-single-ladies` | 19.7s | Yes | 2026-03-11 13:49 |
| `feel-the-magic-in-the-air` | 22.0s | Yes | 2026-03-02 16:04 |
| `demon-hunters-1` | 30.8s | Yes | 2026-02-26 08:01 |

            ## Reuse

            - Cite this dataset as `Anne-Charlotte/music`.
            - Keep the `reachy_mini_community_moves` tag when sharing derivatives so the community can discover related sets.
