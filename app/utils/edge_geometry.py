# ---------------------------------------------------
# Project: Asteroid
# Author: Daryll Lorenzo Alfonso
# Year: 2025
# License: MIT License
# ---------------------------------------------------

"""Pure polyline/arrow geometry math, independent of any Qt scene state."""

import math

from PyQt6.QtCore import QPointF

Segment = tuple[QPointF, QPointF, float]


def point_to_segment_distance(
    point: QPointF, line_start: QPointF, line_end: QPointF
) -> float:
    """Shortest distance from point to the segment [line_start, line_end]."""
    dx = line_end.x() - line_start.x()
    dy = line_end.y() - line_start.y()

    if dx == 0 and dy == 0:
        return math.hypot(point.x() - line_start.x(), point.y() - line_start.y())

    t = ((point.x() - line_start.x()) * dx + (point.y() - line_start.y()) * dy) / (
        dx * dx + dy * dy
    )
    t = max(0, min(1, t))

    closest_x = line_start.x() + t * dx
    closest_y = line_start.y() + t * dy

    return math.hypot(point.x() - closest_x, point.y() - closest_y)


def path_segments(points: list[QPointF]) -> list[Segment]:
    """Consecutive (start, end, length) segments along a polyline."""
    if len(points) < 2:
        return []

    segments: list[Segment] = []
    for p1, p2 in zip(points, points[1:], strict=False):
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        segments.append((p1, p2, math.hypot(dx, dy)))
    return segments


def point_at_distance(
    segments: list[Segment], distance: float
) -> tuple[QPointF, float]:
    """Point and tangent angle (radians) at `distance` along `segments`."""
    if not segments:
        return QPointF(0, 0), 0.0

    total_length = sum(seg[2] for seg in segments)
    if total_length == 0:
        return QPointF(0, 0), 0.0

    if distance >= total_length:
        last_seg = segments[-1]
        angle = math.atan2(
            last_seg[1].y() - last_seg[0].y(), last_seg[1].x() - last_seg[0].x()
        )
        return last_seg[1], angle

    accumulated = 0.0
    for p1, p2, seg_length in segments:
        if accumulated + seg_length >= distance:
            t = (distance - accumulated) / seg_length if seg_length > 0 else 0
            x = p1.x() + t * (p2.x() - p1.x())
            y = p1.y() + t * (p2.y() - p1.y())
            angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
            return QPointF(x, y), angle
        accumulated += seg_length

    last_seg = segments[-1]
    angle = math.atan2(
        last_seg[1].y() - last_seg[0].y(), last_seg[1].x() - last_seg[0].x()
    )
    return last_seg[1], angle


def point_at_percentage(
    segments: list[Segment], percentage: float
) -> tuple[QPointF, float]:
    """Point and tangent angle (radians) at `percentage` (0..1) along `segments`."""
    if not segments:
        return QPointF(0, 0), 0.0

    total_length = sum(seg[2] for seg in segments)
    if total_length == 0:
        return QPointF(0, 0), 0.0

    return point_at_distance(segments, total_length * percentage)


def border_point(node_pos: QPointF, radius: float, target_pos: QPointF) -> QPointF:
    """Point on a circle of `radius` centered at `node_pos`, facing `target_pos`."""
    dx = target_pos.x() - node_pos.x()
    dy = target_pos.y() - node_pos.y()

    distance = math.sqrt(dx * dx + dy * dy)
    if distance == 0:
        return node_pos

    scale_factor = radius / distance
    return QPointF(node_pos.x() + dx * scale_factor, node_pos.y() + dy * scale_factor)


def arrow_head_points(
    line_start: QPointF, line_end: QPointF, arrow_size: float
) -> tuple[QPointF, QPointF, QPointF] | None:
    """The 3 triangle points of an arrow head at `line_end`, facing along the line."""
    dx = line_end.x() - line_start.x()
    dy = line_end.y() - line_start.y()

    if dx == 0 and dy == 0:
        return None

    angle = math.atan2(dy, dx)

    adjusted_end = QPointF(
        line_end.x() - arrow_size * 0.5 * math.cos(angle),
        line_end.y() - arrow_size * 0.5 * math.sin(angle),
    )
    p1 = QPointF(
        adjusted_end.x() - arrow_size * math.cos(angle - math.pi / 6),
        adjusted_end.y() - arrow_size * math.sin(angle - math.pi / 6),
    )
    p2 = QPointF(
        adjusted_end.x() - arrow_size * math.cos(angle + math.pi / 6),
        adjusted_end.y() - arrow_size * math.sin(angle + math.pi / 6),
    )
    return adjusted_end, p1, p2
