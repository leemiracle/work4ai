def bresenham_line(x1, y1, x2, y2):
    points = []
    dx = (x2 - x1)
    dy = (y2 - y1)
    k= dy/dx
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    p = 2*dy - dx
    y0 = y1
    for x0 in range(x1, x2 + sx, sx):
        points.append((x0, y0))
        print(f"{x0}, {y0}, {p}, {k*x0:.2f}")
        if x0 == x2 and y0 == y2:
            break
        
        if p >= 0:
            y0 += sy
            p += 2*(dy-dx)
        else:
            p += 2*dy
        

    return points


if __name__ == "__main__":
    # input = (0, 0, 6, 3)
    input = (0, 0, 7, 2)
    # input = (0, 0, 7, 5)
    print("input: ",input)
    line = bresenham_line(*input)
    # line = bresenham_line(0, 0, 7, 2)
    # for point in line:
    #     print(point)
        
