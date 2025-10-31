def calculate_iou(box1, box2):
    """Calculates the Intersection over Union (IoU) of two bounding boxes.

    Args:
        box1 (list): A list of 4 floats representing [x0, y0, x1, y1] of the first box.
        box2 (list): A list of 4 floats representing [x0, y0, x1, y1] of the second box.

    Returns:
        float: The IoU value, a float between 0 and 1.
    """
    # Determine the coordinates of the intersection rectangle
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    # Compute the area of intersection rectangle
    intersection_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)

    # Compute the area of both bounding boxes
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    # Compute the area of union
    union_area = float(box1_area + box2_area - intersection_area)

    # Handle case where union_area is zero to avoid division by zero
    if union_area == 0:
        return 0.0

    # Compute the IoU
    iou = intersection_area / union_area

    return iou
