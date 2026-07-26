import math

def generate_thick_line(x1, y1, x2, y2, thickness=5, step=1):
    """
    Generates coordinate pairs forming a thick line between two points.
    
    x1, y1: start point
    x2, y2: end point
    thickness: pixels to each side of the line
    step: spacing between points along the line
    """
    coords = []

    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)

    # Unit direction vector along the line
    ux = dx / length
    uy = dy / length

    # Unit perpendicular vector
    px = -uy
    py = ux

    # Number of samples along the line
    num_steps = int(length / step)

    for i in range(num_steps + 1):
        t = i / num_steps
        cx = x1 + t * dx
        cy = y1 + t * dy

        # sweep -thickness to +thickness sideways
        for offset in range(-thickness, thickness + 1):
            ox = cx + offset * px
            oy = cy + offset * py
            coords.append((int(ox), int(oy)))

    return coords


coords = generate_thick_line(390, 711, 778, 1005)

print(coords)