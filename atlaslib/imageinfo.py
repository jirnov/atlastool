# coding: utf-8
import os
import hashlib
from PIL import Image
from util import *

class AtlasImageInfo(object):
    '''Информация об изображении в атласе'''
    
    def __init__(self, imageName, imagePath, imageShortPath, alphaThreshold, padding):
        '''
        Инициализация.
            imageName    имя изображения в атласе.
            imagePath    путь к изображению.
            padding     размер пустого пространства между соседними изображениями.
        '''
        assert imageName, 'Invalid image name'
        assert os.path.exists(imagePath), 'Image cannot be found: "%s"' % imagePath
        assert padding >= 0, 'Padding must be positive or 0'
        
        self.__name = imageName
        self.__checksum = None
        self.__path = imagePath
        self.__shortPath=  imageShortPath
        self.__alphaThreshold = alphaThreshold
        self.__padding = padding
        self.__image = None
        self.__placed = False
        self.__loadImage(imagePath, True)
    
    @property
    def name(self):
        '''Имя изображения в атласе.'''
        return self.__name

    @property
    def shortPath(self):
        '''Короткий путь к файлу изображения.'''
        return self.__shortPath

    @property
    def path(self):
        '''Путь к файлу изображения.'''
        return self.__path
    
    @property
    def originalSize(self):
        '''Исходный размер изображения'''
        return self.__originalSize
    
    @property
    def sourceRect(self):
        '''Регион изображения, сохраняемый в атлас.'''
        return self.__sourceRect
    
    @property
    def paddedSourceRect(self):
        '''Регион изображения, сохраняемый в атлас с учетом расстояния между изображениями.'''
        return self.__paddedSourceRect

    @property
    def checksum(self):
        '''md5 от данных изображения'''
        if self.__checksum is None:
            self.__checksum = hashlib.md5(open(self.__path, 'rb').read()).hexdigest()
        return self.__checksum
    
    @property
    def atlasPosition(self):
        '''Координата верхнего левого угла (обрезанного) изображения в атласе.'''
        assert self.__placed, 'Image was not placed in atlas'
        return self.__atlasPosition
    
    def placeToAtlasImage(self, image, position, isDuplicate=False):
        '''
        Копирование (обрезанного) изображения в атлас и освобождение памяти под изображение.
            image          объект Image, в который копируется изображение
            atlasPosition  положение верхнего левого угла (обрезанного) изображения в атласе.
            isDuplicate    данное изображение уже есть в атласе
        '''
        assert isDuplicate or not self.__placed, 'Image already placed in atlas'
        assert isinstance(image, Image.Image), 'Image must be Image instance'
        assert isinstance(position, Point), 'AtlasPosition must be Point instance'
        assert isDuplicate or self.__image is not None, 'Image not loaded'
        
        if not isDuplicate:
            atlasImage = self.__image.crop(self.__sourceRect.coordinateTuple)
            image.paste(atlasImage, position.pointTuple)
        self.__atlasPosition = position
        self.__placed = True
        self.__image = None

    def isEqual(self, imageInfo):
        '''Сравнение двух изображений'''
        return self.checksum == imageInfo.checksum
    
    #
    # Приватные методы.
    #
    
    def __loadImage(self, imagePath, trim):
        '''
        Загрузка изображения.
            imagePath  путь к изображению.
            trim       нужно ли обрезать изображение по границе прозрачной области.
        '''
        assert self.__image is None, 'Image already loaded'
        assert not self.__placed, 'Image already placed in atlas'
        self.__image = Image.open(imagePath)
        self.__image.convert('RGBA')
        self.__originalSize = Size(*self.__image.size)
        if self.__originalSize.width <= 0 or self.__originalSize.height <= 0:
            raise Exception('Image "%s": invalid dimensions (%d x %d)' % \
                             (self.name, self.__originalSize.width, self.__originalSize.height))
        self.__sourceRect = Rect(Point(0, 0), self.__originalSize)
        if trim:
            self.__trim()
      	self.__paddedSourceRect = Rect(self.__sourceRect.origin, Size(self.__sourceRect.size.width + self.__padding,
	                                                                  self.__sourceRect.size.height + self.__padding))
    
    def __trim(self):
        '''
        Обрезание прозрачных краев изображения.
            alphaThreshold  пороговое значение прозрачности для обрезания краев.
        '''
        assert self.__image is not None, 'Image is not loaded'
        if self.__image.mode != 'RGBA':
            self.__image = self.__image.convert('RGBA')
        alphaThreshold = self.__alphaThreshold
        originalWidth, originalHeight = self.__originalSize.sizeTuple
        
        # Ищем левую границу.
        minX = self.__findBorder(xrange(originalWidth), 1,
                                 xrange(originalHeight), originalWidth, alphaThreshold)
        
        # Изображение полностью прозрачно.
        if minX is None:
            minX = maxX = 0
            minY = maxY = 0
        else:
            # Ищем остальные границы.
            maxX = self.__findBorder(xrange(originalWidth - 1, -1, -1), 1,
                                     xrange(originalHeight), originalWidth, alphaThreshold)
            minY = self.__findBorder(xrange(originalHeight), originalWidth,
                                     xrange(originalWidth), 1, alphaThreshold)
            maxY = self.__findBorder(xrange(originalHeight - 1, -1, -1), originalWidth,
                                     xrange(originalWidth), 1, alphaThreshold)
        # Обновляем размер сохраняемой области изображения.
        self.__sourceRect = Rect(Point(minX, minY), Size(maxX - minX + 1, maxY - minY + 1))
        
    
    def __findBorder(self, firstRange, firstStride, secondRange, secondStride, alphaThreshold):
        '''
        Сканирование изображения в заданном направлении в поисках полосы непрозрачности.
        '''
        assert firstStride > 0 and secondStride > 0, 'Stride must be positive'
        originalWidth, originalHeight = self.__originalSize.sizeTuple
        data = self.__image.getdata()
        
        extremum = None
        for i in firstRange:
            for j in secondRange:
                alpha = data[i * firstStride + j * secondStride][3]
                if alpha >= alphaThreshold:
                    extremum = i
                    break
            if extremum is not None:
                break
        return extremum
