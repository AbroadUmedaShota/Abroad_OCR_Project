def calculate_iou(bbox1: list, bbox2: list) -> float:
    """
    Calculates the Intersection over Union (IoU) of two bounding boxes.
    Bounding boxes are expected in the format [x_min, y_min, x_max, y_max].
    """
    # Determine the coordinates of the intersection rectangle
    x_left = max(bbox1[0], bbox2[0])
    y_top = max(bbox1[1], bbox2[1])
    x_right = min(bbox1[2], bbox2[2])
    y_bottom = min(bbox1[3], bbox2[3])

    # If no intersection, return 0
    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # Calculate intersection area
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # Calculate union area
    bbox1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
    bbox2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
    union_area = float(bbox1_area + bbox2_area - intersection_area)

    # Avoid division by zero
    if union_area == 0:
        return 0.0

    return intersection_area / union_area


if __name__ == '__main__':
    # Example Usage:
    box1 = [0, 0, 10, 10]  # Example bounding box 1
    box2 = [5, 5, 15, 15]  # Example bounding box 2
    iou_score = calculate_iou(box1, box2)
    print(f"IoU between {box1} and {box2}: {iou_score:.4f}")

    box3 = [0, 0, 10, 10]
    box4 = [10, 10, 20, 20] # Touching at one point
    iou_score2 = calculate_iou(box3, box4)
    print(f"IoU between {box3} and {box4}: {iou_score2:.4f}")

    box5 = [0, 0, 10, 10]
    box6 = [11, 11, 20, 20] # No overlap
    iou_score3 = calculate_iou(box5, box6)
    print(f"IoU between {box5} and {box6}: {iou_score3:.4f}")

    # Example with lists of bboxes (simplified for demonstration)
    # In a real scenario, you'd need a more complex matching algorithm for lists of bboxes.
    # This function is designed for single bbox comparison.
    # For lists, you'd iterate and match bboxes, then average/aggregate IoU.
    gt_bboxes_list = [[0,0,10,10], [20,20,30,30]]
    ocr_bboxes_list = [[0,0,9,9], [21,21,29,29]]
    
    # Simplified IoU for lists (average of pairwise, assuming order matches)
    if len(gt_bboxes_list) == len(ocr_bboxes_list):
        total_iou = 0
        for i in range(len(gt_bboxes_list)):
            total_iou += calculate_iou(gt_bboxes_list[i], ocr_bboxes_list[i])
        avg_iou_list = total_iou / len(gt_bboxes_list)
        print(f"\nAverage IoU for lists (simplified): {avg_iou_list:.4f}")
    else:
        print("\nCannot calculate average IoU for lists of different lengths without a matching algorithm.")