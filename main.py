"""
Z-Space: Digitacao Espacial
Genero: Shoot 'em up / Typing Game (Estilo ZType)
Plataforma / Linguagem: Python (Pygame)
Resolucao da Janela: 1200x900 pixels (1.5x ampliado)
"""

import json
import math
import os
import random
import struct
import sys
import wave
import pygame

# =============================================================================
# CONFIGURACOES GERAIS E CONSTANTES (ESPACO 1.5X MAIOR: 1200x900)
# =============================================================================
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
FPS = 60
WINDOW_TITLE = "Z-Space: Digitação Espacial"

# Suporte para execucao tanto via script (.py) quanto via executavel (.exe PyInstaller)
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
HIGHSCORES_FILE = os.path.join(BASE_DIR, "highscores.json")

# Paleta de Cores (Estilo Retro Sci-Fi / Arcade)
COLOR_BG_DEEP = (6, 7, 18)
COLOR_WHITE = (240, 245, 255)
COLOR_GRAY = (140, 150, 175)
COLOR_DARK_GRAY = (45, 50, 70)
COLOR_CYAN = (0, 230, 255)
COLOR_YELLOW = (255, 220, 40)
COLOR_ORANGE = (255, 130, 30)
COLOR_RED = (255, 55, 75)
COLOR_GREEN = (50, 240, 130)
COLOR_PURPLE = (185, 80, 255)
COLOR_BOSS = (255, 40, 110)

# =============================================================================
# BANCO DE PALAVRAS EM PORTUGUES (SEM ACENTOS E SEM CEDILHA)
# =============================================================================
PALAVRAS_CURTAS = [
    "SOL", "LUA", "NAVE", "CAOS", "RAIO", "FOGO", "GELO", "ALVO", "MIRA",
    "VIDA", "ONDA", "REDE", "BASE", "ZONA", "ORBE", "VOO", "PULSO", "LASER",
    "ASTRO", "COMETA", "METAL", "MOTOR", "PORTA", "ROTA", "SINAL", "TERRA",
    "VENTO", "VIGIA", "FORCA", "FLUXO", "CARGA", "DADOS", "FAIXA", "GRADE",
    "SETOR", "PILOTO", "SONDA", "TURBO", "VACUO", "ATOMO", "ION", "LUZ"
]

PALAVRAS_MEDIAS = [
    "GALAXIA", "PLANETA", "ESTRELA", "ORBITA", "METEORO", "CRATERA", "ECLIPSE",
    "NEBULOSA", "QUASAR", "PULSAR", "FOGUETE", "SATELITE", "ESTACAO", "CAPSULA",
    "ESCUDO", "CANHAO", "REATOR", "ENERGIA", "SISTEMA", "COMANDO", "CONTROLE",
    "RADAR", "SENSOR", "ANTENA", "MISSAO", "DESTINO", "HORIZONTE", "INFINITO",
    "UNIVERSO", "COSMOS", "GRAVIDADE", "IMPULSO", "PROTON", "NEUTRON", "PLASMA",
    "FUSAO", "INVASOR", "AMEACA", "COMBATE", "DEFESA", "ESQUADRA", "PATRULHA"
]

PALAVRAS_LONGAS = [
    "ASTRONAUTA", "CONSTELACAO", "HIPERESPACO", "PROPULSOR", "TELEMETRIA",
    "TRAJETORIA", "VELOCIDADE", "CINTURAO", "ASTEROIDE", "ATMOSFERA",
    "ESTRATOSFERA", "MAGNETOSFERA", "INTERGERACIONAL", "INTERESTELAR",
    "INTERPLANETARIO", "SUPERCONDUTOR", "ANTIMATERIA", "SINGULARIDADE",
    "BURACONEGRO", "TRANSMISSAO", "FREQUENCIA",
    "SINCRONIZAR", "COMPUTADOR", "PROCESSADOR", "CIBERNETICO", "ENGENHARIA",
    "LABORATORIO", "OBSERVATORIO", "TELESCOPIO", "ACELERADOR", "COMBUSTIVEL",
    "DESTRUIDOR", "COURACADO", "INTERCEPTADOR", "RECONHECIMENTO"
]


# =============================================================================
# UTILITARIOS DE AUDIO E ASSETS (COM FALLBACK PROCEDURAL)
# =============================================================================
def ensure_directories():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(SOUNDS_DIR, exist_ok=True)


def generate_synth_wav(filepath, freq_start, freq_end, duration_sec, volume=0.4, noise=False):
    """Gera um arquivo .wav sintetizado caso nao exista arquivo externo."""
    if os.path.exists(filepath):
        return
    sample_rate = 22050
    num_samples = int(sample_rate * duration_sec)
    try:
        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            phase = 0.0
            for i in range(num_samples):
                t = i / num_samples
                freq = freq_start + (freq_end - freq_start) * t
                envelope = (1.0 - t) ** 1.4
                phase += 2.0 * math.pi * freq / sample_rate
                tone = math.sin(phase)
                if noise:
                    tone = 0.6 * random.uniform(-1.0, 1.0) + 0.4 * tone
                sample = int(max(-1.0, min(1.0, tone * envelope * volume)) * 32767)
                wav_file.writeframesraw(struct.pack("<h", sample))
    except Exception:
        pass


def generate_timestop_wav(filepath):
    """
    Gera um efeito sonoro marcante para a Ampulheta (Paralisacao do Tempo):
    impacto temporal + queda grave de frequencia (time warp) + tique-taque cristalino.
    """
    if os.path.exists(filepath):
        return
    sample_rate = 22050
    duration_sec = 0.95
    num_samples = int(sample_rate * duration_sec)
    try:
        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            phase1 = 0.0
            phase2 = 0.0
            for i in range(num_samples):
                t = i / num_samples
                sec = i / sample_rate
                # Queda exponencial dramatica de frequencia (efeito "time slow")
                freq_drop = 920.0 * ((0.09) ** t) + 55.0
                # Ressonancia harmonica
                freq_sub = freq_drop * 0.5
                phase1 += 2.0 * math.pi * freq_drop / sample_rate
                phase2 += 2.0 * math.pi * freq_sub / sample_rate

                # Pulso de relogio nos instantes 0.0s, 0.22s e 0.48s
                tick = 0.0
                for tick_t in (0.02, 0.24, 0.50):
                    if 0.0 <= (sec - tick_t) < 0.045:
                        local_t = (sec - tick_t) / 0.045
                        tick += math.sin(2.0 * math.pi * 1650.0 * sec) * (1.0 - local_t) ** 2 * 0.45

                wobble = 0.8 + 0.2 * math.sin(2.0 * math.pi * 14.0 * sec)
                envelope = (1.0 - t * 0.75)
                wave_val = (0.55 * math.sin(phase1) + 0.35 * math.sin(phase2)) * wobble * envelope + tick
                sample = int(max(-1.0, min(1.0, wave_val * 0.65)) * 32767)
                wav_file.writeframesraw(struct.pack("<h", sample))
    except Exception:
        pass


def generate_bgm_wav(filepath, duration_sec=6.4):
    """Gera um loop musical retro espacial caso bgm.wav/bgm.ogg nao exista."""
    if os.path.exists(filepath):
        return
    sample_rate = 22050
    num_samples = int(sample_rate * duration_sec)
    notes = [110.0, 130.81, 146.83, 164.81, 146.83, 130.81, 98.0, 110.0]
    arp = [220.0, 261.63, 329.63, 440.0, 329.63, 261.63, 196.0, 246.94]
    try:
        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            phase_bass = 0.0
            phase_arp = 0.0
            for i in range(num_samples):
                sec = i / sample_rate
                idx_bass = int(sec / 0.8) % len(notes)
                idx_arp = int(sec / 0.2) % len(arp)
                f_bass = notes[idx_bass]
                f_arp = arp[idx_arp]
                phase_bass += 2.0 * math.pi * f_bass / sample_rate
                phase_arp += 2.0 * math.pi * f_arp / sample_rate
                s_bass = 0.22 * (1.0 if math.sin(phase_bass) >= 0 else -1.0)
                s_arp = 0.14 * math.sin(phase_arp) * (1.0 - (sec % 0.2) / 0.2)
                sample = int(max(-1.0, min(1.0, s_bass + s_arp)) * 32767)
                wav_file.writeframesraw(struct.pack("<h", sample))
    except Exception:
        pass


class SoundManager:
    """Gerencia musica de fundo e efeitos sonoros (.wav/.ogg)."""

    def __init__(self):
        self.enabled = False
        self.volume = 0.7
        self.sounds = {}
        self.bgm_path = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
        except Exception:
            self.enabled = False

        ensure_directories()
        self._prepare_default_sounds()
        self._load_sounds()

    def _prepare_default_sounds(self):
        generate_synth_wav(os.path.join(SOUNDS_DIR, "shoot.wav"), 880, 260, 0.09, 0.35, False)
        generate_synth_wav(os.path.join(SOUNDS_DIR, "explosion.wav"), 180, 40, 0.35, 0.45, True)
        generate_synth_wav(os.path.join(SOUNDS_DIR, "error.wav"), 160, 90, 0.18, 0.40, False)
        generate_synth_wav(os.path.join(SOUNDS_DIR, "powerup.wav"), 360, 1040, 0.32, 0.40, False)
        generate_timestop_wav(os.path.join(SOUNDS_DIR, "timestop.wav"))
        bgm_ogg = os.path.join(SOUNDS_DIR, "bgm.ogg")
        bgm_wav = os.path.join(SOUNDS_DIR, "bgm.wav")
        if not os.path.exists(bgm_ogg) and not os.path.exists(bgm_wav):
            generate_bgm_wav(bgm_wav)

    def _find_sound_file(self, base_name):
        for ext in (".ogg", ".wav"):
            path = os.path.join(SOUNDS_DIR, base_name + ext)
            if os.path.exists(path):
                return path
        return None

    def _load_sounds(self):
        if not self.enabled:
            return
        for key in ("shoot", "explosion", "error", "powerup", "timestop"):
            path = self._find_sound_file(key)
            if path:
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(self.volume)
                    self.sounds[key] = snd
                except Exception:
                    pass

        self.bgm_path = self._find_sound_file("bgm")
        if self.bgm_path:
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.set_volume(self.volume * 0.55)
                pygame.mixer.music.play(-1)
            except Exception:
                pass

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        if not self.enabled:
            return
        for snd in self.sounds.values():
            snd.set_volume(self.volume)
        try:
            pygame.mixer.music.set_volume(self.volume * 0.55)
        except Exception:
            pass

    def play(self, key):
        if self.enabled and key in self.sounds:
            try:
                self.sounds[key].play()
            except Exception:
                pass


class SpriteManager:
    """
    Carrega imagens .png externas com transparencia para:
    - player.png (Nave do Jogador)
    - enemy.png (Inimigos Comuns)
    - missile.png (Misseis)
    - minion.png (Lacaios)
    - boss.png (Boss)
    - robotic_hand.png (Mao Robotica)
    Caso o .png nao exista ainda, gera e salva o sprite em pixel art transparente.
    """

    def __init__(self):
        ensure_directories()
        self.sprites = {}
        self._load_all()

    def _create_pixel_surface(self, grid, palette, scale=3):
        h = len(grid)
        w = len(grid[0]) if h > 0 else 0
        surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                if ch in palette:
                    pygame.draw.rect(
                        surf,
                        palette[ch],
                        (c * scale, r * scale, scale, scale),
                    )
        return surf

    def _load_or_generate(self, filename, target_size, generator_fn):
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                if target_size:
                    img = pygame.transform.smoothscale(img, target_size)
                return img
            except Exception:
                pass
        surf = generator_fn()
        try:
            pygame.image.save(surf, path)
        except Exception:
            pass
        if target_size and surf.get_size() != target_size:
            surf = pygame.transform.scale(surf, target_size)
        return surf

    def _gen_player(self):
        grid = [
            ".......CC.......",
            "......CAAC......",
            "......CAAC......",
            ".....CCWWCC.....",
            ".....CWWWWC.....",
            "....CCWWWWCC....",
            "...CCBWWWWBCC...",
            "..CCBBWWWWBBCC..",
            ".CCBBBWWWWBBBCC.",
            "CCBBBBWWWWBBBBCC",
            "CBBBB.WWWW.BBBBC",
            "CBB...WWWW...BBC",
            "......OOOO......",
            ".....OOYYOO.....",
        ]
        palette = {
            "C": (0, 220, 255, 255),
            "A": (160, 250, 255, 255),
            "W": (235, 245, 255, 255),
            "B": (35, 95, 190, 255),
            "O": (255, 120, 20, 255),
            "Y": (255, 230, 80, 255),
        }
        return self._create_pixel_surface(grid, palette, scale=3)

    def _gen_enemy(self):
        grid = [
            "..RR........RR..",
            "...RR..PP..RR...",
            "..RRRRPPPPRRRR..",
            ".RRRRRPPPPRRRRR.",
            "RRRRYYRRRRYYRRRR",
            "RRRRYYRRRRYYRRRR",
            ".RRRRRRRRRRRRRR.",
            "..RRR.RRRR.RRR..",
            "...R...RR...R...",
        ]
        palette = {
            "R": (230, 55, 80, 255),
            "P": (150, 40, 180, 255),
            "Y": (255, 230, 60, 255),
        }
        return self._create_pixel_surface(grid, palette, scale=3)

    def _gen_missile(self):
        grid = [
            "...YY...",
            "..OOOO..",
            "..RRRR..",
            "..RWWR..",
            "..RRRR..",
            ".RRRRRR.",
            "RR.RR.RR",
            "R..OO..R",
        ]
        palette = {
            "Y": (255, 240, 90, 255),
            "O": (255, 140, 20, 255),
            "R": (220, 45, 55, 255),
            "W": (240, 240, 255, 255),
        }
        return self._create_pixel_surface(grid, palette, scale=3)

    def _gen_minion(self):
        grid = [
            "....GGGG....",
            "..GGGGGGGG..",
            ".GGYYGGYYGG.",
            "GGGGGGGGGGGG",
            ".GG.GGGG.GG.",
            "G...G..G...G",
        ]
        palette = {
            "G": (60, 225, 130, 255),
            "Y": (255, 230, 60, 255),
        }
        return self._create_pixel_surface(grid, palette, scale=3)

    def _gen_boss(self):
        grid = [
            "....PPPP....PPPP....",
            "..PPPPPPPPPPPPPPPP..",
            ".PPPPRRRRRRRRRRPPPP.",
            "PPPPRRYYRRRRYYRRPPPP",
            "PPPPRRYYRRRRYYRRPPPP",
            "PPPPCCCCCCCCCCCCPPPP",
            ".PPPPCCCCCCCCCCPPPP.",
            "..PPP.RR.PP.RR.PPP..",
            "...P..RR....RR..P...",
        ]
        palette = {
            "P": (165, 45, 225, 255),
            "R": (255, 45, 95, 255),
            "Y": (255, 235, 65, 255),
            "C": (0, 220, 255, 255),
        }
        return self._create_pixel_surface(grid, palette, scale=5)

    def _gen_hand(self):
        grid = [
            ".MM..MM..MM..MM.",
            ".MM..MM..MM..MM.",
            ".SSR.SSR.SSR.SSR",
            "SSSSSSSSSSSSSSSS",
            "SSSSCCCCCCCCSSSS",
            "SSSSCCCCCCCCSSSS",
            ".SSSSSSSSSSSSSS.",
            "..RRRRRRRRRRRR..",
            "...RR..RR..RR...",
        ]
        palette = {
            "M": (170, 185, 210, 255),
            "S": (100, 115, 145, 255),
            "C": (255, 60, 90, 255),
            "R": (255, 150, 30, 255),
        }
        return self._create_pixel_surface(grid, palette, scale=4)

    def _load_all(self):
        self.sprites["player"] = self._load_or_generate("player.png", (56, 48), self._gen_player)
        self.sprites["enemy"] = self._load_or_generate("enemy.png", (54, 34), self._gen_enemy)
        self.sprites["missile"] = self._load_or_generate("missile.png", (28, 34), self._gen_missile)
        self.sprites["minion"] = self._load_or_generate("minion.png", (42, 26), self._gen_minion)
        self.sprites["boss"] = self._load_or_generate("boss.png", (170, 86), self._gen_boss)
        self.sprites["robotic_hand"] = self._load_or_generate("robotic_hand.png", (96, 62), self._gen_hand)

    def get(self, key):
        return self.sprites.get(key)


# =============================================================================
# FUNDO GALAXIA PIXEL ART PROCEDURAL
# =============================================================================
class PixelGalaxyBackground:
    """
    Cenario de uma galaxia desenhado em 'pixel art' gerada processualmente
    pelo proprio codigo (nebulosas em blocos pixelados, planetas pixelados
    e camadas de estrelas com parallax).
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixel_size = 5
        self.base_surface = self._generate_pixel_nebula()
        self.stars = []
        self._init_stars()

    def _generate_pixel_nebula(self):
        cols = self.width // self.pixel_size
        rows = self.height // self.pixel_size
        low_res = pygame.Surface((cols, rows))
        low_res.fill(COLOR_BG_DEEP)

        nebula_blobs = [
            (cols * 0.28, rows * 0.32, 46, (48, 18, 82)),
            (cols * 0.72, rows * 0.65, 54, (16, 52, 92)),
            (cols * 0.52, rows * 0.48, 38, (80, 20, 68)),
            (cols * 0.20, rows * 0.78, 34, (20, 68, 78)),
        ]

        for y in range(rows):
            for x in range(cols):
                r, g, b = COLOR_BG_DEEP
                for bx, by, rad, col in nebula_blobs:
                    dist = math.hypot(x - bx, y - by)
                    if dist < rad:
                        factor = (1.0 - dist / rad) ** 1.6
                        dither = ((x + y) % 2) * 0.12
                        intensity = max(0.0, factor - dither)
                        r = min(255, int(r + col[0] * intensity))
                        g = min(255, int(g + col[1] * intensity))
                        b = min(255, int(b + col[2] * intensity))
                low_res.set_at((x, y), (r, g, b))

        # Galaxia espiral em pixel art no quadrante superior direito
        gx, gy = int(cols * 0.78), int(rows * 0.22)
        for angle_step in range(140):
            ang = angle_step * 0.15
            radius = angle_step * 0.14
            for arm in (0, math.pi):
                px = int(gx + math.cos(ang + arm) * radius * 1.4)
                py = int(gy + math.sin(ang + arm) * radius * 0.8)
                if 0 <= px < cols and 0 <= py < rows:
                    col = (200, 160, 255) if angle_step < 35 else (110, 90, 190)
                    low_res.set_at((px, py), col)

        # Planeta com aneis em pixel art no quadrante esquerdo
        px_center, py_center, p_rad = int(cols * 0.16), int(rows * 0.24), 11
        for y in range(py_center - p_rad - 4, py_center + p_rad + 5):
            for x in range(px_center - p_rad - 10, px_center + p_rad + 11):
                if 0 <= x < cols and 0 <= y < rows:
                    d = math.hypot(x - px_center, y - py_center)
                    if d <= p_rad:
                        shade = 1.0 if (x - px_center) + (y - py_center) < 2 else 0.65
                        band = 15 if (y % 3 == 0) else 0
                        low_res.set_at(
                            (x, y),
                            (
                                int((70 + band) * shade),
                                int((130 + band) * shade),
                                int((195 + band) * shade),
                            ),
                        )
                    elif abs((y - py_center) - (x - px_center) * 0.35) < 1.3 and p_rad + 2 <= abs(x - px_center) <= p_rad + 8:
                        low_res.set_at((x, y), (180, 160, 120))

        return pygame.transform.scale(low_res, (self.width, self.height))

    def _init_stars(self):
        for _ in range(160):
            layer = random.choice([1, 2, 3])
            speed = layer * 20.0
            size = self.pixel_size if layer == 3 else 3
            color = random.choice([
                (220, 235, 255),
                (140, 210, 255),
                (255, 220, 160),
                (195, 150, 255),
            ])
            self.stars.append({
                "x": random.randrange(0, self.width, 2),
                "y": float(random.randrange(0, self.height)),
                "speed": speed,
                "size": size,
                "color": color,
                "twinkle_offset": random.uniform(0, 6.28),
            })

    def update(self, dt):
        for s in self.stars:
            s["y"] += s["speed"] * dt
            if s["y"] >= self.height:
                s["y"] = 0.0
                s["x"] = random.randrange(0, self.width, 2)

    def draw(self, surface, time_sec):
        surface.blit(self.base_surface, (0, 0))
        for s in self.stars:
            twinkle = 0.65 + 0.35 * math.sin(time_sec * 4.0 + s["twinkle_offset"])
            c = (
                int(s["color"][0] * twinkle),
                int(s["color"][1] * twinkle),
                int(s["color"][2] * twinkle),
            )
            pygame.draw.rect(
                surface,
                c,
                (int(s["x"]), int(s["y"]), s["size"], s["size"]),
            )


# =============================================================================
# ENTIDADES DO JOGO
# =============================================================================
class LaserShot:
    """Projetil visual disparado pela nave do jogador ate o alvo."""

    def __init__(self, start_pos, target_pos):
        self.x, self.y = start_pos
        self.tx, self.ty = target_pos
        self.progress = 0.0
        self.speed = 10.0
        self.alive = True

    def update(self, dt):
        self.progress += self.speed * dt
        if self.progress >= 1.0:
            self.progress = 1.0
            self.alive = False

    def draw(self, surface):
        cx = self.x + (self.tx - self.x) * self.progress
        cy = self.y + (self.ty - self.y) * self.progress
        px = self.x + (self.tx - self.x) * max(0.0, self.progress - 0.22)
        py = self.y + (self.ty - self.y) * max(0.0, self.progress - 0.22)
        pygame.draw.line(surface, COLOR_CYAN, (px, py), (cx, cy), 3)
        pygame.draw.circle(surface, COLOR_WHITE, (int(cx), int(cy)), 4)


class Particle:
    """Particula em pixel art para explosoes e efeitos."""

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(50, 240)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.color = color
        self.life = random.uniform(0.25, 0.65)
        self.max_life = self.life
        self.size = random.choice([3, 4, 5])

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return
        ratio = max(0.0, self.life / self.max_life)
        c = (
            int(self.color[0] * ratio),
            int(self.color[1] * ratio),
            int(self.color[2] * ratio),
        )
        pygame.draw.rect(surface, c, (int(self.x), int(self.y), self.size, self.size))


class Enemy:
    """Inimigo comum, missil ou lacaio com uma palavra flutuando acima."""

    def __init__(self, x, y, word, speed, kind, sprite):
        self.x = float(x)
        self.y = float(y)
        self.word = word.upper()
        self.typed_count = 0
        self.speed = float(speed)
        self.kind = kind  # 'enemy', 'missile', 'minion'
        self.sprite = sprite
        self.width = sprite.get_width() if sprite else 48
        self.height = sprite.get_height() if sprite else 34
        self.wobble_seed = random.uniform(0, 6.28)

    @property
    def remaining_word(self):
        return self.word[self.typed_count:]

    def update(self, dt, target_x, target_y, time_sec):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy) or 1.0
        self.x += (dx / dist) * self.speed * dt
        self.y += (dy / dist) * self.speed * dt

        if self.kind == "minion":
            self.x += math.sin(time_sec * 5.0 + self.wobble_seed) * 45.0 * dt

    def draw(self, surface, font, is_locked):
        rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.sprite, rect)

        if is_locked:
            pad = 6
            box = rect.inflate(pad * 2, pad * 2)
            pygame.draw.rect(surface, COLOR_YELLOW, box, 2)

        self.draw_word_label(surface, font, int(self.x), rect.top - 16, is_locked)

    def draw_word_label(self, surface, font, cx, cy, is_locked):
        typed_part = self.word[:self.typed_count]
        rem_part = self.word[self.typed_count:]

        typed_surf = font.render(typed_part, True, COLOR_GREEN)
        rem_color = COLOR_YELLOW if is_locked else COLOR_WHITE
        rem_surf = font.render(rem_part, True, rem_color)

        total_w = typed_surf.get_width() + rem_surf.get_width()
        total_h = max(typed_surf.get_height(), rem_surf.get_height())

        bg_rect = pygame.Rect(cx - total_w // 2 - 7, cy - total_h // 2 - 4, total_w + 14, total_h + 8)
        pygame.draw.rect(surface, (10, 14, 28, 220), bg_rect, border_radius=4)
        border_col = COLOR_YELLOW if is_locked else (70, 80, 110)
        pygame.draw.rect(surface, border_col, bg_rect, 1, border_radius=4)

        start_x = cx - total_w // 2
        surface.blit(typed_surf, (start_x, cy - total_h // 2))
        surface.blit(rem_surf, (start_x + typed_surf.get_width(), cy - total_h // 2))


class RoboticHand:
    """
    Subfase 3 do Boss: Mao Robotica gigante que avanca ate o jogador.
    - Possui uma palavra ativa.
    - Cada palavra concluida faz a mao recuar um estagio.
    - 5 palavras concluidas = 1 recuo total.
    - Se encostar no jogador = Game Over instantaneo!
    """

    def __init__(self, start_x, start_y, sprite, word_generator):
        self.x = float(start_x)
        self.start_y = float(start_y)
        self.y = float(start_y)
        self.sprite = sprite
        self.word_generator = word_generator
        self.words_completed = 0
        self.words_required = 5
        self.speed = 62.0
        self.word = ""
        self.typed_count = 0
        self.assign_new_word()

    def assign_new_word(self):
        self.word = self.word_generator()
        self.typed_count = 0

    def on_word_completed(self):
        self.words_completed += 1
        # Empurra a mao para tras proporcionalmente ao espaco 1.5x maior
        self.y = max(self.start_y, self.y - 115.0)
        if self.words_completed < self.words_required:
            self.assign_new_word()
            return False
        return True

    def update(self, dt, player_x):
        self.y += self.speed * dt
        self.x += (player_x - self.x) * 1.5 * dt

    def draw(self, surface, boss_x, boss_y, font, is_locked):
        segments = 10
        for i in range(1, segments):
            t = i / segments
            sx = int(boss_x + (self.x - boss_x) * t)
            sy = int(boss_y + (self.y - boss_y) * t)
            pygame.draw.rect(surface, (90, 100, 130), (sx - 10, sy - 7, 20, 14))
            pygame.draw.rect(surface, COLOR_RED, (sx - 5, sy - 3, 10, 6))

        rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.sprite, rect)

        if is_locked:
            pygame.draw.rect(surface, COLOR_RED, rect.inflate(14, 14), 2)

        prog_text = f"RECUO DA MÃO: {self.words_completed}/{self.words_required}"
        prog_surf = font.render(prog_text, True, COLOR_ORANGE)
        surface.blit(prog_surf, (int(self.x) - prog_surf.get_width() // 2, rect.top - 46))

        typed_part = self.word[:self.typed_count]
        rem_part = self.word[self.typed_count:]
        t_surf = font.render(typed_part, True, COLOR_GREEN)
        r_surf = font.render(rem_part, True, COLOR_YELLOW if is_locked else COLOR_WHITE)
        tw = t_surf.get_width() + r_surf.get_width()
        th = max(t_surf.get_height(), r_surf.get_height())
        bg_rect = pygame.Rect(int(self.x) - tw // 2 - 8, rect.top - 24 - th // 2, tw + 16, th + 6)
        pygame.draw.rect(surface, (30, 8, 18), bg_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_RED if is_locked else COLOR_ORANGE, bg_rect, 2, border_radius=4)
        surface.blit(t_surf, (int(self.x) - tw // 2, rect.top - 24 - th // 2 + 3))
        surface.blit(r_surf, (int(self.x) - tw // 2 + t_surf.get_width(), rect.top - 24 - th // 2 + 3))


# =============================================================================
# CLASSE PRINCIPAL DO JOGO
# =============================================================================
class ZSpaceGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        # Fontes ajustadas para a resolucao 1200x900
        self.font_title = pygame.font.SysFont("consolas", 44, bold=True)
        self.font_subtitle = pygame.font.SysFont("consolas", 26, bold=True)
        self.font_ui = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_word = pygame.font.SysFont("consolas", 19, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 15, bold=True)

        # Sistemas
        self.sound = SoundManager()
        self.sprites = SpriteManager()
        self.background = PixelGalaxyBackground(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Configuracoes ajustaveis
        self.brightness = 1.0
        self.settings_tab = "SOM"

        # Estados: MENU, SETTINGS, HIGHSCORES, USERNAME, PLAYING, GAMEOVER, VICTORY
        self.state = "MENU"
        self.menu_index = 0
        self.menu_options = ["Jogar", "Configurações", "Recordes", "Sair"]

        # Dados do Jogador e Recordes
        self.username = ""
        self.highscores = self.load_highscores()
        self.score_saved_for_match = False

        # Variaveis de Gameplay
        self.reset_gameplay_variables()

    # -------------------------------------------------------------------------
    # PERSISTENCIA DE RECORDES
    # -------------------------------------------------------------------------
    def load_highscores(self):
        if os.path.exists(HIGHSCORES_FILE):
            try:
                with open(HIGHSCORES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception:
                pass
        return [
            {"name": "NOVA", "score": 4500},
            {"name": "ORION", "score": 3200},
            {"name": "VEGA", "score": 1800},
        ]

    def save_highscore(self, name, score):
        clean_name = (name.strip() or "PILOTO")[:14].upper()
        self.highscores.append({"name": clean_name, "score": int(score)})
        self.highscores.sort(key=lambda item: item["score"], reverse=True)
        self.highscores = self.highscores[:10]
        try:
            with open(HIGHSCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.highscores, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # INICIALIZACAO E LOGICA DE PARTIDA
    # -------------------------------------------------------------------------
    def reset_gameplay_variables(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT - 68
        self.player_angle = 0.0

        self.score = 0
        self.combo = 0
        self.multiplier = 1

        # Sistema de Poder da Ampulheta (Camera Lenta / Paralisacao do Tempo)
        self.max_hourglass_charges = 3
        self.hourglass_charges = 0
        self.combo_charge_progress = 0  # A cada 10 acertos seguidos no combo, ganha 1 ampulheta (ate 3)
        self.time_stop_timer = 0.0     # Quando > 0, paralisa o tempo por 3 segundos e deixa em P&B
        self.hourglass_hud_rect = pygame.Rect(16, SCREEN_HEIGHT - 108, 290, 92)

        self.lives = 3
        self.consecutive_errors = 0
        self.paralyze_timer = 0.0  # 3 segundos quando erra 3 letras seguidas

        self.phase = 1
        self.phase_enemies_destroyed = 0
        self.total_enemies_destroyed = 0
        self.spawn_timer = 0.0
        self.phase_banner_timer = 2.5

        self.enemies = []
        self.locked_target = None
        self.lasers = []
        self.particles = []

        # Estado do Boss (Fase 3)
        self.boss_x = float(SCREEN_WIDTH // 2)
        self.boss_y = 95.0
        self.boss_dir = 1.0
        self.boss_subphase = 1  # 1: Misseis, 2: Lacaios, 3: Mao Robotica
        self.boss_subphase_spawned = 0
        self.boss_subphase_quota = 8
        self.boss_hand_retreats = 0
        self.robotic_hand = None

        self.score_saved_for_match = False

    def activate_hourglass_power(self):
        """Ativa uma carga da Ampulheta: paralisa o tempo por 3s, som marcante e tela P&B."""
        if self.hourglass_charges > 0 and self.time_stop_timer <= 0.0:
            self.hourglass_charges -= 1
            self.time_stop_timer = 3.0
            self.sound.play("timestop")
            # Efeito visual de ondas na ativacao
            self.spawn_explosion(self.player_x, self.player_y, COLOR_WHITE, 35)

    def get_active_letters_on_screen(self):
        used = {e.word[0] for e in self.enemies if e.word}
        if self.robotic_hand and self.robotic_hand.word:
            used.add(self.robotic_hand.word[0])
        return used

    def pick_word(self, pool):
        used_initials = self.get_active_letters_on_screen()
        available = [w for w in pool if w[0] not in used_initials]
        if not available:
            available = pool
        return random.choice(available).upper()

    def spawn_enemy_for_current_phase(self):
        x = random.randint(90, SCREEN_WIDTH - 90)
        y = -30

        if self.phase == 1:
            pool = PALAVRAS_CURTAS if random.random() < 0.78 else PALAVRAS_MEDIAS
            word = self.pick_word(pool)
            speed = random.uniform(52.0, 72.0)
            self.enemies.append(Enemy(x, y, word, speed, "enemy", self.sprites.get("enemy")))

        elif self.phase == 2:
            pool = PALAVRAS_MEDIAS if random.random() < 0.60 else PALAVRAS_LONGAS
            word = self.pick_word(pool)
            speed = random.uniform(76.0, 102.0)
            self.enemies.append(Enemy(x, y, word, speed, "enemy", self.sprites.get("enemy")))

        elif self.phase == 3:
            if self.boss_subphase == 1:
                if self.boss_subphase_spawned < self.boss_subphase_quota:
                    word = self.pick_word(PALAVRAS_CURTAS)
                    mx = self.boss_x + random.randint(-75, 75)
                    my = self.boss_y + 38
                    speed = random.uniform(110.0, 138.0)
                    self.enemies.append(Enemy(mx, my, word, speed, "missile", self.sprites.get("missile")))
                    self.boss_subphase_spawned += 1

            elif self.boss_subphase == 2:
                if self.boss_subphase_spawned < self.boss_subphase_quota:
                    word = self.pick_word(PALAVRAS_MEDIAS)
                    mx = self.boss_x + random.randint(-120, 120)
                    my = self.boss_y + 32
                    speed = random.uniform(82.0, 106.0)
                    self.enemies.append(Enemy(mx, my, word, speed, "minion", self.sprites.get("minion")))
                    self.boss_subphase_spawned += 1

    def spawn_explosion(self, x, y, color=COLOR_ORANGE, count=22):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
        self.sound.play("explosion")

    def handle_typing_Char(self, char):
        """Processa uma letra digitada pelo jogador durante o gameplay."""
        if self.paralyze_timer > 0.0:
            return

        ch = char.upper()
        if not ("A" <= ch <= "Z"):
            return

        if self.locked_target is None:
            candidates = []
            if self.robotic_hand and self.robotic_hand.word.startswith(ch):
                candidates.append(self.robotic_hand)
            for e in self.enemies:
                if e.word.startswith(ch):
                    candidates.append(e)

            if candidates:
                candidates.sort(key=lambda obj: obj.y, reverse=True)
                self.locked_target = candidates[0]
            else:
                self.register_typing_error()
                return

        target = self.locked_target
        expected_char = target.word[target.typed_count]

        if ch == expected_char:
            self.register_typing_hit(target)
        else:
            self.register_typing_error()

    def register_typing_hit(self, target):
        self.consecutive_errors = 0

        # Atualiza combo e multiplicador
        self.combo += 1
        self.multiplier = 1 + (self.combo // 10)

        # Recarrega cargas da Ampulheta a cada 10 acertos seguidos de combo (ate 3 cargas)
        if self.hourglass_charges < self.max_hourglass_charges:
            self.combo_charge_progress += 1
            if self.combo_charge_progress >= 10:
                self.hourglass_charges += 1
                self.combo_charge_progress = 0
                self.sound.play("powerup")
        else:
            self.combo_charge_progress = 10

        # Pontuacao base: 10 pontos por letra * multiplicador atual
        self.score += 10 * self.multiplier

        # Avanca letra digitada e dispara laser visual
        target.typed_count += 1
        self.sound.play("shoot")
        self.lasers.append(
            LaserShot((self.player_x, self.player_y - 18), (target.x, target.y))
        )

        # Rotaciona nave para apontar ao alvo
        dx = target.x - self.player_x
        dy = target.y - self.player_y
        self.player_angle = math.degrees(math.atan2(-dx, -dy))

        # Destroi o inimigo ao completar todas as letras da palavra
        if target.typed_count >= len(target.word):
            self.complete_target_word(target)

    def complete_target_word(self, target):
        if target is self.robotic_hand:
            self.spawn_explosion(target.x, target.y, COLOR_CYAN, 28)
            self.locked_target = None
            fully_retreated = self.robotic_hand.on_word_completed()
            if fully_retreated:
                self.boss_hand_retreats += 1
                self.spawn_explosion(self.boss_x, self.boss_y, COLOR_BOSS, 48)
                self.robotic_hand = None
                if self.boss_hand_retreats >= 3:
                    self.trigger_victory()
                else:
                    self.boss_subphase = 1
                    self.boss_subphase_spawned = 0
                    self.phase_banner_timer = 2.0
            return

        if target in self.enemies:
            self.enemies.remove(target)
        if self.locked_target is target:
            self.locked_target = None

        self.spawn_explosion(target.x, target.y, COLOR_ORANGE, 24)
        self.phase_enemies_destroyed += 1
        self.total_enemies_destroyed += 1

        if self.phase == 1 and self.phase_enemies_destroyed >= 30:
            self.advance_to_phase(2)
        elif self.phase == 2 and self.phase_enemies_destroyed >= 35:
            self.advance_to_phase(3)

    def advance_to_phase(self, new_phase):
        self.phase = new_phase
        self.phase_enemies_destroyed = 0
        self.spawn_timer = 0.0
        self.phase_banner_timer = 3.0
        self.enemies.clear()
        self.locked_target = None
        if new_phase == 3:
            self.boss_subphase = 1
            self.boss_subphase_spawned = 0
            self.boss_hand_retreats = 0
            self.robotic_hand = None

    def register_typing_error(self):
        self.sound.play("error")
        # Quebra de Combo: zera combo, multiplicador volta para x1 e progresso da recarga atual zera
        self.combo = 0
        self.multiplier = 1
        self.combo_charge_progress = 0

        # Penalidade de Erro: 3 letras erradas seguidas = Paralisia por 3 segundos
        self.consecutive_errors += 1
        if self.consecutive_errors >= 3:
            self.paralyze_timer = 3.0
            self.consecutive_errors = 0

    def trigger_game_over(self):
        if not self.score_saved_for_match:
            self.save_highscore(self.username, self.score)
            self.score_saved_for_match = True
        self.state = "GAMEOVER"

    def trigger_victory(self):
        if not self.score_saved_for_match:
            self.save_highscore(self.username, self.score)
            self.score_saved_for_match = True
        self.state = "VICTORY"

    # -------------------------------------------------------------------------
    # LOOP DE ATUALIZACAO (UPDATE)
    # -------------------------------------------------------------------------
    def update_gameplay(self, dt, time_sec):
        if self.phase_banner_timer > 0.0:
            self.phase_banner_timer = max(0.0, self.phase_banner_timer - dt)

        if self.paralyze_timer > 0.0:
            self.paralyze_timer = max(0.0, self.paralyze_timer - dt)

        # Controle do Poder da Ampulheta (3 segundos de tempo paralisado / camera lenta)
        if self.time_stop_timer > 0.0:
            self.time_stop_timer = max(0.0, self.time_stop_timer - dt)
            world_dt = 0.0  # Paralisa completamente o avanco dos inimigos e do Boss!
        else:
            world_dt = dt

        # Controle de Spawn por Fase (pausado enquanto o tempo esta paralisado)
        self.spawn_timer += world_dt
        if self.phase == 1:
            if self.spawn_timer >= 2.0 and (
                len(self.enemies) + self.phase_enemies_destroyed < 30
            ):
                self.spawn_timer -= 2.0
                self.spawn_enemy_for_current_phase()

        elif self.phase == 2:
            if self.spawn_timer >= 1.55 and (
                len(self.enemies) + self.phase_enemies_destroyed < 35
            ):
                self.spawn_timer -= 1.55
                self.spawn_enemy_for_current_phase()

        elif self.phase == 3:
            self.boss_x += self.boss_dir * 95.0 * world_dt
            if self.boss_x > SCREEN_WIDTH - 140:
                self.boss_x = SCREEN_WIDTH - 140
                self.boss_dir = -1.0
            elif self.boss_x < 140:
                self.boss_x = 140
                self.boss_dir = 1.0

            if self.boss_subphase == 1:
                if self.spawn_timer >= 0.85 and self.boss_subphase_spawned < self.boss_subphase_quota:
                    self.spawn_timer = 0.0
                    self.spawn_enemy_for_current_phase()
                elif self.boss_subphase_spawned >= self.boss_subphase_quota and len(self.enemies) == 0:
                    self.boss_subphase = 2
                    self.boss_subphase_spawned = 0
                    self.spawn_timer = 0.0
                    self.phase_banner_timer = 1.8

            elif self.boss_subphase == 2:
                if self.spawn_timer >= 1.15 and self.boss_subphase_spawned < self.boss_subphase_quota:
                    self.spawn_timer = 0.0
                    self.spawn_enemy_for_current_phase()
                elif self.boss_subphase_spawned >= self.boss_subphase_quota and len(self.enemies) == 0:
                    self.boss_subphase = 3
                    self.spawn_timer = 0.0
                    self.phase_banner_timer = 2.0
                    self.robotic_hand = RoboticHand(
                        self.boss_x,
                        self.boss_y + 55,
                        self.sprites.get("robotic_hand"),
                        lambda: self.pick_word(PALAVRAS_LONGAS if random.random() < 0.65 else PALAVRAS_MEDIAS),
                    )

            elif self.boss_subphase == 3 and self.robotic_hand:
                self.robotic_hand.update(world_dt, self.player_x)
                if math.hypot(self.robotic_hand.x - self.player_x, self.robotic_hand.y - self.player_y) < 52:
                    self.spawn_explosion(self.player_x, self.player_y, COLOR_RED, 50)
                    self.trigger_game_over()
                    return

        # Atualiza inimigos com world_dt (paralisados durante o poder da Ampulheta)
        for e in list(self.enemies):
            e.update(world_dt, self.player_x, self.player_y, time_sec)
            if math.hypot(e.x - self.player_x, e.y - self.player_y) < 38 or e.y >= SCREEN_HEIGHT - 28:
                self.enemies.remove(e)
                if self.locked_target is e:
                    self.locked_target = None
                self.lives -= 1
                self.spawn_explosion(self.player_x, self.player_y, COLOR_RED, 30)
                if self.lives <= 0:
                    self.trigger_game_over()
                    return

        # Lasers e particulas continuam na velocidade normal do jogador
        for laser in list(self.lasers):
            laser.update(dt)
            if not laser.alive:
                self.lasers.remove(laser)

        for p in list(self.particles):
            p.update(dt)
            if p.life <= 0:
                self.particles.remove(p)

    # -------------------------------------------------------------------------
    # RENDERIZACAO DO INDICADOR DE AMPULHETA E TELAS
    # -------------------------------------------------------------------------
    def draw_hourglass_icon(self, cx, cy, is_charged, is_active):
        """Desenha um icone de ampulheta estilizado em pixel art / vetorial."""
        w, h = 26, 36
        top = cy - h // 2
        bot = cy + h // 2
        left = cx - w // 2
        right = cx + w // 2

        frame_col = COLOR_YELLOW if is_charged else COLOR_DARK_GRAY
        glass_col = COLOR_CYAN if is_charged else (75, 85, 110)

        # Bases superior e inferior da ampulheta
        pygame.draw.rect(self.screen, frame_col, (left - 2, top, w + 4, 4), border_radius=2)
        pygame.draw.rect(self.screen, frame_col, (left - 2, bot - 4, w + 4, 4), border_radius=2)

        # Preenchimento de areia dourada se carregada
        if is_charged:
            sand_col = COLOR_ORANGE if is_active else COLOR_YELLOW
            pygame.draw.polygon(
                self.screen,
                sand_col,
                [(left + 4, top + 6), (right - 4, top + 6), (cx, cy - 2)],
            )
            pygame.draw.polygon(
                self.screen,
                sand_col,
                [(cx, cy + 3), (left + 3, bot - 5), (right - 3, bot - 5)],
            )
            pygame.draw.line(self.screen, sand_col, (cx, cy - 2), (cx, bot - 5), 2)

        # Contorno de vidro (dois triangulos conectados no centro)
        pygame.draw.polygon(
            self.screen,
            glass_col,
            [(left + 2, top + 4), (right - 2, top + 4), (cx + 2, cy), (cx - 2, cy)],
            2,
        )
        pygame.draw.polygon(
            self.screen,
            glass_col,
            [(cx - 2, cy), (cx + 2, cy), (right - 2, bot - 4), (left + 2, bot - 4)],
            2,
        )

    def draw_hourglass_hud(self):
        """Desenha o painel de Ampulhetas no canto inferior esquerdo da tela."""
        panel = self.hourglass_hud_rect
        pygame.draw.rect(self.screen, (12, 16, 34), panel, border_radius=10)
        border_col = COLOR_YELLOW if self.hourglass_charges > 0 else (65, 80, 115)
        pygame.draw.rect(self.screen, border_col, panel, 2, border_radius=10)

        # Desenha as 3 ampulhetas lado a lado
        for i in range(self.max_hourglass_charges):
            hx = panel.x + 32 + i * 42
            hy = panel.y + 38
            self.draw_hourglass_icon(
                hx,
                hy,
                is_charged=(i < self.hourglass_charges),
                is_active=(self.time_stop_timer > 0.0),
            )

        # Texto de cargas e barra de recarga por combo
        info_x = panel.x + 150
        title_surf = self.font_small.render(
            f"AMPULHETAS: {self.hourglass_charges}/{self.max_hourglass_charges}",
            True,
            COLOR_YELLOW if self.hourglass_charges > 0 else COLOR_GRAY,
        )
        self.screen.blit(title_surf, (info_x, panel.y + 14))

        # Barra de progresso para a proxima carga (a cada 10 acertos de combo)
        bar_rect = pygame.Rect(info_x, panel.y + 38, 124, 12)
        pygame.draw.rect(self.screen, (30, 38, 60), bar_rect, border_radius=5)
        fill_ratio = (
            1.0
            if self.hourglass_charges >= self.max_hourglass_charges
            else (self.combo_charge_progress / 10.0)
        )
        fill_w = int(bar_rect.width * max(0.0, min(1.0, fill_ratio)))
        if fill_w > 0:
            pygame.draw.rect(
                self.screen,
                COLOR_CYAN,
                (bar_rect.x, bar_rect.y, fill_w, bar_rect.height),
                border_radius=5,
            )
        pygame.draw.rect(self.screen, COLOR_WHITE, bar_rect, 1, border_radius=5)

        if self.time_stop_timer > 0.0:
            act_txt = f"TEMPO PARADO: {self.time_stop_timer:.1f}s"
            act_col = COLOR_WHITE
        elif self.hourglass_charges > 0:
            act_txt = "[ESPAÇO] Parar Tempo (3s)"
            act_col = COLOR_GREEN
        else:
            act_txt = f"Combo p/ carga: {self.combo_charge_progress}/10"
            act_col = COLOR_GRAY

        hint_surf = self.font_small.render(act_txt, True, act_col)
        self.screen.blit(hint_surf, (panel.x + 14, panel.bottom - 24))

    def draw_button(self, rect, text, is_selected=False, accent=COLOR_CYAN):
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos) or is_selected
        bg_col = (28, 42, 78) if hovered else (16, 22, 42)
        border_col = accent if hovered else (70, 90, 130)
        pygame.draw.rect(self.screen, bg_col, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=8)
        txt_surf = self.font_subtitle.render(text, True, COLOR_WHITE if hovered else COLOR_GRAY)
        self.screen.blit(
            txt_surf,
            (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2),
        )
        return rect

    def draw_menu(self):
        title1 = self.font_title.render("Z-SPACE", True, COLOR_CYAN)
        title2 = self.font_subtitle.render("DIGITAÇÃO ESPACIAL", True, COLOR_YELLOW)
        self.screen.blit(title1, (SCREEN_WIDTH // 2 - title1.get_width() // 2, 160))
        self.screen.blit(title2, (SCREEN_WIDTH // 2 - title2.get_width() // 2, 218))

        self.menu_rects = []
        start_y = 320
        for i, label in enumerate(self.menu_options):
            r = pygame.Rect(SCREEN_WIDTH // 2 - 170, start_y + i * 76, 340, 56)
            self.draw_button(r, label, is_selected=(i == self.menu_index))
            self.menu_rects.append(r)

        hint = self.font_small.render(
            "Use as Setas / Enter ou clique com o Mouse para navegar", True, COLOR_GRAY
        )
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 48))

    def draw_username_screen(self):
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 280, SCREEN_HEIGHT // 2 - 170, 560, 340)
        pygame.draw.rect(self.screen, (14, 18, 36), panel, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_CYAN, panel, 2, border_radius=12)

        t = self.font_subtitle.render("REGISTRO DE PILOTO", True, COLOR_CYAN)
        self.screen.blit(t, (panel.centerx - t.get_width() // 2, panel.top + 36))

        inst = self.font_ui.render("Digite seu Nome de Usuário para iniciar:", True, COLOR_WHITE)
        self.screen.blit(inst, (panel.centerx - inst.get_width() // 2, panel.top + 96))

        input_box = pygame.Rect(panel.centerx - 200, panel.top + 142, 400, 52)
        pygame.draw.rect(self.screen, (8, 10, 22), input_box, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_YELLOW, input_box, 2, border_radius=6)

        cursor = "_" if (pygame.time.get_ticks() // 400) % 2 == 0 else " "
        name_txt = self.font_subtitle.render(self.username + cursor, True, COLOR_YELLOW)
        self.screen.blit(name_txt, (input_box.x + 16, input_box.y + 12))

        self.btn_start_game = pygame.Rect(panel.centerx - 190, panel.bottom - 82, 180, 48)
        self.btn_back_menu = pygame.Rect(panel.centerx + 10, panel.bottom - 82, 180, 48)

        can_start = len(self.username.strip()) > 0
        self.draw_button(
            self.btn_start_game,
            "Iniciar (Enter)",
            accent=COLOR_GREEN if can_start else COLOR_DARK_GRAY,
        )
        self.draw_button(self.btn_back_menu, "Voltar (Esc)", accent=COLOR_RED)

    def draw_settings_screen(self):
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 310, SCREEN_HEIGHT // 2 - 220, 620, 440)
        pygame.draw.rect(self.screen, (14, 18, 36), panel, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_CYAN, panel, 2, border_radius=12)

        title = self.font_subtitle.render("CONFIGURAÇÕES", True, COLOR_CYAN)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.top + 26))

        self.tab_sound_rect = pygame.Rect(panel.x + 50, panel.top + 80, 245, 46)
        self.tab_bright_rect = pygame.Rect(panel.right - 295, panel.top + 80, 245, 46)

        self.draw_button(
            self.tab_sound_rect, "Aba: Som", is_selected=(self.settings_tab == "SOM"), accent=COLOR_YELLOW
        )
        self.draw_button(
            self.tab_bright_rect,
            "Aba: Brilho da Tela",
            is_selected=(self.settings_tab == "BRILHO"),
            accent=COLOR_YELLOW,
        )

        slider_bar = pygame.Rect(panel.centerx - 190, panel.top + 230, 380, 20)
        self.btn_minus = pygame.Rect(slider_bar.left - 58, slider_bar.centery - 22, 44, 44)
        self.btn_plus = pygame.Rect(slider_bar.right + 14, slider_bar.centery - 22, 44, 44)
        self.slider_bar_rect = slider_bar

        if self.settings_tab == "SOM":
            pct = int(round(self.sound.volume * 100))
            lbl = self.font_ui.render(f"Volume Geral do Áudio: {pct}%", True, COLOR_WHITE)
            self.screen.blit(lbl, (panel.centerx - lbl.get_width() // 2, panel.top + 175))
            ratio = self.sound.volume
        else:
            pct = int(round(self.brightness * 100))
            lbl = self.font_ui.render(f"Brilho / Opacidade da Tela: {pct}%", True, COLOR_WHITE)
            self.screen.blit(lbl, (panel.centerx - lbl.get_width() // 2, panel.top + 175))
            ratio = (self.brightness - 0.3) / 1.0

        pygame.draw.rect(self.screen, (35, 42, 68), slider_bar, border_radius=9)
        fill_w = int(max(0.0, min(1.0, ratio)) * slider_bar.width)
        if fill_w > 0:
            pygame.draw.rect(
                self.screen,
                COLOR_CYAN,
                (slider_bar.x, slider_bar.y, fill_w, slider_bar.height),
                border_radius=9,
            )
        pygame.draw.rect(self.screen, COLOR_WHITE, slider_bar, 2, border_radius=9)

        self.draw_button(self.btn_minus, "-", accent=COLOR_CYAN)
        self.draw_button(self.btn_plus, "+", accent=COLOR_CYAN)

        tip = self.font_small.render(
            "Dica: Use as setas Esquerda/Direita ou clique na barra para ajustar", True, COLOR_GRAY
        )
        self.screen.blit(tip, (panel.centerx - tip.get_width() // 2, panel.top + 285))

        self.btn_settings_back = pygame.Rect(panel.centerx - 120, panel.bottom - 72, 240, 48)
        self.draw_button(self.btn_settings_back, "Voltar ao Menu", accent=COLOR_RED)

    def draw_highscores_screen(self):
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 290, SCREEN_HEIGHT // 2 - 240, 580, 480)
        pygame.draw.rect(self.screen, (14, 18, 36), panel, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_YELLOW, panel, 2, border_radius=12)

        title = self.font_subtitle.render("RECORDES - MAIORES PONTUADORES", True, COLOR_YELLOW)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.top + 28))

        y = panel.top + 88
        for idx, entry in enumerate(self.highscores[:8], start=1):
            rank_col = COLOR_YELLOW if idx == 1 else (COLOR_CYAN if idx <= 3 else COLOR_WHITE)
            line_txt = f"{idx:02d}. {entry['name']:<15} {entry['score']:>7d} PTS"
            surf = self.font_ui.render(line_txt, True, rank_col)
            self.screen.blit(surf, (panel.x + 80, y))
            y += 38

        self.btn_highscores_back = pygame.Rect(panel.centerx - 120, panel.bottom - 68, 240, 48)
        self.draw_button(self.btn_highscores_back, "Voltar ao Menu", accent=COLOR_CYAN)

    def draw_gameplay(self, time_sec):
        # Desenha Boss se estiver na Fase 3
        if self.phase == 3:
            boss_sprite = self.sprites.get("boss")
            boss_rect = boss_sprite.get_rect(center=(int(self.boss_x), int(self.boss_y)))
            self.screen.blit(boss_sprite, boss_rect)

            hp_ratio = (3 - self.boss_hand_retreats) / 3.0
            bar_w = 300
            bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - bar_w // 2, 14, bar_w, 16)
            pygame.draw.rect(self.screen, (40, 15, 30), bar_rect, border_radius=5)
            pygame.draw.rect(
                self.screen,
                COLOR_BOSS,
                (bar_rect.x, bar_rect.y, int(bar_w * hp_ratio), bar_rect.height),
                border_radius=5,
            )
            pygame.draw.rect(self.screen, COLOR_WHITE, bar_rect, 1, border_radius=5)
            boss_lbl = self.font_small.render(
                f"BOSS FINAL - RECUOS DA MÃO: {self.boss_hand_retreats}/3", True, COLOR_WHITE
            )
            self.screen.blit(boss_lbl, (SCREEN_WIDTH // 2 - boss_lbl.get_width() // 2, 34))

        # Desenha Mao Robotica (se ativa na Subfase 3)
        if self.robotic_hand:
            self.robotic_hand.draw(
                self.screen,
                self.boss_x,
                self.boss_y,
                self.font_word,
                is_locked=(self.locked_target is self.robotic_hand),
            )

        # Desenha Inimigos
        for e in self.enemies:
            e.draw(
                self.screen,
                self.font_word,
                is_locked=(e is self.locked_target),
            )

        # Desenha Lasers e Particulas
        for laser in self.lasers:
            laser.draw(self.screen)
        for p in self.particles:
            p.draw(self.screen)

        # Desenha Nave do Jogador
        p_sprite = self.sprites.get("player")
        rotated = pygame.transform.rotate(p_sprite, self.player_angle)
        p_rect = rotated.get_rect(center=(int(self.player_x), int(self.player_y)))
        self.screen.blit(rotated, p_rect)

        # Efeito de Curto-Circuito / Paralisia
        if self.paralyze_timer > 0.0:
            for _ in range(5):
                sx = self.player_x + random.randint(-28, 28)
                sy = self.player_y + random.randint(-26, 26)
                ex = sx + random.randint(-14, 14)
                ey = sy + random.randint(-14, 14)
                pygame.draw.line(self.screen, COLOR_YELLOW, (sx, sy), (ex, ey), 2)
            warn = self.font_subtitle.render(
                f"CURTO-CIRCUITO! PARALISADO ({self.paralyze_timer:.1f}s)", True, COLOR_RED
            )
            self.screen.blit(warn, (SCREEN_WIDTH // 2 - warn.get_width() // 2, SCREEN_HEIGHT - 140))

        # HUD Superior Esquerdo: Pontos, Combo e Multiplicador
        hud_score = self.font_ui.render(f"PONTOS: {self.score}", True, COLOR_WHITE)
        hud_combo = self.font_ui.render(
            f"COMBO: {self.combo} (x{self.multiplier})",
            True,
            COLOR_YELLOW if self.multiplier > 1 else COLOR_CYAN,
        )
        self.screen.blit(hud_score, (18, 14))
        self.screen.blit(hud_combo, (18, 40))

        # HUD Inferior Esquerdo: Indicador de Ampulhetas (Poder de Camera Lenta / Tempo Parado)
        self.draw_hourglass_hud()

        # HUD Superior Direito: Fase, Progresso e Vidas
        if self.phase == 1:
            phase_str = f"FASE 1 ({self.phase_enemies_destroyed}/30)"
        elif self.phase == 2:
            phase_str = f"FASE 2 ({self.phase_enemies_destroyed}/35)"
        else:
            sub_names = {1: "MÍSSEIS", 2: "LACAIOS", 3: "MÃO ROBÓTICA"}
            phase_str = f"FASE 3 - {sub_names.get(self.boss_subphase, 'BOSS')}"

        hud_phase = self.font_ui.render(phase_str, True, COLOR_CYAN)
        hud_lives = self.font_ui.render(f"VIDAS: {'♥ ' * self.lives}", True, COLOR_RED)
        hud_err = self.font_small.render(
            f"Erros seguidos: {self.consecutive_errors}/3", True, COLOR_GRAY
        )
        self.screen.blit(hud_phase, (SCREEN_WIDTH - hud_phase.get_width() - 18, 14))
        self.screen.blit(hud_lives, (SCREEN_WIDTH - hud_lives.get_width() - 18, 40))
        self.screen.blit(hud_err, (SCREEN_WIDTH - hud_err.get_width() - 18, 66))

        # Banner de transicao de Fase / Subfase
        if self.phase_banner_timer > 0.0:
            if self.phase == 1:
                b_txt = "FASE 1 - DESTRUA 30 INIMIGOS"
            elif self.phase == 2:
                b_txt = "FASE 2 - VELOCIDADE E PALAVRAS LONGAS"
            else:
                sub_titles = {
                    1: "BOSS FINAL: SUBFASE 1 (MÍSSEIS RÁPIDOS)",
                    2: "BOSS FINAL: SUBFASE 2 (ENXAME DE LACAIOS)",
                    3: "PERIGO FATAL: MÃO ROBÓTICA!",
                }
                b_txt = sub_titles.get(self.boss_subphase, "FASE 3 - BOSS FINAL")
            b_surf = self.font_subtitle.render(b_txt, True, COLOR_YELLOW)
            b_bg = pygame.Rect(
                SCREEN_WIDTH // 2 - b_surf.get_width() // 2 - 20,
                SCREEN_HEIGHT // 2 - 28,
                b_surf.get_width() + 40,
                52,
            )
            pygame.draw.rect(self.screen, (10, 14, 30), b_bg, border_radius=8)
            pygame.draw.rect(self.screen, COLOR_YELLOW, b_bg, 2, border_radius=8)
            self.screen.blit(b_surf, (b_bg.x + 20, b_bg.y + 12))

        # Se o poder da Ampulheta estiver ativo, converte toda a tela para Preto e Branco!
        if self.time_stop_timer > 0.0:
            self.apply_grayscale_effect()

    def apply_grayscale_effect(self):
        """Deixa toda a tela em preto e branco durante os 3 segundos da Ampulheta."""
        try:
            pygame.transform.grayscale(self.screen, self.screen)
        except Exception:
            pass
        # Borda pulsante indicando o efeito temporal ativo
        pygame.draw.rect(self.screen, (235, 235, 235), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 6)

    def draw_end_screen(self, is_victory):
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 280, SCREEN_HEIGHT // 2 - 180, 560, 360)
        pygame.draw.rect(self.screen, (14, 18, 36), panel, border_radius=12)
        accent = COLOR_GREEN if is_victory else COLOR_RED
        pygame.draw.rect(self.screen, accent, panel, 2, border_radius=12)

        heading = "VITÓRIA ESPACIAL!" if is_victory else "GAME OVER"
        h_surf = self.font_title.render(heading, True, accent)
        self.screen.blit(h_surf, (panel.centerx - h_surf.get_width() // 2, panel.top + 32))

        p_surf = self.font_ui.render(f"Piloto: {self.username}", True, COLOR_WHITE)
        s_surf = self.font_subtitle.render(f"Pontuação Final: {self.score} PTS", True, COLOR_YELLOW)
        k_surf = self.font_ui.render(
            f"Inimigos Destruídos: {self.total_enemies_destroyed}", True, COLOR_CYAN
        )

        self.screen.blit(p_surf, (panel.centerx - p_surf.get_width() // 2, panel.top + 115))
        self.screen.blit(s_surf, (panel.centerx - s_surf.get_width() // 2, panel.top + 158))
        self.screen.blit(k_surf, (panel.centerx - k_surf.get_width() // 2, panel.top + 205))

        self.btn_end_menu = pygame.Rect(panel.centerx - 160, panel.bottom - 82, 320, 50)
        self.draw_button(self.btn_end_menu, "Voltar ao Menu Principal", accent=COLOR_CYAN)

    def apply_brightness_overlay(self):
        if abs(self.brightness - 1.0) < 0.02:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        if self.brightness < 1.0:
            alpha = int((1.0 - self.brightness) * 230)
            overlay.fill((0, 0, 0, max(0, min(220, alpha))))
        else:
            alpha = int((self.brightness - 1.0) * 190)
            overlay.fill((255, 255, 255, max(0, min(140, alpha))))
        self.screen.blit(overlay, (0, 0))

    # -------------------------------------------------------------------------
    # TRATAMENTO DE EVENTOS E LOOP PRINCIPAL
    # -------------------------------------------------------------------------
    def activate_menu_option(self, idx):
        option = self.menu_options[idx]
        if option == "Jogar":
            self.state = "USERNAME"
        elif option == "Configurações":
            self.state = "SETTINGS"
        elif option == "Recordes":
            self.state = "HIGHSCORES"
        elif option == "Sair":
            pygame.quit()
            sys.exit()

    def adjust_active_setting(self, delta):
        if self.settings_tab == "SOM":
            self.sound.set_volume(self.sound.volume + delta)
        else:
            self.brightness = max(0.3, min(1.3, self.brightness + delta))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ---- MENU PRINCIPAL ----
            if self.state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.activate_menu_option(self.menu_index)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, r in enumerate(getattr(self, "menu_rects", [])):
                        if r.collidepoint(event.pos):
                            self.menu_index = i
                            self.activate_menu_option(i)

            # ---- REGISTRO DE USUARIO ----
            elif self.state == "USERNAME":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                    elif event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.username.strip():
                            self.reset_gameplay_variables()
                            self.state = "PLAYING"
                    else:
                        ch = event.unicode
                        if ch and ch.isprintable() and len(self.username) < 14:
                            self.username += ch.upper()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if getattr(self, "btn_start_game", None) and self.btn_start_game.collidepoint(event.pos):
                        if self.username.strip():
                            self.reset_gameplay_variables()
                            self.state = "PLAYING"
                    elif getattr(self, "btn_back_menu", None) and self.btn_back_menu.collidepoint(event.pos):
                        self.state = "MENU"

            # ---- CONFIGURACOES ----
            elif self.state == "SETTINGS":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                    elif event.key == pygame.K_TAB:
                        self.settings_tab = "BRILHO" if self.settings_tab == "SOM" else "SOM"
                    elif event.key == pygame.K_LEFT:
                        self.adjust_active_setting(-0.05)
                    elif event.key == pygame.K_RIGHT:
                        self.adjust_active_setting(0.05)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if getattr(self, "tab_sound_rect", None) and self.tab_sound_rect.collidepoint(event.pos):
                        self.settings_tab = "SOM"
                    elif getattr(self, "tab_bright_rect", None) and self.tab_bright_rect.collidepoint(event.pos):
                        self.settings_tab = "BRILHO"
                    elif getattr(self, "btn_minus", None) and self.btn_minus.collidepoint(event.pos):
                        self.adjust_active_setting(-0.1)
                    elif getattr(self, "btn_plus", None) and self.btn_plus.collidepoint(event.pos):
                        self.adjust_active_setting(0.1)
                    elif getattr(self, "slider_bar_rect", None) and self.slider_bar_rect.collidepoint(event.pos):
                        rel = (event.pos[0] - self.slider_bar_rect.x) / self.slider_bar_rect.width
                        if self.settings_tab == "SOM":
                            self.sound.set_volume(rel)
                        else:
                            self.brightness = 0.3 + max(0.0, min(1.0, rel)) * 1.0
                    elif getattr(self, "btn_settings_back", None) and self.btn_settings_back.collidepoint(event.pos):
                        self.state = "MENU"

            # ---- RECORDES ----
            elif self.state == "HIGHSCORES":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.state = "MENU"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if getattr(self, "btn_highscores_back", None) and self.btn_highscores_back.collidepoint(event.pos):
                        self.state = "MENU"

            # ---- GAMEPLAY ----
            elif self.state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                    elif event.key in (pygame.K_SPACE, pygame.K_TAB, pygame.K_LSHIFT, pygame.K_RSHIFT):
                        # Ativa uma carga da Ampulheta!
                        self.activate_hourglass_power()
                    elif event.unicode:
                        self.handle_typing_Char(event.unicode)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.hourglass_hud_rect.collidepoint(event.pos):
                        self.activate_hourglass_power()

            # ---- GAME OVER / VITORIA ----
            elif self.state in ("GAMEOVER", "VICTORY"):
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self.state = "MENU"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if getattr(self, "btn_end_menu", None) and self.btn_end_menu.collidepoint(event.pos):
                        self.state = "MENU"

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            time_sec = pygame.time.get_ticks() / 1000.0

            self.handle_events()
            self.background.update(dt if (self.state != "PLAYING" or self.time_stop_timer <= 0.0) else 0.0)

            if self.state == "PLAYING":
                self.update_gameplay(dt, time_sec)

            # Renderizacao
            self.background.draw(self.screen, time_sec)

            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "USERNAME":
                self.draw_username_screen()
            elif self.state == "SETTINGS":
                self.draw_settings_screen()
            elif self.state == "HIGHSCORES":
                self.draw_highscores_screen()
            elif self.state == "PLAYING":
                self.draw_gameplay(time_sec)
            elif self.state == "GAMEOVER":
                self.draw_end_screen(is_victory=False)
            elif self.state == "VICTORY":
                self.draw_end_screen(is_victory=True)

            self.apply_brightness_overlay()
            pygame.display.flip()


if __name__ == "__main__":
    game = ZSpaceGame()
    game.run()
