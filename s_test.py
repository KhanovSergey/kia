class Rectangle:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @property
    def area(self):
        return self.a * self.b


rect = Rectangle(5, 6)
print(rect)
print(rect.area)
