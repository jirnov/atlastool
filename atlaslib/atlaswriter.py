# coding: utf8
from util import Rect, Size
from atlas import Atlas

# Классы для экспорта атласов.
WRITERS = {}

class Cocos2dWriter(object):
    '''Класс для эскпорта атласов в формате cocos2d plist'''
    def __init__(self):
        pass
    
    def imageName(self, image):
        return image.name
    
    def writeAtlas(self, baseName, atlas):
        assert isinstance(atlas, Atlas), 'Atlas must be Atlas instance'
        atlasFileName = baseName + '.png'
        atlas.atlasImage.save(atlasFileName)

        plist = file(atlasFileName + '.plist', 'wt')
        print >> plist, '<?xml version="1.0" encoding="UTF-8"?>'
        print >> plist, '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
        print >> plist, '<plist version="1.0">'
        print >> plist, '<dict>'
        print >> plist, '    <key>frames</key>'
        print >> plist, '    <dict>'
        for image in atlas.images:
            sourceCenterX = image.sourceRect.origin.x + image.sourceRect.size.width / 2.0
            sourceCenterY = image.sourceRect.origin.y + image.sourceRect.size.height / 2.0
            offsetX = sourceCenterX - image.originalSize.width / 2.0
            offsetY = image.originalSize.height / 2.0 - sourceCenterY

            print >> plist, '        <key>%s</key>' % self.imageName(image)
            print >> plist, '        <dict>'
            print >> plist, '            <key>frame</key>'
            print >> plist, '            <string>%s</string>' % self.__formatRect(Rect(image.atlasPosition, image.sourceRect.size))
            print >> plist, '            <key>offset</key>'
            print >> plist, '            <string>{%.1f, %.1f}</string>' % (offsetX, offsetY)
            print >> plist, '            <key>sourceColorRect</key>'
            print >> plist, '            <string>%s</string>' % self.__formatRect(image.sourceRect)
            print >> plist, '            <key>sourceSize</key>'
            print >> plist, '            <string>%s</string>' % self.__formatSize(image.originalSize)
            print >> plist, '        </dict>'
        print >> plist, '    </dict>'
        print >> plist, '    <key>metadata</key>'
        print >> plist, '    <dict>'
        print >> plist, '        <key>format</key>'
        print >> plist, '        <integer>1</integer>'
        print >> plist, '        <key>size</key>'
        print >> plist, '        <string>%s</string>' % self.__formatSize(atlas.atlasSize)
        print >> plist, '    </dict>'
        print >> plist, '</dict>'
        print >> plist, '</plist>'

    def __formatRect(self, rect):
        return '{{%d, %d}, {%d, %d}}' % (rect.origin.x, rect.origin.y, rect.size.width, rect.size.height)

    def __formatSize(self, size):
            return '{%d, %d}' % (size.width, size.height)
WRITERS['cocos2d'] = Cocos2dWriter

class Cocos2dWriterWithFullPath(Cocos2dWriter):
    '''То же, что и Cocos2dWriter, но вместо имен изображений записывает относительный путь.'''
    def imageName(self, image):
        return image.shortPath
WRITERS['cocos2d-with-path'] = Cocos2dWriterWithFullPath

class OgreWriter(object):
    ''' Класс для экспорта атласов в формате info '''
    def __init__(self):
        pass

    def writeAtlas(self, baseName, atlas):
        assert isinstance(atlas, Atlas), 'Atlas must be Atlas instance'

        atlasImageName = baseName + '.png'
        atlas.atlasImage.save(atlasImageName)

        atlasFileName = baseName + '.atlas'

        info = open(atlasFileName, 'wt')

        import os

        print >> info, 'atlas %s' % os.path.split(os.path.abspath(atlasImageName))[-1]
        print >> info, '{'

        for image in sorted(atlas.images, key=lambda image: image.path):

            path = image.path.replace('\\', '/')
            imagePath, imageName = os.path.split(path)
            imagePath = os.path.basename(imagePath)

            print >> info, '    frame %s' % '/'.join((imagePath, imageName))
            print >> info, '    {'

            sourceSize = (image.originalSize.width, image.originalSize.height)

            left = image.sourceRect.origin.x
            top = image.sourceRect.origin.y
            right = left + image.sourceRect.size.width
            bottom = top + image.sourceRect.size.height

            sourceRect = (left, top, right, bottom)

            offset = (image.atlasPosition.x, image.atlasPosition.y)

            print >> info, '        sourceSize %d %d' % sourceSize
            print >> info, '        sourceRect %d %d %d %d' % sourceRect
            print >> info, '        offset %d %d' % offset

            print >> info, '    }'
        print >> info, '}'

WRITERS['ogre'] = OgreWriter
