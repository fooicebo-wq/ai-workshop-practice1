# Procedural background music for the 集思 palette video (12 s, synced to the color changes)
import sys, wave
import numpy as np
SR = 44100; DUR = 12.0; N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR); sig = sig[: max(0, N - i)] * gain
    L[i:i+len(sig)] += sig * np.sqrt((1 - pan) / 2); R[i:i+len(sig)] += sig * np.sqrt((1 + pan) / 2)
def pluck(m, dur=1.6):   # kalimba-like: fundamental + inharmonic partial, fast decay
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    s = np.sin(2*np.pi*f*t) * np.exp(-t*3.2) + 0.35*np.sin(2*np.pi*f*4.07*t) * np.exp(-t*9) + 0.15*np.sin(2*np.pi*f*2*t)*np.exp(-t*5)
    return s * np.minimum(1, t / 0.004)
def pad(ms, dur, att=0.8, rel=1.2):   # soft detuned chord
    t = np.arange(int(dur * SR)) / SR; s = np.zeros_like(t)
    for m in ms:
        for d in (-0.08, 0.08):
            f = hz(m + d); s += np.sin(2*np.pi*f*t) + 0.25*np.sin(2*np.pi*2*f*t)
    env = np.minimum(1, t/att) * np.minimum(1, (dur - t)/rel)
    return s / (len(ms) * 2) * np.clip(env, 0, 1)
def bell(m, dur=3.0):
    t = np.arange(int(dur*SR)) / SR; f = hz(m)
    s = sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t*d) for a, r, d in [(1,1,1.2),(0.5,2.76,2.5),(0.3,5.4,4),(0.2,8.9,6)])
    return s * np.minimum(1, t/0.003)
# brush whoosh (band-limited noise swell) for the logo reveal
w = rng.standard_normal(int(1.7*SR)); w = np.convolve(w, np.ones(40)/40, "same") - np.convolve(w, np.ones(400)/400, "same")
tw = np.arange(len(w))/SR; add(w*np.sin(np.pi*tw/1.7)**2, 0.3, pan=-0.3, gain=0.5)
add(pad([60, 64, 67, 71], 2.9, att=1.2, rel=0.6), 0.0, gain=0.22)            # Cmaj7 intro
add(pluck(76, 2.2), 1.9, gain=0.5)                                            # logo lands
START, STEP = 2.6, 0.72
chords = [[57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 67], [52, 55, 60, 64], [53, 57, 60, 64]]
for k, ch in enumerate(chords):                                               # pad changes every 2 beats
    add(pad(ch, 2*STEP + 0.6, att=0.25, rel=0.5), START + k*2*STEP - 0.05, gain=0.2)
melody = [76, 79, 81, 84, 81, 79, 76, 74, 79]                                 # one note per color change
for k, m in enumerate(melody):
    t = START + k*STEP; pan = -0.5 + k/8
    add(pluck(m), t, pan=pan, gain=0.55)
    add(pluck(m - 12, 1.0), t + STEP/2, pan=-pan, gain=0.22)                  # off-beat echo
    add(pluck({0:45,2:41,4:43,6:40,8:41}.get(k, 0), 1.4) if k % 2 == 0 else np.zeros(1), t, gain=0.35)  # bass
add(pad([60, 64, 67, 71, 74], 3.0, att=0.6, rel=1.4), 9.0, gain=0.22)          # resolve Cmaj9
for i, m in enumerate([72, 76, 79, 83, 86]):                                  # finale bell arpeggio
    add(bell(m, 2.6), 9.7 + i*0.09, pan=-0.4 + i*0.2, gain=0.22)
# simple stereo reverb: decaying noise impulse response
def reverb(x, seed):
    ir = np.random.default_rng(seed).standard_normal(int(1.8*SR)) * np.exp(-np.arange(int(1.8*SR))/SR*3.0); ir[0] = 0
    n = len(x) + len(ir); F = 1 << (n-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + 0.06*reverb(L, 1); R = R + 0.06*reverb(R, 2)
fade = np.ones(N); nf = int(0.8*SR); fade[-nf:] = np.linspace(1, 0, nf) ** 2
L *= fade; R *= fade
pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L/pk*0.89, R/pk*0.89
out = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(out.tobytes())
