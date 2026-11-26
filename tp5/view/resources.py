"""VIEW: loads the images and sounds of the current theme.
The only file that knows where the resource files are."""
import math
import os
import pygame
import settings as cfg

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Assets:
    def __init__(self, theme=None):
        self.root = os.path.join(PROJECT_ROOT, cfg.ASSETS_DIR)
        self.theme = theme or cfg.THEME
        self.background = "background"
        self._images, self._sounds = {}, {}
        self._reset_background()

    @property
    def base(self):
        return os.path.join(self.root, self.theme)

    # ------------------------------------------------ themes and backgrounds
    def themes(self):
        if not os.path.isdir(self.root):
            return []
        return sorted(d for d in os.listdir(self.root)
                      if os.path.isdir(os.path.join(self.root, d)))

    def set_theme(self, name):
        self.theme = name
        self._images.clear()
        self._sounds.clear()
        self._reset_background()

    def next_theme(self):
        names = self.themes()
        if names:
            i = names.index(self.theme) if self.theme in names else -1
            self.set_theme(names[(i + 1) % len(names)])

    def backgrounds(self):
        folder = os.path.join(self.base, "backgrounds")
        if not os.path.isdir(folder):
            return []
        return sorted(f[:-4] for f in os.listdir(folder) if f.lower().endswith(".png"))

    def _reset_background(self):
        names = self.backgrounds()
        self.background = "background" if "background" in names or not names else names[0]

    def next_background(self):
        names = self.backgrounds()
        if names:
            i = names.index(self.background) if self.background in names else -1
            self.background = names[(i + 1) % len(names)]

    # ------------------------------------------------------ images and sounds
    @staticmethod
    def _clean(img):
        """Remove a solid background (connected to the top-left pixel), then crop the empty margins."""
        corner = img.get_at((0, 0))
        if corner.a == 255:                                   # opaque background
            same = pygame.mask.from_threshold(img, corner, (12, 12, 12, 255))
            region = same.connected_component((0, 0))         # only the part touching the corner
            cut = region.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(255, 255, 255, 255))
            img.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        rect = img.get_bounding_rect()
        return img.subsurface(rect).copy() if rect.width and rect.height else img

    def image(self, category, name, size=None):
        """A pygame Surface, or None if the file (or the window) doesn't exist.
        size: a number = fit inside a size x size box (proportions kept),
              a (w, h) tuple = exact size (used for backgrounds)."""
        if pygame.display.get_surface() is None:
            return None
        if isinstance(size, float):
            size = round(size)
        key = (category, name, size)
        if key not in self._images:
            path = os.path.join(self.base, category, name + ".png")
            img = None
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if isinstance(size, int):
                    img = self._clean(img)
                    w, h = img.get_size()
                    k = size / max(w, h)
                    img = pygame.transform.smoothscale(
                        img, (max(1, round(w * k)), max(1, round(h * k))))
                elif size:
                    img = pygame.transform.smoothscale(img, size)
            self._images[key] = img
        return self._images[key]

    def cover(self, category, name, size):
        """Fill `size` with the image without distorting it (the extra is cropped)."""
        key = (category, name, "cover", size)
        if key in self._images:
            return self._images[key]
        src = self.image(category, name)
        if src is None:
            return None
        w, h = src.get_size()
        k = max(size[0] / w, size[1] / h)
        scaled = pygame.transform.smoothscale(src, (math.ceil(w * k), math.ceil(h * k)))
        rect = pygame.Rect((0, 0), size)
        rect.center = scaled.get_rect().center
        rect.clamp_ip(scaled.get_rect())
        self._images[key] = scaled.subsurface(rect).copy()
        return self._images[key]

    def blit(self, screen, category, name, pos, size, angle=0):
        """Draw a centered image. Returns False if there is none (caller draws its shape)."""
        img = self.image(category, name, size)
        if img is None:
            return False
        if angle:
            img = pygame.transform.rotate(img, angle)
        screen.blit(img, img.get_rect(center=(pos.x, pos.y)))
        return True

    def sound(self, name):
        if name not in self._sounds:
            path = os.path.join(self.base, "sounds", name + ".wav")
            ok = os.path.exists(path) and pygame.mixer.get_init()
            self._sounds[name] = pygame.mixer.Sound(path) if ok else None
        return self._sounds[name]

    def play(self, name):
        s = self.sound(name)
        if s:
            s.play()


assets = Assets()      # one shared instance, images load lazily (after the window exists)
