# Procedural cello background music for the 集思 palette video (12 s, synced to the color changes)
# Additive bowed-string model: harmonics shaped by cello body formants, delayed vibrato, bow attack, bow noise.
import sys, wave
import numpy as np
SR = 44100; DUR = 12.0; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, pan=0.0, gain=1.0):
    i = max(0, int(t * SR)); sig = sig[: max(0, N - i)] * gain
    L[i:i+len(sig)] += sig * np.sqrt((1 - pan) / 2); R[i:i+len(sig)] += sig * np.sqrt((1 + pan) / 2)
def body(f):              # cello body resonances (approx. formant peaks)
    return 0.12 + np.exp(-((f-230)/110)**2) + 0.8*np.exp(-((f-520)/170)**2) + 0.45*np.exp(-((f-1150)/350)**2) + 0.15*np.exp(-((f-2600)/700)**2)
def cello(m, dur, att=0.22, rel=0.45, vib=0.0028, seed=0):
    n = int(dur * SR); t = np.arange(n) / SR; f0 = hz(m)
    r = np.random.default_rng(seed)
    vdepth = vib * np.clip((t - 0.25) / 0.4, 0, 1)                       # vibrato fades in after the bow settles
    inst = f0 * (1 + vdepth * np.sin(2*np.pi*(5.0 + 0.3*r.random())*t + r.random()*6) + 0.0006*np.sin(2*np.pi*0.7*t))
    ph = 2*np.pi*np.cumsum(inst) / SR
    s = np.zeros(n)
    for k in range(1, 26):
        if k*f0 > 7000: break
        s += body(k*f0) / k**0.9 * np.sin(k*ph + r.random()*6)
    noise = np.convolve(r.standard_normal(n), np.ones(30)/30, "same") * 0.25   # bow hair noise
    env = np.clip(np.minimum(t/att, (dur - t)/rel), 0, 1); env = env*env*(3 - 2*env)
    swell = 1 + 0.12*np.sin(np.pi*np.clip(t/dur, 0, 1))                  # slight bow pressure swell
    return (s + noise * np.exp(-t*2)) * env * swell / 6
START, STEP = 2.6, 0.72
# low C pedal under the whole piece (second cello)
add(cello(36, 12.0, att=1.8, rel=1.5, vib=0.0015, seed=1), 0.0, pan=-0.2, gain=0.55)
# opening: G2 -> C3 rising into the logo reveal
add(cello(43, 2.0, att=0.6, rel=0.6, seed=2), 0.2, pan=0.2, gain=0.5)
add(cello(48, 1.0, att=0.3, rel=0.5, seed=3), 1.9, pan=0.2, gain=0.55)
# harmony cello: sustained chord tones, two beats each (Am - F - G - Em - F)
harm = [45, 41, 43, 40, 41]
for k, m in enumerate(harm):
    add(cello(m, 2*STEP + 0.35, att=0.35, rel=0.4, vib=0.002, seed=10+k), START + k*2*STEP - 0.12, pan=-0.35, gain=0.42)
# melody cello: one legato note per color change (bow starts slightly early so the note blooms on the beat)
melody = [52, 55, 57, 60, 57, 55, 52, 50, 55]
for k, m in enumerate(melody):
    dur = STEP + 0.3 if k < len(melody) - 1 else 1.3
    add(cello(m, dur, att=0.16, rel=0.3, seed=20+k), START + k*STEP - 0.08, pan=0.3, gain=0.62)
# finale: C major chord bowed by the section, slow roll upward
for i, m in enumerate([36, 43, 48, 52, 55]):
    add(cello(m, 3.0 - i*0.12, att=0.5, rel=1.2, vib=0.0025, seed=40+i), 9.3 + i*0.12, pan=-0.4 + i*0.2, gain=0.45)
def reverb(x, seed, sec=2.8):    # warm hall
    n0 = int(sec*SR); ir = np.random.default_rng(seed).standard_normal(n0) * np.exp(-np.arange(n0)/SR*2.0); ir[0] = 0
    ir = np.convolve(ir, np.ones(10)/10, "same")
    n = len(x) + len(ir); F = 1 << (n-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + 0.045*reverb(L, 1); R = R + 0.045*reverb(R, 2)
fade = np.ones(N); nf = int(1.0*SR); fade[-nf:] = np.linspace(1, 0, nf) ** 2
L *= fade; R *= fade
pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L/pk*0.7, R/pk*0.7
out = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(out.tobytes())
