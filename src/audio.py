"""
AUTOPILOT PONG — Procedural Audio Engine
Synthwave-style sound effects generated entirely in code. No external audio files.
"""

import math
import struct

try:
    import pygame
    import pygame.mixer
    MIXER_AVAILABLE = True
except Exception:
    MIXER_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class AudioEngine:
    """Procedural audio engine using waveform synthesis."""

    def __init__(self):
        self.sounds = {}
        self.initialized = False
        self._init_mixer()

    def _init_mixer(self):
        """Initialize the pygame mixer."""
        if not MIXER_AVAILABLE:
            return
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.initialized = True
            self._generate_all_sounds()
        except Exception:
            self.initialized = False

    def _make_sound_numpy(self, freq, duration=0.1, wave_type="sine",
                          decay=20, volume=0.5):
        """Generate a sound using numpy (fast)."""
        sample_rate = 22050
        n = int(sample_rate * duration)
        t = np.linspace(0, duration, n, dtype=np.float32)

        # Waveform
        if wave_type == "sine":
            wave = np.sin(2 * np.pi * freq * t)
        elif wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif wave_type == "sawtooth":
            wave = 2 * (freq * t % 1) - 1
        else:
            wave = np.sin(2 * np.pi * freq * t)

        # Envelope (exponential decay)
        envelope = np.exp(-t * decay)
        wave = wave * envelope * volume

        # Convert to 16-bit stereo
        samples = (wave * 32767).astype(np.int16)
        stereo = np.column_stack([samples, samples])

        return pygame.mixer.Sound(buffer=stereo.tobytes())

    def _make_sound_basic(self, freq, duration=0.1, decay=20):
        """Generate a sound using basic Python (fallback, slower)."""
        sample_rate = 22050
        n = int(sample_rate * duration)
        buf = bytearray(n * 4)  # 16-bit stereo = 4 bytes per sample

        for i in range(n):
            t = i / sample_rate
            val = int(32767 * math.sin(2 * math.pi * freq * t) * math.exp(-t * decay) * 0.5)
            val = max(-32768, min(32767, val))
            # Pack as signed 16-bit, stereo (left + right)
            packed = struct.pack('<hh', val, val)
            buf[i * 4:i * 4 + 4] = packed

        return pygame.mixer.Sound(buffer=bytes(buf))

    def _make_sound(self, freq, duration=0.1, wave_type="sine", decay=20, volume=0.5):
        """Generate a sound using best available method."""
        if NUMPY_AVAILABLE:
            return self._make_sound_numpy(freq, duration, wave_type, decay, volume)
        else:
            return self._make_sound_basic(freq, duration, decay)

    def _make_arpeggio(self, base_freq, steps=3, step_time=0.06):
        """Generate a rising arpeggio (for power-up pickup)."""
        if not NUMPY_AVAILABLE:
            return self._make_sound_basic(base_freq, steps * step_time)

        sample_rate = 22050
        total_duration = steps * step_time
        n = int(sample_rate * total_duration)
        t = np.linspace(0, total_duration, n, dtype=np.float32)
        wave = np.zeros(n, dtype=np.float32)

        for i in range(steps):
            freq = base_freq * (2 ** (i * 4 / 12))  # Major third intervals
            start = int(i * step_time * sample_rate)
            end = min(int((i + 1) * step_time * sample_rate), n)
            seg_t = np.linspace(0, step_time, end - start, dtype=np.float32)
            seg = np.sin(2 * np.pi * freq * seg_t) * np.exp(-seg_t * 15) * 0.4
            wave[start:end] += seg

        samples = (wave * 32767).astype(np.int16)
        stereo = np.column_stack([samples, samples])
        return pygame.mixer.Sound(buffer=stereo.tobytes())

    def _generate_all_sounds(self):
        """Pre-generate all game sound effects."""
        if not self.initialized:
            return

        try:
            self.sounds = {
                # Paddle hit — sharp square wave blip
                "paddle": self._make_sound(440, 0.08, "square", decay=25, volume=0.3),
                # Wall bounce — soft sine
                "wall": self._make_sound(220, 0.05, "sine", decay=30, volume=0.2),
                # Goal scored — descending buzz
                "goal": self._make_sound(150, 0.3, "sawtooth", decay=8, volume=0.4),
                # Win fanfare
                "win": self._make_sound(880, 0.4, "sine", decay=5, volume=0.4),
                # Power-up pickup — rising arpeggio
                "powerup": self._make_arpeggio(440, steps=4, step_time=0.05),
                # Freeze effect
                "freeze": self._make_sound(1200, 0.15, "sine", decay=12, volume=0.3),
                # Multi-ball split
                "split": self._make_sound(600, 0.12, "square", decay=18, volume=0.25),
                # Level up
                "levelup": self._make_arpeggio(330, steps=5, step_time=0.08),
                # Combo milestone
                "combo": self._make_sound(660, 0.1, "square", decay=20, volume=0.3),
                # Menu select
                "select": self._make_sound(550, 0.06, "sine", decay=30, volume=0.2),
            }
        except Exception:
            self.sounds = {}

    def play(self, name):
        """Play a named sound effect."""
        if not self.initialized or name not in self.sounds:
            return
        try:
            self.sounds[name].play()
        except Exception:
            pass

    def play_pitch(self, name, pitch_factor=1.0):
        """Play a sound with modified volume based on speed (crude pitch simulation)."""
        if not self.initialized or name not in self.sounds:
            return
        try:
            sound = self.sounds[name]
            sound.set_volume(min(1.0, max(0.1, 0.3 + pitch_factor * 0.3)))
            sound.play()
        except Exception:
            pass
