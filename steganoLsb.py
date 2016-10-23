#!/usr/bin/python3

import optparse
from sys import exit

from PIL import Image

class lsbIter:
    def __init__(self, im, i=0, j=0, rgba=False):
        self.im = im
        self.i = i
        self.j = j
        self.c = -1
        if rgba:
            self.maxc = 4
        else:
            self.maxc = 3

    def next(self, n="unknown"):
        self.c+=1
        if self.c==self.maxc:
            self.j+=1
            if self.j==self.im.size[1]:
                if self.i==self.im.size[0]-1:
                    raise Exception('Data too large, stopping at byte %i' %n)
                else:
                    self.j=0
                    self.i+=1
            self.c=0
        return self.c,self.i,self.j

def main(task, src, output=None, data=None, size=None, rgba=False):
    if task == 'hide':
        im = Image.open(src)
        with open(data, 'rb') as fb:
            h = hide(im, fb, rgba)
            if output:
                h.save(output)
            else:
                h.show()
    elif task == 'extract':
        im = Image.open(src)
        r = extract(im, int(size), rgba)
        if output:
            with open(output, 'wb') as fp:
                fp.write(bytearray(r))
        else:
            print("".join([chr(i) for i in r]))

def hide(im, data, rgba):
    msg = data.read()
    it = lsbIter(im, rgba)
    for n, byte in enumerate(msg):
        for k in range(8):
            c,i,j = it.next(n)
            pixel = list(im.getpixel((i,j)))
            pixel[c] = (pixel[c] >> 1 << 1) + ((byte >> k) & 1)
            im.putpixel((i,j), tuple(pixel))
    return im

def extract(im, size, rgba):

    bytes = [0]*size
    it = lsbIter(im, rgba)

    for n in range(size):
        for k in range(8):
            c,i,j = it.next(n)
            pixel = im.getpixel((i,j))
            bytes[n] = bytes[n] + ((pixel[c]&1) << k)
    return bytes


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-a', '--use-rgba', default=False, action='store_true',
                  help='use alpha channel')
    parser.add_option('-e', action='store', dest='ime',
                  help='extract data from image')
    parser.add_option('-s', action='store', dest='size',
                  help='indicate size (bytes) of hidden data to read from img')
    parser.add_option('-d', action='store', dest='data',
                  help='path to secret data')
    parser.add_option('-p', action='store', dest='imp',
                  help='image to be patched')
    parser.add_option('-o', action='store', dest='output',
                      help='specify output for patched image or for extracted img (otherwise nothing is saved)')
    (opts, args) = parser.parse_args()
    if opts.imp:
        if not opts.data:
            print('you did not specified path to secret data')
            exit(-1)
        main('hide', opts.imp, output=opts.output, data=opts.data, rgba=opts.use_rgba)

    elif opts.ime:
        if not opts.size:
            print('plz indicate size of hidden data with -s [size]')
            exit(-1)
        main('extract', opts.ime, output=opts.output, size=opts.size, rgba=opts.use_rgba)

    else:
        parser.print_help()
