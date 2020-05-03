import copy

class Vector(tuple): # 
    def __new__(self, x, yyy):
        return tuple.__new__(Vector, (x, yyy))

    def __copy__(self):
        return Vector(self.x, self.y)

    def __deepcopy__(self,memo):
        return Vector(self.x, self.y)

    @property
    def x(self):
        return self[0]
    
    @property
    def y(self):
        return self[1]

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def inverted(self, axis=0):
        return Vector(((axis * 2) - 1) * self.x, (1 - (axis * 2)) *  self.y)

    @staticmethod
    def fromDirection(str):
        x,y = 0,0
        for ch in str:
            if ch == 'B':
                y-=1
            if ch == 'F':
                y+=1
            if ch == 'L':
                x-=1
            if ch == 'R':
                x+=1
        return Vector(x,y)

    def asDirection(self):
        return "".join(["B"] * -self.y) \
             + "".join(["F"] * self.y) \
             + "".join(["L"] * -self.x) \
             + "".join(["R"] * self.x )