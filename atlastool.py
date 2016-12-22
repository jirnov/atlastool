# coding: utf8
import sys, os, os.path, optparse
from atlaslib.atlasmanager import AtlasManager
from atlaslib.atlaswriter import WRITERS

if __name__ == '__main__':
    USAGE = 'usage: %prog [options] directory'
    VERSION = '%prog 0.1'
    
    # Разбор командной строки.
    parser = optparse.OptionParser(usage=USAGE, version=VERSION)
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False,
                      help='verbose output')
    group = optparse.OptionGroup(parser, 'Atlas options')
    group.add_option('-W', '--max-width', type='int', action='store', dest='maxWidth', default=2048,
                      help='max atlas width [default %default]')
    group.add_option('-H', '--max-height', type='int', action='store', dest='maxHeight', default=2048,
                      help='max atlas height [default %default]')
    group.add_option('-p', '--padding', type='int', action='store', dest='padding', default=1,
                      help='atlas image padding [default %default]')
    group.add_option('-s', '--sort-on', action='store', dest='sortOn', default='height',
                      help='sort parameter (width or height) [default "%default"]')
    group.add_option('', '--skip-dimension-sum', type='int', action='store', dest='skipDimensionSum', default=1 << 32,
                      help='skip images with dimension sum greater then [default %default]')
    group.add_option('-a', '--alpha-threshold', type='int', action='store', dest='alphaThreshold', default=1,
                      help='alpha threshold for image trimming [default %default]')
    group.add_option('', '--no-optimize', action='store_true', dest='dontOptimize', default=False,
                      help='disable atlas size optimization')

    parser.add_option_group(group)
    
    group = optparse.OptionGroup(parser, 'Output options')
    group.add_option('-f', '--format', action='store', dest='format',
                      help='output format (%s)' % ', '.join(WRITERS.keys()))
    group.add_option('-o', '--output', action='store', dest='outputDirectory', default='./atlases',
                      help='output directory [default "%default"]')
    group.add_option('-n', '--output-name', action='store', dest='outputName', default='atlas',
                      help='output filename [default "%default"]')
    parser.add_option_group(group)
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.print_help()
        print '*** Directory is required'
        exit(1)
    options.directory = args[0]
    
    if options.sortOn not in ('width', 'height'):
        parser.print_help()
        print '*** Sort parameter must be either width or height'
        exit(1)
    
    if options.format not in WRITERS.keys():
        print '*** Invalid output format. Possible formats: %s' % ', '.join(WRITERS.keys())
        exit(1)
    
    # Поиск изображений для создания атласов.
    atlasManager = AtlasManager(options.directory, options.maxWidth, options.maxHeight, options.skipDimensionSum,
                                options.alphaThreshold, options.dontOptimize, options.padding,
                                options.verbose and sys.stdout or None)
    for root, dirs, files in os.walk(options.directory):
        for filename in files:
            basename, ext = os.path.splitext(filename)
            if ext != '.png':
                continue
            atlasManager.appendImage(filename, os.path.join(root, filename))
    
    # Генерация атласов.
    if atlasManager.count == 0:
        print '*** No images found'
        exit(1)
    
    if not os.path.exists(options.outputDirectory):
        os.makedirs(options.outputDirectory)
    atlasManager.generateAtlases(os.path.join(options.outputDirectory, options.outputName), options.sortOn, options.format)
