import time

def dosomething():
	print 'did a thing'

global A
A = {'a':1, 'b':2}

import Image
lena = Image.open('lena.jpg')

import browser
def loadimage():
	browser.writeimage('#image', lena)

# 
# from opencv.highgui import *
# from opencv.adaptors import *	
# #cap = cvCreateCameraCapture(0)
# def cam():
# 	for i in range(10):
# 		frame = cvQueryFrame(cap)
# 		pyreg.writeimage('#image', Ipl2PIL(frame))
# 	
