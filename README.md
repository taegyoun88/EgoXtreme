# EgoXtreme: A Dataset for Robust Object Pose Estimation in Egocentric Views under Extreme Conditions

[![Project Page](https://img.shields.io/badge/Project-Page-blue)](https://taegyoun88.github.io/EgoXtreme/) 
[![Paper](https://img.shields.io/badge/arXiv-Paper-b31b1b.svg)](https://arxiv.org/abs/2603.25135)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Train%2FVal-yellow)](https://huggingface.co/datasets/taegyoun88/egoxtreme)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Test_Set-orange)](https://huggingface.co/datasets/taegyoun88/egoxtreme-test)

![EgoXtreme Sample](images/egoxtreme_sample.jpg)

## News
**(2026-04-09)** Our paper has been selected as the **Highlight** paper of **CVPR 2026**!  
**(2026-03-26)** The EgoXtreme dataset and arXiv preprint have been officially released!  
**(2026-02-21)** Our paper has been accepted to **CVPR 2026**!

## Dataset Download
The dataset is hosted on Hugging Face. We separate the test set (without GT) for benchmark evaluation.

* **Train / Validation Set:** [taegyoun88/egoxtreme](https://huggingface.co/datasets/taegyoun88/egoxtreme)
* **Test Set (without GT):** [taegyoun88/egoxtreme-test](https://huggingface.co/datasets/taegyoun88/egoxtreme-test)

## Requirements
+ **[hand_tracking_toolkit](https://github.com/facebookresearch/hand_tracking_toolkit)**
+ **opencv-python**
+ **open3d**

## Dataset Information
EgoXtreme is a novel large-scale dataset designed for robust egocentric 6D object pose estimation under extreme environmental conditions. The dataset comprises approximately 1.3 million frames with a total duration of 775.5 minutes (~12.9 hours). It was captured at 30 fps using Aria glasses, providing high-resolution 1408 $\times$ 1408 raw fisheye RGB images along with their undistorted versions.

The dataset features 15 participants performing diverse interactions with 13 different objects (including sports equipment, assembly blocks, and emergency supplies). It is divided into training (518.8 min), validation (80.7 min), and test (176 min) sets across three challenging scenarios: Industrial Maintenance, Sports, and Emergency Rescue.

## Scenario Configurations
The detailed configurations of illumination and environmental conditions for each scenario are summarized below:
<table>
  <thead>
    <tr>
      <th rowspan="2">Scenario</th>
      <th rowspan="2">Standard<br><span style="font-size: 0.8em; font-weight: normal;">(normal, middle, high)</span></th>
      <th colspan="5">Extreme</th>
      <th rowspan="2">Smoke</th>
      <th rowspan="2">Object</th>
    </tr>
    <tr style="font-size: 0.85em; font-weight: normal;">
      <th>&nbsp;&nbsp;&nbsp;&nbsp;low&nbsp;&nbsp;&nbsp;&nbsp;</th>
      <th>&nbsp;&nbsp;&nbsp;&nbsp;head&nbsp;&nbsp;&nbsp;&nbsp;</th>
      <th>&nbsp;&nbsp;&nbsp;flash&nbsp;&nbsp;&nbsp;</th>
      <th>&nbsp;&nbsp;warning&nbsp;&nbsp;</th>
      <th style="border-right: 1px solid rgba(128, 128, 128, 0.2);">&nbsp;&nbsp;&nbsp;green&nbsp;&nbsp;&nbsp;</th>
    </tr>
  </thead>
  <tbody style="text-align: center;">
    <tr>
      <td style="text-align: left;"><strong>Maintenance</strong></td>
      <td align="center">✔️</td>
      <td align="center">✔️</td>
      <td align="center">✔️</td>
      <td align="center">✔️</td>
      <td></td>
      <td></td>
      <td align="center">✔️</td>
      <td align="center">5</td>
    </tr>
    <tr>
      <td style="text-align: left;"><strong>Sports</strong></td>
      <td align="center">✔️</td>
      <td align="center">✔️</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td align="center">5</td>
    </tr>
    <tr>
      <td style="text-align: left;"><strong>Emergency</strong></td>
      <td align="center">✔️</td>
      <td align="center">✔️</td>
      <td></td>
      <td></td>
      <td align="center">✔️</td>
      <td align="center">✔️</td>
      <td align="center">✔️</td>
      <td align="center">3</td>
    </tr>
  </tbody>
</table>

To facilitate scenario-specific training and evaluation, below is the mapping of Scene IDs to their corresponding scenarios across the dataset splits:
| Split | Scenario | Scene IDs |
| :--- | :--- | :--- |
| **Train** | Maintenance | `000000` - `000211` |
| | Sports | `000212` - `000417` |
| | Emergency | `000418` - `000573` |
| **Validation** | Maintenance | `000000` - `000039` |
| | Sports | `000040` - `000067` |
| | Emergency | `000068` - `000079` |
| **Test** | Maintenance | `000000` - `000095` |
| | Sports | `000096` - `000179` |
| | Emergency | `000180` - `000191` |

For further fine-grained environmental attributes (e.g., specific light conditions and the presence of smoke) of each sequence, please refer to the sequence-level metadata JSON files.

## Dataset Documentation
All files (*.json) and 3D model information follow the BOP format. Please refer to the BOP Challenge website for detailed format specifications.

## Directory Structure
The structure of the EgoXtreme dataset is organized as follows.
Note: To reduce storage size, rgb_undist and mask_undist folders are not included in the initial download. Please refer to the Undistortion section below to generate them.

```
EgoXtreme
├── models/
│   ├── modles_info.json
│   ├── obj_01.ply
│   ├── obj_02.ply
│   └── ...
├── train/
│   ├── 000000/                              # Scene ID
│   │   ├── rgb/                             # Raw fisheye RGB images
│   │   ├── mask/                            # Full object masks
│   │   ├── scene_camera.json
│   │   ├── scene_gt.json
│   │   ├── scene_gt_info.json
│   │   ├── scene_camera_undist.json
│   │   │
│   │   │   # Generated by tools/undistortion.py
│   │   ├── rgb_undist/ (*)                  # Undistorted RGB images
│   │   └── mask_undist/ (*)                 # Undistorted object masks
│   └── ...
├── val/
│   ├── 000000/
│   └── ...
├── test/
│   ├── 000000/
│   └── ...
├── tools/
│   ├── undistortion.py                          # Script to generate undistorted data
│   └── visualization.py                         # Helper script to visualize 6D pose
└── camera.json
```

## Undistortion
Due to the large file size, rgb_undist and mask_undist folders are not included in the dataset. You can generate them using the provided script.

Run the following command:

```
# Process a specific scene
python tools/undistortion.py --data_dir ./data/train --scene_id 000000

# Process all scenes in train/test set
python tools/undistortion.py --data_dir ./data/train --all
```

## Visualization
To visualize the Ground Truth pose on the images.

```
# Visualize specific scene (Add --undist for undistorted images, --im_id for single frame)
python tools/visualization.py --data_dir ./data/test --scene_id 000000 --models_dir ./models [--undist] [--im_id 0]
```

## Baseline Results
We established baselines using recent state-of-the-art RGB-only zero-shot models ([FoundPose](https://github.com/facebookresearch/foundpose), [GigaPose](https://github.com/nv-nguyen/gigapose), [PicoPose](https://github.com/foollh/PicoPose)) on the three scenarios of the **EgoXtreme** dataset.
The results are evaluated using the **ADD(-S) recall** metric at **0.1d** threshold.
Full baseline results including 0.2d and 0.3d can be found in our paper.

| Scenario | Light | Smoke | FoundPose | GigaPose | PicoPose |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Sports** | Standard | | 0.53 | 4.12 | 3.13 |
| | Extreme | | 0.18 | 3.11 | 1.80 |
| **Maintenance** | Standard | | 21.02 | 33.64 | 39.27 |
| | Extreme | | 13.78 | 19.78 | 26.44 |
| | Standard | ✔️ | 14.44 | 23.01 | 26.37 |
| | Extreme | ✔️ | 11.19 | 17.56 | 20.97 |
| **Emergency** | Standard | | 6.31 | 22.03 | 22.67 |
| | Extreme | | 0.10 | 9.40 | 9.18 |
| | Standard | ✔️ | 3.52 | 16.25 | 19.66 |
| | Extreme | ✔️ | 0.11 | 7.07 | 9.45 |

## Citation

```
@inproceedings{egoxtreme2026,
  title={EgoXtreme: A Dataset for Robust Object Pose Estimation in Egocentric Views under Extreme Conditions},
  author={Yoon, Taegyoon and Han, Yegyu and Ji, Seojin and Park, Jaewoo and Kim, Sojeong and Kwon, Taein and Kim, Hyung-Sin},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year={2026}
}
```
