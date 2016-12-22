# coding: utf8
import os
from atlas import Atlas
from imageinfo import AtlasImageInfo
from atlaswriter import WRITERS
from util import *

class AtlasManager(object):
    '''Менеджер атласов.'''

    def __init__(self, directory, maxWidth, maxHeight, skipDimensionsSum, alphaThreshold, withoutOptimize, padding, logFile=None):
        '''
        Инициализация менеджера атласов.
            maxWidth     максимальная ширина атласа
            maxHeight         -       высота атласа
            padding      расстояние между соседними изображениями в атласе
            logFile      файл для вывода отладочной информации
        '''
        assert maxWidth > 0 and maxHeight > 0, 'Invalid max texture dimensions'
        assert maxWidth & (maxWidth - 1) == 0, 'Max texture width must be power of 2'
        assert maxHeight & (maxHeight - 1) == 0, 'Max texture height must be power of 2'
        assert padding >= 0, 'Padding must be positive or 0'
        assert 0 < alphaThreshold < 256, 'Alpha threshold must be greater 0 and less 256'

        # Если лог-файл не задан, выводим в /dev/null
        if logFile is None:
            class DummyLog:
                def write(*args):
                    pass
            logFile = DummyLog()

        # Список изображений, сгруппированных по sourceRect.size
        self.__imagesGroupedBySize = {}

        self.__maxSize = Size(maxWidth, maxHeight)
        self.__skipDimensionsSum = skipDimensionsSum
        self.__alphaThreshold = alphaThreshold
        self.__padding = padding
        self.__directory = os.path.abspath(directory)
        self.__withoutOptimize = withoutOptimize
        self.__images = []
        self.__log = logFile
        print >> self.__log, "[AtlasManager] Starting Atlas Manager"

    @property
    def count(self):
        '''Возвращает количество изображений.'''
        return len(self.__images)

    def appendImage(self, imageName, imagePath):
        '''
        Добавление изображения в набор атласов.
            imageName   имя изображения в атласе.
            imagePath   путь к изображению.
        '''
        # TODO: проверить, не добавлено ли изображение дважды
        shortImagePath = os.path.abspath(imagePath)[len(self.__directory) + 1:]
        imageInfo = AtlasImageInfo(imageName, imagePath, shortImagePath, self.__alphaThreshold, self.__padding)
        if imageInfo.sourceRect.size.dimensionsSum > self.__skipDimensionsSum:
            print >> self.__log, ' * [AtlasManager] skip image', imageInfo.shortPath
            return
        print >> self.__log, ' * [AtlasManager] adding image', imageInfo.shortPath
        if not self.__maxSize.canFit(imageInfo.sourceRect.size):
            raise Exception('Image "%s": image dimensions (%s) with padding %dpx exceed max atlas size (%s)' % \
                            (imageName, imageInfo.sourceRect.size, self.__padding, self.__maxSize))
        if imageInfo.sourceRect.size.sizeTuple not in self.__imagesGroupedBySize.iterkeys():
            self.__imagesGroupedBySize[imageInfo.sourceRect.size.sizeTuple] = []
        self.__imagesGroupedBySize[imageInfo.sourceRect.size.sizeTuple].append(imageInfo)
        self.__images.append(imageInfo)

    def generateAtlases(self, basePath, sortOn, writer):
        '''
        Создание атласов и их описаний.
            basePath     путь и префикс имени файла с атласом
            sortOn       параметр сортировки атласов (ширина или высота)
            writer         объект для записи атласов
        '''
        assert sortOn in ('width', 'height'), 'SortOn must be either width or height'
        assert writer in WRITERS, 'Unknown writer'

        print >> self.__log, '[AtlasManager] generating atlases'

        # Сортируем изображения в порядке увеличения параметра сортировки (будем искать подходящее
        # по размерам изображение начиная с конца.
        self.__images.sort(key=lambda i: getattr(i.paddedSourceRect.size, sortOn))
        writer = WRITERS[writer]()

        # Размещаем изображения.
        atlasIndex = 0
        while self.__images:
            # Количество помещенных изображений
            imageCount = 0
            # Количество дубликатов
            duplicateCount = 0

            atlas = Atlas(self.__maxSize, self.__log)

            areas = [Rect(Point(0, 0), self.__maxSize)]
            while areas:
                # Ищем изображение, максимально подходящее по размеру.
                area = areas.pop()
                image = self.__retainMostFittableImage(area.size)

                # Если изображение не найдено, переходим к следующей области.
                if image is None:
                    continue

                # Размещаем изображение в верхний левый угол области и делим оставшееся пространство.
                atlas.placeImage(image, area.origin)
                areas.extend(self.__splitRect(area, image.paddedSourceRect.size, sortOn))
                imageCount += 1

                # Ищем оставшиеся дубликаты изображения
                groupImages = self.__imagesGroupedBySize[image.sourceRect.size.sizeTuple]
                groupImages.remove(image)

                for dupeImage in list(groupImages):
                    if dupeImage.isEqual(image):
                        groupImages.remove(dupeImage)
                        atlas.placeImage(dupeImage, area.origin, isDuplicate=True)
                        duplicateCount += 1
                        imageCount += 1
                        self.__images.remove(dupeImage)

            # Записываем атлас.
            if not self.__withoutOptimize:
                atlas.optimize()
            atlasName = basePath + str(atlasIndex)
            writer.writeAtlas(atlasName, atlas)
            atlasIndex += 1
            print >> self.__log, ' * [AtlasManager] writing atlas "%s" (images %d, duplicates %d%%)' % (os.path.basename(atlasName),
                imageCount, float(duplicateCount) / imageCount * 100.0)

    def __retainMostFittableImage(self, targetSize):
        '''
        Возвращает наибольшее изображение, помещающееся в заданный регион и удаляет его из списка изображений.
        Если изображение не найдено, возвращает None.
        '''
        assert isinstance(targetSize, Size), 'Size must be Size instance'

        # Изображения уже отсортированы по размеру. Ищем первое подходящее с конца.
        for image in reversed(self.__images):
            if targetSize.canFit(image.sourceRect.size):
                self.__images.remove(image)
                return image
        return None

    def __splitRect(self, rect, size, sortOn):
        '''
        Возвращает tuple из прямоугольников (от нуля до двух), получаемых разделением
        исходного заданной областью.
        '''
        assert isinstance(rect, Rect), 'Rect must be Rect instance'
        assert isinstance(size, Size), 'Rect must be Size instance'
        assert sortOn in ('width', 'height'), 'SortOn must be either width or height'

        # Если размеры разделяющего прямоугольника больше, чем у разделяемого, обрезаем разделяющий.
        size = Size(min(size.width, rect.size.width), min(size.height, rect.size.height))

        # Создаем прямоугольники справа и снизу.
        rects = []

        if sortOn == 'height':
#            ┌───┬───┐
#            │ 3 │ 2 │
#            ├───┴───┤
#            │   1   │
#            └───────┘
            if rect.size.height != size.height:
                rects.append(Rect(Point(rect.origin.x, rect.origin.y + size.height), Size(rect.size.width, rect.size.height - size.height)))

            if rect.size.width != size.width:
                rects.append(Rect(Point(rect.origin.x + size.width, rect.origin.y), Size(rect.size.width - size.width, size.height)))

        elif sortOn == 'width':
#            ┌───┬───┐
#            │ 3 │   │
#            ├───┤ 1 │
#            │ 2 │   │
#            └───┴───┘
            if rect.size.width != size.width:
                rects.append(Rect(Point(rect.origin.x + size.width, rect.origin.y), Size(rect.size.width - size.width, rect.size.height)))

            if rect.size.height != size.height:
                rects.append(Rect(Point(rect.origin.x, rect.origin.y + size.height), Size(size.width, rect.size.height - size.height)))
        return rects
