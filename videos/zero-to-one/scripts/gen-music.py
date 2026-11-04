"""Local MusicGen bed for the turn → payoff (free, offline once the model is cached).

Writes assets/bgm/warm-seed.wav (~30 s); scripts/build-music.sh loops and shapes it.
"""
import numpy as np
import soundfile as sf
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

torch.manual_seed(1095)
proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
rate = model.config.audio_encoder.sampling_rate
prompt = (
    "warm hopeful modern instrumental, soft felt piano chords, gentle plucked synth arpeggio, "
    "airy pads, light soft kick and shaker, steady and rising, optimistic, clean mix, 100 bpm"
)
inputs = proc(text=[prompt], padding=True, return_tensors="pt")
with torch.no_grad():
    audio = model.generate(**inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=1500)
sf.write("assets/bgm/warm-seed.wav", audio[0, 0].numpy().astype(np.float32), rate)
print("warm done", flush=True)
