# petvideo-hub

Local pet → superhero image & video generator. ComfyUI workflows + scripts for turning pet photos into AI-animated superhero clips (Hulk, Iron Man, Batman, Thor, Superman, etc.).

Inspired by petvideo.ai. Runs fully locally, no paid APIs.

## Pipeline

Two-stage:

1. **Stage 1 — Pet photo → styled superhero image**
   - `FLUX.1 Kontext dev (GGUF Q4_K_M)` for best quality on low VRAM
   - or `SDXL + IP-Adapter Plus` as fallback
2. **Stage 2 — Styled image → short video**
   - `LTX-Video 0.9.6 Distilled` (8 sampling steps, ~4 sec / 97 frames @ 24fps)

## Hardware

| GPU / machine | Stage 1 | Stage 2 | Notes |
|---|---|---|---|
| RTX 4090 24GB | 30 s | 30 s | FLUX Kontext fp16, Wan 2.1 14B |
| RTX 3090 24GB | 40 s | 45 s | same |
| RTX 3070 8GB | 2–3 min | 1–2 min | FLUX Kontext Q5/Q6, LTX Distilled |
| M3 Pro 18GB | 8 min | 3 min | FLUX Kontext Q4, LTX Distilled |
| M1/M2 16GB | not recommended | | VRAM too tight |

## Models

Download into these `ComfyUI/models/` subfolders:

### `diffusion_models/`
- [flux1-kontext-dev-Q4_K_M.gguf](https://huggingface.co/QuantStack/FLUX.1-Kontext-dev-GGUF/resolve/main/flux1-kontext-dev-Q4_K_M.gguf) (6.9 GB)

### `checkpoints/`
- [ltxv-2b-0.9.6-distilled.safetensors](https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-2b-0.9.6-distilled-04-25.safetensors) (6.3 GB)
- Optional fallback: [sd_xl_base_1.0.safetensors](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors) (6.6 GB)

### `text_encoders/`
- [clip_l.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors) (246 MB)
- [t5xxl_fp8_e4m3fn.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors) (4.9 GB)

### `vae/`
- ae.safetensors (FLUX VAE, 320 MB — any mirror works)

### `ipadapter/` + `clip_vision/` (Stage 1 fallback)
- [ip-adapter-plus_sdxl_vit-h.safetensors](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors)
- [CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors](https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors)

## Custom nodes

In `ComfyUI/custom_nodes/`:
```bash
git clone https://github.com/city96/ComfyUI-GGUF ComfyUI_GGUF   # rename hyphen → underscore
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus
pip install gguf
```

## Usage

1. Put your pet photo in `ComfyUI/input/my_cat.jpeg` (resize to ≤ 768 px on long side).
2. Load `workflows/flux_kontext.json` in ComfyUI.
3. Edit the text prompt inside the Image Edit node — e.g. *"Transform this cat into a muscular green Hulk..."* (see `prompts/themes.json` for ready-made prompts).
4. Run. Output PNG saved to `ComfyUI/output/`.
5. Copy the PNG into `ComfyUI/input/` and load `workflows/ltxv_i2v.json` to animate.

Or run the batch script:
```bash
python scripts/batch_themes.py --image my_cat.jpeg
```

## Prompts

`prompts/themes.json` holds ready-to-use prompts for: Hulk, Iron Man, Batman, Thor, Superman, Ultracat, Harry Potter cat, Gangster cat.

## Output

Stage 1 → PNG at 768×512 or 1024×1024.
Stage 2 → 4-sec animated WEBP (converts to MP4 with `ffmpeg -i in.webp out.mp4`).

## Known issues

- **FLUX Kontext Q4 loses identity on small pet features** — consider Q5/Q6 if VRAM allows.
- **LTX 2B distilled max length** = 257 frames (~10.7 sec).
- **Apple MPS memory pressure** — close other apps; restart ComfyUI between runs.

## License

MIT.
