import math
import random
from typing import List, Optional, Tuple

from scipy.spatial.distance import cityblock

from logis.data_type import Point


def manhattan_distance(start_point: Point, end_point: Point) -> float:
    """
    计算曼哈顿距离，又称为街道距离
    """
    return float(cityblock(start_point.to_tuple(), end_point.to_tuple()))
    distance = abs(start_point.x - end_point.x) + abs(start_point.y - end_point.y)
    return distance


def euclid_distance(pos1: Point, pos2: Point, precision: Optional[int] = None) -> float:
    """计算欧几里得距离"""
    v = math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)
    return round(v, precision) if precision is not None else v


def vector_between_points(p1: Point, p2: Point) -> Tuple[float, float]:
    """计算两点之间的向量。"""
    return p2.x - p1.x, p2.y - p1.y


def angle_between_vectors(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    """计算两个向量之间的夹角（弧度）。"""
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude_product = math.sqrt(v1[0] ** 2 + v1[1] ** 2) * math.sqrt(
        v2[0] ** 2 + v2[1] ** 2
    )
    if magnitude_product == 0:
        return 0
    cos_theta = dot_product / magnitude_product
    cos_theta = max(-1, min(1, cos_theta))  # 避免数值误差导致超出 [-1, 1] 范围
    return math.acos(cos_theta)


def intersection_calculate(
    line1_p1: Point, line1_p2: Point, seg_p1: Point, seg_p2: Point
) -> Optional[Point]:
    """计算两条线段的交点"""
    x1, y1 = line1_p1.x, line1_p1.y
    x2, y2 = line1_p2.x, line1_p2.y
    x3, y3 = seg_p1.x, seg_p1.y
    x4, y4 = seg_p2.x, seg_p2.y

    det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if det == 0:
        return None  # 平行或共线

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / det
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / det

    if 0 <= t <= 1 and 0 <= u <= 1:
        intersect_x = x1 + t * (x2 - x1)
        intersect_y = y1 + t * (y2 - y1)
        return Point(intersect_x, intersect_y)

    return None


def _is_point_on_edge(p1: Point, p2: Point, new_pt: Point, eps=1e-2) -> bool:
    """精确判断点是否在边上（含端点）"""

    # 共线性检查
    cross = (p2.x - p1.x) * (new_pt.y - p1.y) - (p2.y - p1.y) * (new_pt.x - p1.x)
    segment_length = math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
    if segment_length == 0:
        return False  # 线段长度为0
    normalized_cross = abs(cross) / segment_length

    # 判断共线性
    if normalized_cross > eps:
        return False

    # 判断点是否在线段范围内
    dist_p1p2 = segment_length
    dist_p1new = math.sqrt((new_pt.x - p1.x) ** 2 + (new_pt.y - p1.y) ** 2)
    dist_p2new = math.sqrt((new_pt.x - p2.x) ** 2 + (new_pt.y - p2.y) ** 2)
    return abs(dist_p1p2 - (dist_p1new + dist_p2new)) < eps


def uniform_point_in_rectangle(N, center_x, center_y, length, width, rotation_deg=0):
    """
    在矩形内生成均匀分布的点坐标

    参数：
    N (int) - 需要生成的点数
    center_x, center_y (float) - 矩形中心坐标
    length (float) - 矩形长度（旋转前X轴方向）
    width (float) - 矩形宽度（旋转前Y轴方向）
    rotation_deg (float) - 矩形旋转角度（度数，默认0度）

    返回：
    list - 包含N个坐标元组(x, y)的列表
    """
    if N <= 0:
        return []

    # 转换为弧度
    theta = math.radians(rotation_deg)
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)

    # 计算行列布局（考虑长宽比优化）
    aspect_ratio = length / width
    cols = max(1, math.ceil(math.sqrt(N * aspect_ratio)))  # 初步列数
    rows = max(1, math.ceil(N / cols))  # 初步行数

    # 优化行列组合（确保足够容纳N个点）
    while rows * cols < N:
        cols += 1
        rows = max(1, math.ceil(N / cols))

    # 计算单元格尺寸
    cell_width = length / cols
    cell_height = width / rows

    # 生成基础网格点（未旋转）
    points = []
    for row in range(rows):
        for col in range(cols):
            # 计算单元格中心坐标（基于未旋转的坐标系）
            x = col * cell_width + cell_width / 2 - length / 2
            y = row * cell_height + cell_height / 2 - width / 2
            points.append((x, y))
            if len(points) >= N:
                break
        if len(points) >= N:
            break

    # 应用旋转和平移变换
    rotated_points = []
    for x, y in points[:N]:
        # 坐标旋转
        x_rot = x * cos_theta - y * sin_theta
        y_rot = x * sin_theta + y * cos_theta

        # 平移至中心点
        x_final = x_rot + center_x
        y_final = y_rot + center_y

        rotated_points.append(Point((round(x_final, 4), round(y_final, 4))))

    return rotated_points


def random_points_in_rectangle(N, center_x, center_y, length, width, rotation_deg=0):
    """在旋转后的矩形内部生成随机分布的坐标点"""
    points = []
    angle_rad = math.radians(rotation_deg)
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)

    half_length = length / 2
    half_width = width / 2

    for _ in range(N):
        local_x = random.uniform(-half_length, half_length)
        local_y = random.uniform(-half_width, half_width)

        rotated_x = local_x * cos_theta - local_y * sin_theta
        rotated_y = local_x * sin_theta + local_y * cos_theta

        global_x = center_x + rotated_x
        global_y = center_y + rotated_y

        points.append(Point((global_x, global_y)))

    return points


import math


def vector_length_square(vec: List[float]):
    return sum([x * x for x in vec])


def vector_length(vec: List[float]) -> float:
    return math.sqrt(vector_length_square(vec))


def unit_vector(vec: List[float]) -> List[float]:
    l = vector_length(vec)
    if l == 0:
        raise ZeroDivisionError("zero vector has no unit vector")

    return tuple([x / l for x in vec])


def vector_to(starter: Point, ender: Point) -> Tuple[float, float]:
    return tuple([x - y for (x, y) in zip((ender.x, ender.y), (starter.x, starter.y))])


def vector_add(v1: List[float], v2: List[float]) -> List[float]:
    return tuple([x + y for (x, y) in zip(v1, v2)])


def vector_mul(v: List[float], la: float) -> List[float]:
    return tuple([x * la for x in v])


def weighted_midpoint(starter: Point, ender: Point, la: float):
    """
    gives the point mid so that
    starter-> mid = la * (starter->ender)
    """

    return vector_add(starter, vector_mul(vector_to(starter, ender), la))


def point_on_segment_left_flag(pt, p1, p2):
    """returns pos num if point is on the left side of the segment p1->p2.
    Require points lie on 2d plane."""
    return (p2[0] - p1[0]) * (pt[1] - p1[1]) - (p2[1] - p1[1]) * (pt[0] - p1[0])


def seg_on_seg_same_side(p1, p2, p3, p4):
    """
    returns true if both  p3,p4 lie on the same side of the line p1->p2,
        Require points lie on 2d plane.

    """
    return (
        point_on_segment_left_flag(p1, p3, p4) * point_on_segment_left_flag(p2, p3, p4)
        > 0
    )


def segment_intersection(p1, p2, p3, p4):
    """
    strictly test if intersection happens. Endpoint lie on segment also counts.
    """
    if seg_on_seg_same_side(p1, p2, p3, p4) or seg_on_seg_same_side(p3, p4, p1, p2):
        return False
    else:
        return True


def linear_movement_time(pos1, pos2, velocity):
    assert velocity > 0, f"non-positive velocity {velocity}"

    result = euclid_distance(pos1, pos2) / velocity
    # printpos1, pos2, velocity, result )
    return result


def linear_movement_gen(pos1, pos2, start_t2, total_t1):
    assert total_t1 >= 0, "required to move within negative time"
    if total_t1 == 0:
        assert pos1 == pos2, "required to move within zero time"
        return lambda t: pos1

    def result(check_t2):  ## position at check_time

        ratio = (
            float(check_t2 - start_t2) / total_t1
        )  ## total t must be a number, not timeagain
        assert (
            ratio <= 1.01
        ), f"time exceeds movement requirement: {pos1} to {pos2}, start={start_t2}, time_alotted={total_t1}, at time={check_t2}, or {ratio}*t_a after start time"
        return [a + (b - a) * ratio for (a, b) in zip(pos1, pos2)]

    return result


def linear_stop_gen(pos1, pos2, start_t2, total_t1):
    assert total_t1 >= 0, "required to move within negative time"
    if total_t1 == 0:
        assert pos1 == pos2, "required to move within zero time"
        return lambda t: pos1

    def result(check_t2):

        ratio = (
            float(check_t2 - start_t2) / total_t1
        )  ## total t must be a number, not timeagain
        if ratio <= 1:
            return [a + (b - a) * ratio for (a, b) in zip(pos1, pos2)]
        else:
            return pos2

    return result


def wiz(v, z):
    # given z coordinate, make 2d pt v into a 3d pt.
    return tuple(list(v) + [z])


def wizz(v, height_list):
    # given height list, make a 2d point into a list of 3d pts.
    assert isinstance(height_list, list), f"height_list {height_list} is not a list "
    return [wiz(v, z) for z in height_list]

    ## So wizz result is [] if height_list is empty.


def angle_of_heading(v2):
    # given 2d vector, returns angle of heading in degrees.
    # essentially, it is alpha for exp(i*alpha)
    dx, dy = v2
    assert abs(dx) + abs(dy) >= 0.0001, f"heading vector {v2} almost zero"
    if dx == 0:
        if dy > 0:
            res = math.pi / 2
        else:
            res = 3 * math.pi / 2
    else:
        res = math.atan(dy / dx)
        if dx < 0:
            # either dy >0 or not, II and III quadrant
            res += math.pi
        elif dy < 0:  # and dx >0, IV quadrant
            res += math.pi * 2

    return res * 180 / math.pi
