# coding: utf8
from PIL import Image
from util import Size, Point
from imageinfo import AtlasImageInfo

class Atlas(object):
    '''Атлас - текстура, вмещающая набор изображений.'''
    def __init__(self, size, logFile):
        '''Инициализация с заданным размером.'''
        assert isinstance(size, Size), 'Size must me Size instance'
        self.__size = size
        self.__atlasImage = Image.new("RGBA", size.sizeTuple)
        self.__images = []
        self.__logFile = logFile
    
    def placeImage(self, imageInfo, point, isDuplicate=False):
        '''Размещение изображения в атласе.'''
        assert isinstance(imageInfo, AtlasImageInfo), 'ImageInfo must be AtlasImageInfo instance'
        assert isinstance(point, Point), 'Point must be Point instance'
        assert point.x >= 0 and point.y >=0, 'Image origin must be within atlas'
        assert point.x + imageInfo.sourceRect.size.width <= self.__size.width and \
               point.y + imageInfo.sourceRect.size.height <= self.__size.height, 'Image doesn\'t fit in atlas'
        imageInfo.placeToAtlasImage(self.__atlasImage, point, isDuplicate)
        self.__images.append(imageInfo)

    @property
    def atlasImage(self):
        '''Текстура атласа.'''
        return self.__atlasImage
    
    @property
    def atlasSize(self):
        '''Размер текстуры атласа.'''
        return self.__size
    
    @property
    def images(self):
        '''Список изображений в атласе.'''
        return self.__images
    
    def optimize(self):
        '''Оптимизация размера атласа.'''
        # Определяем размер области, занятой изображениями.
        maxX, maxY = 0, 0
        for image in self.__images:
            maxX = max(maxX, image.atlasPosition.x + image.sourceRect.size.width)
            maxY = max(maxY, image.atlasPosition.y + image.sourceRect.size.height)
        
        # Ищем минимальную ширину и высоту, способную вместить все изображения.
        newWidth = self.__size.width
        while newWidth > maxX:
            if (newWidth >> 1) < maxX:
                break
            newWidth >>= 1
        newHeight = self.__size.height
        while newHeight > maxY:
            if (newHeight >> 1) < maxY:
                break
            newHeight >>= 1
        
        # Обрезаем атлас по новым размерам.
        if newWidth < self.__size.width or newHeight < self.__size.height:
            newSize = Size(newWidth, newHeight)
            print >> self.__logFile, '* [Atlas] Resizing atlas from (%s) to (%s)' % (self.__size, newSize)
            self.__atlasImage = self.__atlasImage.crop((0, 0, newWidth, newHeight))
            self.__size = newSize
