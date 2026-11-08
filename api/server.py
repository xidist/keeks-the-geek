"""Serve a trained Keeks adapter locally. One process, one GPU, one request at a time."""
import asyncio
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import load_config, validate_messages
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

cfg = load_config()
adapter_path = Path(os.getenv("KEEKS_ADAPTER_PATH", str(ROOT / "outputs/full/adapter")))
api_token = os.getenv("KEEKS_API_TOKEN", "")
origins = [x.strip() for x in os.getenv("KEEKS_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",") if x.strip()]
runtime = {}
lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(app):
    if not (adapter_path / "adapter_config.json").is_file():
        raise RuntimeError("No trained adapter found. Run the full training notebook first.")
    manifest = adapter_path.parent / "run_manifest.json"
    if not manifest.is_file() or json.loads(manifest.read_text()).get("status") != "complete":
        raise RuntimeError("A completed run_manifest.json is required next to the adapter folder.")
    from unsloth import FastLanguageModel
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("The included server requires an NVIDIA CUDA GPU.")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(adapter_path), max_seq_length=cfg["max_seq_length"], dtype=None, load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)
    runtime.update(model=model, tokenizer=tokenizer, torch=torch)
    yield
    runtime.clear()


app = FastAPI(title="Keeks the Geek", lifespan=lifespan, docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["POST", "GET"], allow_headers=["Content-Type", "Authorization"])


@app.get("/health")
async def health():
    return {"ready": bool(runtime), "mode": "fine-tuned" if runtime else "unavailable"}


@app.get("/config.js")
async def config_js():
    return Response('window.KEEKS_CONFIG = {apiUrl:"/chat"};', media_type="application/javascript")


@app.post("/chat")
async def chat(request: Request):
    if api_token and not secrets.compare_digest(request.headers.get("authorization", ""), "Bearer " + api_token):
        raise HTTPException(401, "Authentication required at the server-side proxy")
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > 24000:
            raise HTTPException(413, "Conversation too large")
        chunks.append(chunk)
    try:
        payload = json.loads(b"".join(chunks))
        messages = validate_messages(payload.get("messages") if isinstance(payload, dict) else None)
    except (ValueError, TypeError) as error:
        raise HTTPException(422, str(error)) from error
    if lock.locked():
        raise HTTPException(429, "Keeks is busy; try again shortly")
    tokenizer, model, torch = runtime["tokenizer"], runtime["model"], runtime["torch"]
    messages = [{"role": "system", "content": cfg["system_prompt"]}] + messages
    ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
    if len(ids) > cfg["max_seq_length"] - 384:
        raise HTTPException(413, "Conversation is too long. Start a new chat.")
    def generate():
        inputs = torch.tensor([ids], device=model.device)
        with torch.inference_mode():
            output = model.generate(input_ids=inputs, attention_mask=torch.ones_like(inputs),
                                    max_new_tokens=384, do_sample=False,
                                    pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                                    eos_token_id=tokenizer.eos_token_id)
        return tokenizer.decode(output[0][len(ids):], skip_special_tokens=True)
    async with lock:
        # Shield generation so a disconnected client cannot release the GPU lock early.
        work = asyncio.create_task(asyncio.to_thread(generate))
        try:
            answer = await asyncio.shield(work)
        except asyncio.CancelledError:
            await work
            raise
    return {"response": answer, "mode": "fine-tuned"}


app.mount("/", StaticFiles(directory=str(ROOT / "web"), html=True), name="web")
