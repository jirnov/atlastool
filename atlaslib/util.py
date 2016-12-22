# coding: utf-8

class Size(object):
    '''Представление для размера'''
    
    def __init__(self, width, height):
        '''Инициализация.'''
        assert width >= 0 and height >= 0, 'Invalid size'
        self.__width = width
        self.__height = height
    
    @property
    def width(self):
        '''Ширина.'''
        return self.__width
    
    @property
    def height(self):
        '''Высота.'''
        return self.__height

    @property
    def dimensionsSum(self):
        '''Сумма высоты и ширины.'''
        return self.__width + self.__height
    
    @property
    def sizeTuple(self):
        '''Размеры в виде tuple (ширина, высота).'''
        return (self.__width, self.__height)
    
    def canFit(self, size):
        '''Проверка, может ли область вместить другую область.'''
        assert isinstance(size, Size), 'Size must be Size instance'
        return self.width >= size.width and self.height >= size.height
    
    def __str__(self):
        '''Строковое представление.'''
        return '%d x %d' % (self.__width, self.__height)
    

class Point(object):
    '''Представление для точки на плоскости'''
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
    
    @property
    def x(self):
        return self.__x
    
    @property
    def y(self):
        return self.__y
    
    @property
    def pointTuple(self):
        '''Координаты в виде tuple (x, y).'''
        return (self.__x, self.__y)
    
    def __str__(self):
        '''Строковое представление.'''
        return '(%d, %d)' % (self.__x, self.__y)
    

class Rect(object):
    '''Прямоугольная область'''
    
    def __init__(self, origin, size):
        '''
        Инициализация прямоугольной области.
            origin  координата верхнего левого угла
            size    размер области
        '''
        assert isinstance(origin, Point), 'Origin must be Point instance'
        assert isinstance(size, Size), 'Size must be Size instance'
        self.__origin = origin
        self.__size = size
    
    @property
    def origin(self):
        '''Координаты верхнего левого угла.'''
        return self.__origin
    
    @property
    def size(self):
        '''Размер.'''
        return self.__size
    
    @property
    def coordinateTuple(self):
        '''Возвращает tuple с координатами левого верхнего и правого нижнего углов.'''
        return (self.__origin.x, self.__origin.y, self.__origin.x + self.__size.width, self.__origin.y + self.__size.height)
    
    def canFit(self, size):
        '''Проверка, может ли область вместить другую область с заданным размером.'''
        assert isinstance(size, Size), 'Size must be Size instance'
        return self.__size.canFit(size)
    
