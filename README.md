����������� �� ��� �������������� ������� ��� �������� ���������� ������� �� ������ �����������.

������� �������� �� ������ ���� � ���� �������� � ������� 2012 ����, �������� �������� �� ��� ���.

������������� ����������:

Usage: atlastool.py [options] directory
 
Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v, --verbose         verbose output
 
  Atlas options:
    -W MAXWIDTH, --max-width=MAXWIDTH
                        max atlas width [default 2048]
    -H MAXHEIGHT, --max-height=MAXHEIGHT
                        max atlas height [default 2048]
    -p PADDING, --padding=PADDING
                        atlas image padding [default 1]
    -s SORTON, --sort-on=SORTON
                        sort parameter (width or height) [default "height"]
    --skip-dimension-sum=SKIPDIMENSIONSUM
                        skip images with dimension sum greater then [default
                        4294967296]
    -a ALPHATHRESHOLD, --alpha-threshold=ALPHATHRESHOLD
                        alpha threshold for image trimming [default 1]
    --no-optimize       disable atlas size optimization
 
  Output options:
    -f FORMAT, --format=FORMAT
                        output format (ogre, cocos2d, cocos2d-with-path)
    -o OUTPUTDIRECTORY, --output=OUTPUTDIRECTORY
                        output directory [default "./atlases"]
    -n OUTPUTNAME, --output-name=OUTPUTNAME
                        output filename [default "atlas"]

�� ������ ������ ������������ ������ png, �� ��� ������� ����� �������� ����� ��������� ������.
