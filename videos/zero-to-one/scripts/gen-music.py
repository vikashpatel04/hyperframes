"""Generates the two local MusicGen beds (free, offline after the model download)."""
import sys
import numpy as np
import soundfile as sf
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

torch.manual_seed(11)
proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
rate = model.config.audio_encoder.sampling_rate
beds = {
    "tense": "sparse dark ambient pulse, soft low synth drone, slow ticking clock, introspective, minimal, no melody, 90 bpm",
    "bright": "confident uplifting modern electronic, warm plucked synth arpeggio, punchy soft kick, steady four on the floor groove, optimistic product launch, 112 bpm",
}
for name, prompt in beds.items():
    inputs = proc(text=[prompt], padding=True, return_tensors="pt")
    with torch.no_grad():
        audio = model.generate(**inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=1500)
    sf.write(f"assets/bgm/{name}-seed.wav", audio[0, 0].numpy().astype(np.float32), rate)
    print(name, "done", flush=True)
