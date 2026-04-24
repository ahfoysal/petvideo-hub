#!/usr/bin/env python3
"""
Batch-generate pet superhero images via a running ComfyUI server.

Assumes:
  - ComfyUI running at http://127.0.0.1:8188
  - Input image placed in ComfyUI/input/<name>
  - Models from README installed

Usage:
  python scripts/batch_themes.py --image my_cat.jpeg
  python scripts/batch_themes.py --image my_cat.jpeg --themes hulk superman
"""

import argparse
import json
import random
import sys
import urllib.request
from pathlib import Path

COMFY = "http://127.0.0.1:8188"
THEMES_FILE = Path(__file__).parent.parent / "prompts" / "themes.json"


def build_flux_kontext_workflow(image_name: str, prompt: str, out_prefix: str) -> dict:
    return {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "flux1-kontext-dev-Q4_K_M.gguf"}},
        "2": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "clip_l.safetensors",
                                                          "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                                                          "type": "flux"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["3", 0]}},
        "5": {"class_type": "FluxGuidance", "inputs": {"conditioning": ["7", 0], "guidance": 2.5}},
        "6": {"class_type": "ReferenceLatent", "inputs": {"conditioning": ["5", 0], "latent": ["8", 0]}},
        "10": {"class_type": "BasicGuider", "inputs": {"model": ["1", 0], "conditioning": ["6", 0]}},
        "11": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "12": {"class_type": "BasicScheduler", "inputs": {"model": ["1", 0], "scheduler": "simple",
                                                           "steps": 20, "denoise": 1.0}},
        "13": {"class_type": "RandomNoise", "inputs": {"noise_seed": random.randint(1, 10**9)}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["13", 0], "guider": ["10", 0],
                                                                  "sampler": ["11", 0], "sigmas": ["12", 0],
                                                                  "latent_image": ["8", 0]}},
        "15": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["3", 0]}},
        "16": {"class_type": "SaveImage", "inputs": {"images": ["15", 0], "filename_prefix": out_prefix}},
    }


def submit(workflow: dict) -> str:
    body = json.dumps({"prompt": workflow, "client_id": "batch_themes"}).encode()
    req = urllib.request.Request(f"{COMFY}/prompt",
                                 data=body,
                                 headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req).read().decode())
    return resp.get("prompt_id", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True,
                        help="Filename inside ComfyUI/input/")
    parser.add_argument("--themes", nargs="*",
                        help="Theme keys from prompts/themes.json (default: all)")
    args = parser.parse_args()

    themes = json.loads(THEMES_FILE.read_text())
    keys = args.themes or list(themes.keys())

    for key in keys:
        if key not in themes:
            print(f"[skip] unknown theme: {key}", file=sys.stderr)
            continue
        prompt = themes[key]["image"]
        prefix = f"{key}_cat"
        wf = build_flux_kontext_workflow(args.image, prompt, prefix)
        pid = submit(wf)
        print(f"queued {key:12s} -> {prefix}_*.png  (prompt_id={pid})")


if __name__ == "__main__":
    main()
