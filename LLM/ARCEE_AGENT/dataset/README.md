---
dataset_info:
  features:
  - name: query
    dtype: string
  - name: id
    dtype: int64
  - name: answers
    dtype: string
  - name: tools
    dtype: string
  splits:
  - name: train
    num_bytes: 19515
    num_examples: 15
  download_size: 14826
  dataset_size: 19515
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---
This dataset is derived from [Liu, et. al. (2024)](https://arxiv.org/abs/2406.18518) The original work is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).