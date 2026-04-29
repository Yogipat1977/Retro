"""
AUTOPILOT PONG — Hybrid Audio Engine
Uses pygame.mixer if available; falls back to paplay/pw-play on Linux if mixer is missing.
"""

import math
import struct
import os
import subprocess
import wave
import threading

try:
    import pygame
    import pygame.mixer
    # Force check if mixer is actually functional
    if not hasattr(pygame, "mixer") or pygame.mixer.get_init() is None:
        try:
            pygame.mixer.init()
            MIXER_AVAILABLE = True
        except:
            MIXER_AVAILABLE = False
    else:
        MIXER_AVAILABLE = True
except Exception:
    MIXER_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class AudioEngine:
    def __init__(self):
        self.sounds = {}
        self.initialized = False
        self.use_fallback = False
        self.audio_dir = os.path.join(os.path.dirname(__file__), "assets", "audio")
        
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir, exist_ok=True)

        self._init_mixer()

    def _init_mixer(self):
        if MIXER_AVAILABLE:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
                self.initialized = True
                self._generate_all_sounds()
                return
            except Exception:
                pass
        
        # Fallback to system player (paplay/pw-play)
        self.use_fallback = True
        self.initialized = True
        self._generate_all_sounds()

    def _save_wav(self, name, data, sample_rate=44100):
        """Save raw 16-bit PCM data to a WAV file."""
        path = os.path.join(self.audio_dir, f"{name}.wav")
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(data)
        return path

    def _make_sound_data(self, freq, duration=0.1, wave_type="sine", decay=20, volume=0.5):
        sample_rate = 44100
        n = int(sample_rate * duration)
        
        if NUMPY_AVAILABLE:
            t = np.linspace(0, duration, n, dtype=np.float32)
            if wave_type == "sine":
                w = np.sin(2 * np.pi * freq * t)
            elif wave_type == "square":
                w = np.sign(np.sin(2 * np.pi * freq * t))
            elif wave_type == "sawtooth":
                w = 2 * (freq * t % 1) - 1
            else:
                w = np.sin(2 * np.pi * freq * t)
            
            envelope = np.exp(-t * decay)
            w = w * envelope * volume
            samples = (w * 32767).astype(np.int16)
            stereo = np.column_stack([samples, samples])
            return stereo.tobytes()
        else:
            buf = bytearray(n * 4)
            for i in range(n):
                t = i / sample_rate
                val = int(32767 * math.sin(2 * math.pi * freq * t) * math.exp(-t * decay) * volume)
                val = max(-32768, min(32767, val))
                packed = struct.pack('<hh', val, val)
                buf[i * 4:i * 4 + 4] = packed
            return bytes(buf)

    def _generate_all_sounds(self):
        # Define sound configs
        configs = {
            "paddle":  (440, 0.08, "square", 25, 0.3),
            "wall":    (220, 0.05, "sine", 30, 0.2),
            "goal":    (150, 0.3, "sawtooth", 8, 0.4),
            "win":     (880, 0.4, "sine", 5, 0.4),
            "freeze":  (1200, 0.15, "sine", 12, 0.3),
            "split":   (600, 0.12, "square", 18, 0.25),
            "combo":   (660, 0.1, "square", 20, 0.3),
            "select":  (550, 0.06, "sine", 30, 0.2),
        }

        for name, config in configs.items():
            data = self._make_sound_data(*config)
            if self.use_fallback:
                self.sounds[name] = self._save_wav(name, data)
            else:
                self.sounds[name] = pygame.mixer.Sound(buffer=data)
        
        # Arpeggios (hand-coded for now)
        if self.use_fallback:
            self.sounds["powerup"] = self._save_wav("powerup", self._make_sound_data(440, 0.2))
            self.sounds["levelup"] = self._save_wav("levelup", self._make_sound_data(330, 0.3))
        elif MIXER_AVAILABLE:
            # Re-use existing arpeggio logic from previous version if needed
            # For simplicity in this emergency fix, using a single sound
            self.sounds["powerup"] = pygame.mixer.Sound(buffer=self._make_sound_data(440, 0.2))
            self.sounds["levelup"] = pygame.mixer.Sound(buffer=self._make_sound_data(330, 0.3))

    def play(self, name):
        if not self.initialized or name not in self.sounds:
            return
        
        if self.use_fallback:
            # Use paplay in a background process to avoid blocking
            try:
                subprocess.Popen(["paplay", self.sounds[name]], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                try:
                    subprocess.Popen(["pw-play", self.sounds[name]], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except:
                    pass
        else:
            try:
                self.sounds[name].play()
            except:
                pass

    def play_pitch(self, name, pitch_factor=1.0):
        # Fallback doesn't easily support pitch/volume changes per call
        # but we can at least play the sound
        self.play(name)
