from __future__ import annotations

from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True, slots=True)
class RetryStrategyProfile:
    name: str
    prompt_suffix: str


@dataclass(frozen=True, slots=True)
class SinglePanelValidationResult:
    decision: str
    reason: str | None = None
    validator_name: str = "SinglePanelHeuristicValidator"
    validator_mode: str = "heuristic"


DEFAULT_RETRY_STRATEGIES = (
    RetryStrategyProfile("standard", ""),
    RetryStrategyProfile(
        "strict_single_scene",
        "\nRetry strategy: keep only one visible moment, one subject focus, and one undivided scene.",
    ),
    RetryStrategyProfile(
        "minimal_snapshot",
        "\nRetry strategy: reduce the image to one frozen instant with no extra scene elements and no visual subdivision.",
    ),
)


class SinglePanelHeuristicValidator:
    name = "SinglePanelHeuristicValidator"
    mode = "heuristic"

    def validate(self, image: Image.Image) -> SinglePanelValidationResult:
        rgb_image = image.convert("RGB")
        width, height = rgb_image.size
        internal_verticals = _internal_divider_lines(rgb_image, axis="vertical")
        internal_horizontals = _internal_divider_lines(rgb_image, axis="horizontal")
        if internal_verticals and internal_horizontals:
            return SinglePanelValidationResult(
                decision="rejected",
                reason="detected internal vertical and horizontal divider lines",
                validator_name=self.name,
                validator_mode=self.mode,
            )
        if len(internal_verticals) >= 2 or len(internal_horizontals) >= 2:
            return SinglePanelValidationResult(
                decision="rejected",
                reason="detected repeated internal divider lines",
                validator_name=self.name,
                validator_mode=self.mode,
            )
        if width < 32 or height < 32:
            return SinglePanelValidationResult(
                decision="ambiguous",
                reason="image too small for reliable single-panel validation",
                validator_name=self.name,
                validator_mode=self.mode,
            )
        if _has_seamless_multi_panel_split(rgb_image):
            return SinglePanelValidationResult(
                decision="rejected",
                reason="detected probable seamless multi-panel layout",
                validator_name=self.name,
                validator_mode=self.mode,
            )
        return SinglePanelValidationResult(
            decision="accepted",
            validator_name=self.name,
            validator_mode=self.mode,
        )


def get_retry_strategies() -> tuple[RetryStrategyProfile, ...]:
    return DEFAULT_RETRY_STRATEGIES


def apply_retry_strategy(prompt: str, strategy: RetryStrategyProfile) -> str:
    if not strategy.prompt_suffix:
        return prompt
    return f"{prompt}{strategy.prompt_suffix}"


def _internal_divider_lines(image: Image.Image, axis: str) -> list[int]:
    dark_lines = _internal_dark_lines(image, axis=axis)
    light_lines = _internal_light_lines(image, axis=axis)
    return _dedupe_nearby_lines(sorted(dark_lines + light_lines))


def _internal_dark_lines(image: Image.Image, axis: str) -> list[int]:
    width, height = image.size
    start_x = max(1, int(width * 0.1))
    end_x = min(width - 1, int(width * 0.9))
    start_y = max(1, int(height * 0.1))
    end_y = min(height - 1, int(height * 0.9))
    dark_threshold = 35
    coverage_threshold = 0.92
    matches: list[int] = []

    if axis == "vertical":
        for x in range(start_x, end_x):
            dark_pixels = 0
            total = end_y - start_y
            for y in range(start_y, end_y):
                r, g, b = image.getpixel((x, y))
                if r <= dark_threshold and g <= dark_threshold and b <= dark_threshold:
                    dark_pixels += 1
            if total > 0 and dark_pixels / total >= coverage_threshold:
                matches.append(x)
    else:
        for y in range(start_y, end_y):
            dark_pixels = 0
            total = end_x - start_x
            for x in range(start_x, end_x):
                r, g, b = image.getpixel((x, y))
                if r <= dark_threshold and g <= dark_threshold and b <= dark_threshold:
                    dark_pixels += 1
            if total > 0 and dark_pixels / total >= coverage_threshold:
                matches.append(y)
    return _dedupe_nearby_lines(matches)


def _internal_light_lines(image: Image.Image, axis: str) -> list[int]:
    width, height = image.size
    start_x = max(2, int(width * 0.1))
    end_x = min(width - 2, int(width * 0.9))
    start_y = max(2, int(height * 0.1))
    end_y = min(height - 2, int(height * 0.9))
    light_threshold = 235
    coverage_threshold = 0.97
    neighbor_gap = 35
    matches: list[int] = []

    if axis == "vertical":
        for x in range(start_x, end_x):
            total = end_y - start_y
            if total <= 0:
                continue
            light_pixels = 0
            for y in range(start_y, end_y):
                r, g, b = image.getpixel((x, y))
                if r >= light_threshold and g >= light_threshold and b >= light_threshold:
                    light_pixels += 1
            if light_pixels / total < coverage_threshold:
                continue
            if _column_neighbor_gap(image, x, start_y, end_y) >= neighbor_gap:
                matches.append(x)
    else:
        for y in range(start_y, end_y):
            total = end_x - start_x
            if total <= 0:
                continue
            light_pixels = 0
            for x in range(start_x, end_x):
                r, g, b = image.getpixel((x, y))
                if r >= light_threshold and g >= light_threshold and b >= light_threshold:
                    light_pixels += 1
            if light_pixels / total < coverage_threshold:
                continue
            if _row_neighbor_gap(image, y, start_x, end_x) >= neighbor_gap:
                matches.append(y)
    return _dedupe_nearby_lines(matches)


def _column_neighbor_gap(image: Image.Image, x: int, start_y: int, end_y: int) -> float:
    left = _column_brightness(image, x - 1, start_y, end_y)
    center = _column_brightness(image, x, start_y, end_y)
    right = _column_brightness(image, x + 1, start_y, end_y)
    return center - max(left, right)


def _row_neighbor_gap(image: Image.Image, y: int, start_x: int, end_x: int) -> float:
    above = _row_brightness(image, y - 1, start_x, end_x)
    center = _row_brightness(image, y, start_x, end_x)
    below = _row_brightness(image, y + 1, start_x, end_x)
    return center - max(above, below)


def _column_brightness(image: Image.Image, x: int, start_y: int, end_y: int) -> float:
    total = 0.0
    count = 0
    for y in range(start_y, end_y):
        r, g, b = image.getpixel((x, y))
        total += (r + g + b) / 3
        count += 1
    return total / count if count else 0.0


def _row_brightness(image: Image.Image, y: int, start_x: int, end_x: int) -> float:
    total = 0.0
    count = 0
    for x in range(start_x, end_x):
        r, g, b = image.getpixel((x, y))
        total += (r + g + b) / 3
        count += 1
    return total / count if count else 0.0


def _has_seamless_multi_panel_split(image: Image.Image) -> bool:
    width, height = image.size
    center_x = width // 2
    center_y = height // 2
    if center_x < 8 or center_y < 8:
        return False
    vertical_score = _seam_discontinuity_score(image, axis="vertical", position=center_x)
    horizontal_score = _seam_discontinuity_score(image, axis="horizontal", position=center_y)
    neighboring_vertical = _neighboring_seam_baseline(image, axis="vertical", position=center_x)
    neighboring_horizontal = _neighboring_seam_baseline(image, axis="horizontal", position=center_y)
    return (
        vertical_score >= 55.0
        and horizontal_score >= 55.0
        and vertical_score >= neighboring_vertical + 18.0
        and horizontal_score >= neighboring_horizontal + 18.0
    )


def _neighboring_seam_baseline(image: Image.Image, axis: str, position: int) -> float:
    limit = image.size[0] if axis == "vertical" else image.size[1]
    offsets = (-48, -32, -16, 16, 32, 48)
    scores: list[float] = []
    for offset in offsets:
        probe = position + offset
        if probe <= 1 or probe >= limit - 1:
            continue
        scores.append(_seam_discontinuity_score(image, axis=axis, position=probe))
    if not scores:
        return 0.0
    scores.sort()
    return scores[len(scores) // 2]


def _seam_discontinuity_score(image: Image.Image, axis: str, position: int) -> float:
    width, height = image.size
    if axis == "vertical":
        start_y = max(1, int(height * 0.1))
        end_y = min(height - 1, int(height * 0.9))
        total = 0.0
        count = 0
        for y in range(start_y, end_y):
            total += _pixel_distance(image.getpixel((position - 1, y)), image.getpixel((position, y)))
            count += 1
        return total / count if count else 0.0
    start_x = max(1, int(width * 0.1))
    end_x = min(width - 1, int(width * 0.9))
    total = 0.0
    count = 0
    for x in range(start_x, end_x):
        total += _pixel_distance(image.getpixel((x, position - 1)), image.getpixel((x, position)))
        count += 1
    return total / count if count else 0.0


def _pixel_distance(left: tuple[int, int, int], right: tuple[int, int, int]) -> float:
    return (abs(left[0] - right[0]) + abs(left[1] - right[1]) + abs(left[2] - right[2])) / 3.0


def _dedupe_nearby_lines(values: list[int], tolerance: int = 4) -> list[int]:
    deduped: list[int] = []
    for value in values:
        if not deduped or value - deduped[-1] > tolerance:
            deduped.append(value)
    return deduped
