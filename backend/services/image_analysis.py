"""
Gruha Alankara — Image Analysis Service
Uses OpenCV and NumPy for room image processing.
"""

import os
import uuid
import logging

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ImageAnalysisService:
    """Analyzes uploaded room images for layout, space, and characteristics."""

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_uploaded_image(self, file_storage) -> str:
        """Save an uploaded image file and return the stored filename."""
        filename = f"{uuid.uuid4().hex}.png"
        filepath = os.path.join(self.storage_dir, filename)
        file_storage.save(filepath)
        return filename

    def analyze(self, filename: str) -> dict:
        """Run full analysis pipeline on a room image."""
        filepath = os.path.join(self.storage_dir, filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Image not found: {filename}")

        img = cv2.imread(filepath)
        if img is None:
            raise ValueError("Could not read the image file")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = img.shape[:2]

        edges = self._detect_edges(gray)
        dominant_colors = self._extract_dominant_colors(img)
        brightness = self._estimate_brightness(gray)
        wall_ratio = self._estimate_wall_ratio(edges, height, width)
        floor_space = self._estimate_floor_space(edges, height, width)

        room_area_estimate = round((width * height) / 10000, 1)  # rough m² estimate

        return {
            "image_width": width,
            "image_height": height,
            "room_area_estimate_m2": room_area_estimate,
            "brightness": brightness,
            "dominant_colors": dominant_colors,
            "wall_ratio": wall_ratio,
            "floor_space_pct": floor_space,
            "edge_density": round(float(np.count_nonzero(edges)) / (height * width) * 100, 2),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _detect_edges(self, gray: np.ndarray) -> np.ndarray:
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        return cv2.Canny(blurred, 50, 150)

    def _extract_dominant_colors(self, img: np.ndarray, k: int = 4) -> list[str]:
        """Return top-k dominant colors as hex strings using k-means."""
        resized = cv2.resize(img, (64, 64))
        pixels = resized.reshape(-1, 3).astype(np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 4, cv2.KMEANS_RANDOM_CENTERS)

        centers = centers.astype(int)
        counts = np.bincount(labels.flatten())
        sorted_idx = np.argsort(-counts)

        hex_colors = []
        for idx in sorted_idx:
            b, g, r = centers[idx]
            hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")
        return hex_colors

    def _estimate_brightness(self, gray: np.ndarray) -> str:
        mean_val = float(np.mean(gray))
        if mean_val > 170:
            return "Bright"
        if mean_val > 110:
            return "Well-Lit"
        if mean_val > 60:
            return "Moderate"
        return "Dim"

    def _estimate_wall_ratio(self, edges: np.ndarray, h: int, w: int) -> float:
        """Rough wall-to-total ratio from top portion of image."""
        top_half = edges[: h // 2, :]
        return round(float(np.count_nonzero(top_half)) / (h // 2 * w) * 100, 2)

    def _estimate_floor_space(self, edges: np.ndarray, h: int, w: int) -> float:
        """Rough floor-space ratio from bottom portion of image."""
        bottom_third = edges[2 * h // 3 :, :]
        empty = (bottom_third.size - np.count_nonzero(bottom_third)) / bottom_third.size * 100
        return round(empty, 2)
