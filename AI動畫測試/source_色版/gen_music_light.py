# Procedural light / airy background music for the 集思 palette video (12 s, synced to the color changes)
# Plucked acoustic-guitar arpeggios (Karplus-Strong), clear piano melody, soft shaker, glockenspiel finish.
import sys, wave
import numpy as np
SR = 44100; DUR = 12.0; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, pan=0.0, gain=1.0):
    i = max(0, int(t * SR)); sig = sig[: max(0, N - i)] * gain
    L[i:i+len(sig)] += sig * np.sqrt((1 - pan) / 2); R[i:i+len(sig)] += sig * np.sqrt((1 + pan) / 2)
def guitar(m, dur=1.8, bright=0.5, seed=0):   # Karplus-Strong plucked string, vectorised per period
    n = int(dur * SR); p = int(round(SR / hz(m)))
    r = np.random.default_rng(seed); y = np.zeros(n + p + 1)
    exc = r.uniform(-1, 1, p); exc = bright * exc + (1 - bright) * np.convolve(exc, np.ones(4) / 4, "same")
    y[:p] = exc
    k = p
    while k < n:
        e = min(k + p, n); seg = y[k - p:e - p]; prev = y[k - p - 1:e - p - 1] if k > p else np.concatenate([[0], seg[:-1]])
        y[k:e] = 0.996 * 0.5 * (seg + prev[:len(seg)]); k = e
    y = y[:n]; t = np.arange(n) / SR
    return y * np.minimum(1, (dur - t) / 0.15)
def piano(m, dur=2.0):    # clear, bright piano-like tone
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    s = (np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*2*f*t)*np.exp(-t*3) + 0.2*np.sin(2*np.pi*3*f*t)*np.exp(-t*5) + 0.08*np.sin(2*np.pi*4.01*f*t)*np.exp(-t*7)) * np.exp(-t*1.8)
    return s * np.minimum(1, t / 0.006)
def glock(m, dur=2.2):
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    return (np.sin(2*np.pi*f*t)*np.exp(-t*2.2) + 0.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*5)) * np.minimum(1, t / 0.002)
def shaker(seed, dur=0.12):
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    x = r.standard_normal(n); x = x - np.convolve(x, np.ones(6) / 6, "same")     # keep only the airy top end
    return x * np.minimum(1, t / 0.02) * np.exp(-t * 35)
def pad(ms, dur, att=0.5, rel=0.8):
    t = np.arange(int(dur * SR)) / SR; s = np.zeros_like(t)
    for m in ms:
        for d in (-0.07, 0.07): s += np.sin(2*np.pi*hz(m + d)*t)
    env = np.clip(np.minimum(t/att, (dur - t)/rel), 0, 1)
    return s / (len(ms) * 2) * env
START, STEP = 2.6, 0.72; E8 = STEP / 2
# intro: open guitar strum + airy pad, logo lands on a bright piano note
add(pad([60, 64, 67, 72], 2.9, att=1.0, rel=0.5), 0.0, gain=0.12)
for i, m in enumerate([48, 55, 60, 64, 67, 72]):
    add(guitar(m, 2.6, seed=i), 0.4 + i*0.035, pan=-0.3 + i*0.1, gain=0.38)
add(piano(79, 2.2), 1.9, pan=0.2, gain=0.40)
add(glock(84), 1.9, pan=0.3, gain=0.12)
# groove: C - G - Am - F - C, two beats per chord, guitar picks eighth-note arpeggios
chords = [[48, 55, 60, 64], [43, 55, 59, 62], [45, 52, 57, 60], [41, 53, 57, 60], [48, 55, 60, 64]]
pattern = [0, 2, 1, 3]
for c, ch in enumerate(chords):
    t0 = START + c * 2 * STEP
    add(pad([x + 12 for x in ch[1:]], 2*STEP + 0.4, att=0.2, rel=0.4), t0, gain=0.07)
    for j in range(4):
        m = ch[0] if j == 0 else ch[pattern[j]]
        add(guitar(m + (0 if j == 0 else 12), 1.2, bright=0.45, seed=100 + c*4 + j), t0 + j*E8, pan=-0.35 + 0.1*j, gain=0.30 if j else 0.36)
for k in range(18):                                       # shaker on every eighth, accent off-beats
    add(shaker(200 + k), START + k*E8, pan=0.45, gain=0.10 if k % 2 else 0.05)
melody = [76, 79, 81, 84, 83, 79, 77, 79, 84]                # one piano note per color change
for k, m in enumerate(melody):
    add(piano(m), START + k*STEP, pan=0.15, gain=0.34)
# finale: bright C chord strum + glockenspiel sparkle arpeggio
for i, m in enumerate([48, 55, 60, 64, 67, 72]):
    add(guitar(m, 2.6, seed=300 + i), 9.4 + i*0.03, pan=-0.3 + i*0.1, gain=0.36)
add(pad([60, 64, 67, 72, 76], 2.6, att=0.4, rel=1.2), 9.4, gain=0.12)
for i, m in enumerate([84, 88, 91, 96]):
    add(glock(m), 9.7 + i*0.12, pan=-0.2 + i*0.15, gain=0.13)
def reverb(x, seed, sec=1.6):
    n0 = int(sec*SR); ir = np.random.default_rng(seed).standard_normal(n0) * np.exp(-np.arange(n0)/SR*3.5); ir[0] = 0
    n = len(x) + len(ir); F = 1 << (n-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + 0.04*reverb(L, 1); R = R + 0.04*reverb(R, 2)
fade = np.ones(N); nf = int(0.8*SR); fade[-nf:] = np.linspace(1, 0, nf) ** 2
L *= fade; R *= fade
pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L/pk*0.68, R/pk*0.68
out = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(out.tobytes())
