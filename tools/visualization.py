import os
import sys
import json
import argparse
import numpy as np
import cv2
import open3d as o3d
from pathlib import Path
from tqdm import tqdm
from hand_tracking_toolkit import camera, rasterizer

def vis_mask_contours(image, mask, color, thickness=2):
    if mask.dtype != np.uint8:
        mask = (mask > 0).astype(np.uint8) * 255
    
    contours, _ = cv2.findContours(
        mask,
        mode=cv2.RETR_EXTERNAL,
        method=cv2.CHAIN_APPROX_SIMPLE,
    )
    
    out_image = image.copy()
    cv2.drawContours(out_image, contours, -1, color, thickness, cv2.LINE_AA)
    return out_image

def load_o3d_models(models_dir):
    models = {}
    models_path = Path(models_dir)
    ply_files = list(models_path.glob("obj_*.ply"))
    
    if not ply_files:
        print(f"[Warn] No .ply files found in {models_dir}")
        return {}

    print(f"Loading {len(ply_files)} models...")
    for file in ply_files:
        try:
            obj_id = int(file.stem.split('_')[-1])
            mesh = o3d.io.read_triangle_mesh(str(file))
            models[obj_id] = mesh
        except Exception:
            pass
    return models

def rasterize_and_draw_contour(
    image,
    model_mesh,
    R_obj_world,
    t_obj_world,
    camera_model
):
    verts_in_m = np.asarray(model_mesh.vertices) / 1000.0 
    faces_in_m = np.asarray(model_mesh.triangles)
    
    if not model_mesh.has_vertex_normals():
        model_mesh.compute_vertex_normals()
    normals_in_m = np.asarray(model_mesh.vertex_normals)

    verts_in_w = (R_obj_world @ verts_in_m.T + t_obj_world[:, np.newaxis]).T
    normals_in_w = (R_obj_world @ normals_in_m.T).T

    _, mask, _ = rasterizer.rasterize_mesh(
        verts=verts_in_w,
        faces=faces_in_m,
        vert_normals=normals_in_w,
        camera=camera_model,
    )

    color = (0, 255, 0)
    image = vis_mask_contours(image, mask, color, thickness=2)

    return image

def process_visualization(data_dir, scene_id, models_dir, output_dir, undist, target_im_id=None):
    scene_dir = Path(data_dir) / scene_id
    if not scene_dir.exists():
        print(f"[Error] Scene folder not found: {scene_dir}")
        return

    if undist:
        output_dir = Path(output_dir) / "undist" / scene_id
    else:
        output_dir = Path(output_dir) / "raw" / scene_id
    output_dir.mkdir(parents=True, exist_ok=True)

    if undist:
        paths = {
            "gt": scene_dir / "scene_gt_undist.json"
        }
    else:
        paths = {
            "gt": scene_dir / "scene_gt.json"
        }
    paths["camera"] = scene_dir / "scene_camera.json"
    
    if not all(p.exists() for p in paths.values()):
        print(f"[Error] JSON files not found in {scene_dir}")
        return

    print(f"Loading metadata for Scene {scene_id}...")
    with open(paths["camera"], "r") as f: scene_camera = json.load(f)
    with open(paths["gt"], "r") as f: scene_gt = json.load(f)

    models = load_o3d_models(models_dir)
    if not models: return

    if target_im_id is not None:
        if str(target_im_id) not in scene_camera:
            print(f"[Error] Image ID {target_im_id} not found in scene {scene_id}")
            return
        frame_ids = [target_im_id]
        print(f"Visualizing ONLY Image ID {target_im_id} in scene {scene_id}")
    else:
        frame_ids = sorted([int(k) for k in scene_camera.keys()])
        print(f"Visualizing ALL {len(frame_ids)} frames")

    for frame_id in tqdm(frame_ids, desc="Processing"):
        str_id = str(frame_id)
        cam_data = scene_camera[str_id]
        
        if undist:
            img_path = scene_dir / "rgb_undist" / f"{frame_id:06d}.png"
        else:
            img_path = scene_dir / "rgb" / f"{frame_id:06d}.png"
            
        if not img_path.exists():
            print(f"[Warn] Image not found: {img_path}")
            continue
        
        image = cv2.imread(str(img_path))
        if image is None: continue
        
        camera_raw_dict = {
            "T_world_from_camera": {
                "quaternion_wxyz": [1.0, 0.0, 0.0, 0.0],
                "translation_xyz": [0.0, 0.0, 0.0]
            },
            "calibration": cam_data["cam_model"]
        }
        camera_model = camera.from_json(camera_raw_dict)
        
        if undist:
            camera_model = camera.PinholePlaneCameraModel(
                width=camera_model.width,
                height=camera_model.height,
                f=[camera_model.f[0], camera_model.f[1]],
                c=camera_model.c,
                distort_coeffs=[],
                T_world_from_eye=camera_model.T_world_from_eye,
            )

        if str_id in scene_gt: 
            for obj_gt in scene_gt[str_id]:
                obj_id = int(obj_gt["obj_id"])
                if obj_id not in models: continue

                R_m2c = np.array(obj_gt["cam_R_m2c"]).reshape(3, 3)
                t_m2c = np.array(obj_gt["cam_t_m2c"]) / 1000.0 
                
                image = rasterize_and_draw_contour(
                    image=image,
                    model_mesh=models[obj_id],
                    R_obj_world=R_m2c,
                    t_obj_world=t_m2c,
                    camera_model=camera_model,
                )
            
        save_path = output_dir / f"{frame_id:06d}.jpg"
        cv2.imwrite(str(save_path), image)
        
    print(f"Done.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Visualize dataset with 3D Mesh contours.")
    parser.add_argument('--data_dir', type=str, required=True, help='Root dataset directory (e.g., ./data/train)')
    parser.add_argument('--scene_id', type=str, required=True, help='Scene ID to visualize (e.g., 000000)')
    parser.add_argument('--models_dir', type=str, required=True, help='Path to models folder')
    parser.add_argument('--output_dir', type=str, default='vis_output', help='Output directory')
    parser.add_argument("--undist", action='store_true', help="Visualize undistorted images")
    parser.add_argument("--im_id", type=int, default=None, help="Specific image ID to visualize (Optional)")
    args = parser.parse_args()
    
    process_visualization(args.data_dir, args.scene_id, args.models_dir, args.output_dir, args.undist, args.im_id)
