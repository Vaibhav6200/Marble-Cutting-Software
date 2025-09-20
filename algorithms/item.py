"""
2D Item class.
"""
class Item:
    """
    Items class for rectangles inserted into sheets
    """
    def __init__(self, width, height,
                 CornerPoint: tuple = (0, 0),
                 rotation: bool = True) -> None:
        self.width = width
        self.height = height
        self.x = CornerPoint[0]
        self.y = CornerPoint[1]
        self.area = self.width * self.height
        self.rotated = False
        self.id = 0


    def __repr__(self):
        return 'Item(width=%r, height=%r, x=%r, y=%r)' % (self.width, self.height, self.x, self.y)


    def rotate(self) -> None:
        self.width, self.height = self.height, self.width
        self.rotated = False if self.rotated == True else True


class CustomItem(Item):
    """
    Customized Item class to include additional attributes: code, polish_edge_l, and polish_edge_w.
    """
    def __init__(self, width, height, code, polish_edge_l, polish_edge_w, CornerPoint=(0, 0), rotation=True):
        super().__init__(width, height, CornerPoint, rotation)
        self.code = code
        self.polish_edge_l = polish_edge_l
        self.polish_edge_w = polish_edge_w

    def __repr__(self):
        return (f'CustomItem(width={self.width!r}, height={self.height!r}, x={self.x!r}, y={self.y!r}, '
                f'code={self.code!r}, polish_edge_l={self.polish_edge_l!r}, polish_edge_w={self.polish_edge_w!r})')

    def rotate(self):
        super().rotate()
