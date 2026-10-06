# Procedural background music for the 集思 palette video (12 s, synced to the color changes)
# Calm version: low register felt-piano, warm low drone, slow pads, long reverb, no busy off-beats.
import sys, wave
import numpy as np
SR = 44100; DUR = 12.0; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR); sig = sig[: max(0, N - i)] * gain
    L[i:i+len(sig)] += sig * np.sqrt((1 - pan) / 2); R[i:i+len(sig)] += sig * np.sqrt((1 + pan) / 2)
def lowpass(x, k):        # gentle smoothing to take the edge off the tone
    return np.convolve(x, np.ones(k) / k, "same")
def piano(m, dur=3.2):    # soft felt-piano: warm partials, slow decay, soft hammer
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    s = (np.sin(2*np.pi*f*t) + 0.4*np.sin(2*np.pi*2*f*t)*np.exp(-t*2.5) + 0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t*4)) * np.exp(-t*1.1)
    return lowpass(s * np.minimum(1, t / 0.018), 6)
def pad(ms, dur, att=1.5, rel=1.8):   # slow, warm chord
    t = np.arange(int(dur * SR)) / SR; s = np.zeros_like(t)
    for m in ms:
        for d in (-0.05, 0.05):
            f = hz(m + d); s += np.sin(2*np.pi*f*t) + 0.15*np.sin(2*np.pi*2*f*t)
    env = np.clip(np.minimum(t/att, (dur - t)/rel), 0, 1)
    return s / (len(ms) * 2) * env * env * (3 - 2*env) / np.maximum(env, 1e-9) * env
def drone(m, dur):        # low cello-like drone with slow swell
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    s = np.sin(2*np.pi*f*t) + 0.3*np.sin(2*np.pi*2*f*t) + 0.1*np.sin(2*np.pi*3*f*t)
    env = np.clip(np.minimum(t/2.5, (dur - t)/2.0), 0, 1)
    return lowpass(s * env * (1 + 0.04*np.sin(2*np.pi*0.3*t)), 12)
add(drone(36, 12.0), 0.0, gain=0.30)                                          # C2 drone under everything
add(pad([48, 55, 60, 64], 3.2), 0.0, gain=0.20)                               # opening Cadd9 (low)
add(piano(60, 4.0), 1.9, gain=0.55)                                           # logo lands: middle C
START, STEP = 2.6, 0.72
chords = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 55], [41, 48, 53, 57]]
for k, ch in enumerate(chords):                                               # Am - F - G - Em - F, two beats each
    add(pad(ch, 2*STEP + 1.2, att=0.6, rel=1.0), START + k*2*STEP - 0.1, gain=0.20)
melody = [64, 67, 69, 72, 69, 67, 64, 62, 67]                                 # one soft note per color change
for k, m in enumerate(melody):
    add(piano(m), START + k*STEP, pan=-0.25 + k/16, gain=0.42)
add(pad([48, 55, 60, 64, 67], 3.2, att=1.0, rel=1.8), 8.9, gain=0.22)         # resolve to C
for i, m in enumerate([48, 55, 60, 64]):                                      # slow rolled final chord
    add(piano(m, 3.0), 9.7 + i*0.16, pan=-0.3 + i*0.2, gain=0.40)
def reverb(x, seed, sec=2.6):
    n0 = int(sec*SR); ir = np.random.default_rng(seed).standard_normal(n0) * np.exp(-np.arange(n0)/SR*2.2); ir[0] = 0
    ir = lowpass(ir, 8)
    n = len(x) + len(ir); F = 1 << (n-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + 0.05*reverb(L, 1); R = R + 0.05*reverb(R, 2)
fade = np.ones(N); nf = int(1.0*SR); fade[-nf:] = np.linspace(1, 0, nf) ** 2
L *= fade; R *= fade
pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L/pk*0.7, R/pk*0.7
out = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(out.tobytes())
