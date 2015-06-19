#!/usr/bin/python
import math
import time
import threading
import os

import picamera
import Adafruit_CharLCD as LCD

# Parameter
capture_delay = 60
capture_resolution = (1920, 1080)
capture_directory = '/var/www/wc/img/'
capture_purge_hour = 12

# Initialize the LCD
lcd = LCD.Adafruit_CharLCDPlate()
lcd.clear()
lcd.set_color(0.0, 0.0, 0.0)

# Misc var
stop = False
lastCaptureDate = time.localtime()
lastCaptureSize = 0

class KeyListener(threading.Thread):
	def run(self):
		global stop
		global capture_delay
		while not stop: 
			if lcd.is_pressed(LCD.SELECT):
				self.stop()
				quit()
			if lcd.is_pressed(LCD.UP):
				capture_delay += 1
				display()
			if lcd.is_pressed(LCD.DOWN):
				capture_delay = max(5, capture_delay - 1)
				display()
			if lcd.is_pressed(LCD.LEFT):
				capture()
			if lcd.is_pressed(LCD.RIGHT):
				capture()
			time.sleep(0.2) 
	def stop(self):
		global stop
		stop = True

class CaptureThread(threading.Thread):
	def run(self):
		global stop
		global capture_delay
		i = 0
		while not stop:
			if i >= capture_delay:
				capture()
				clean()
				i = 0
			else:
				i += 1
			time.sleep(1)

def quit():
	stop = True
	lcd.clear()
	lcd.set_color(0.0, 0.0, 0.0)

def displayText(text):
	lcd.clear()
	lcd.message(text)

def display():
	displayText("D:" + str(capture_delay) + "s S:" + str(lastCaptureSize) + "M\nL:" + time.strftime('%d/%m %H:%M:%S', lastCaptureDate))

def capture():
	global lastCaptureDate
	global lastCaptureSize
	lcd.set_color(1.0, 0.0, 0.0)
	lastCaptureDate = time.localtime()
	fileName = "Capture_" + time.strftime('%y%m%d_%H%M%S', lastCaptureDate) + ".jpg"
	fullPath = capture_directory + fileName
	cameraCapture(fullPath)
	lastCaptureSize = round(os.path.getsize(fullPath) / 1048576.0, 1)
	display()
	lcd.set_color(0.0, 0.0, 0.0)

def cameraCapture(path):
	with picamera.PiCamera() as camera:
		#camera.resolution = (2592, 1944)
		camera.resolution = capture_resolution
		camera.vflip = True
		camera.hflip = True
		camera.start_preview()
		time.sleep(2)
		camera.capture(path)

def clean():
	maxdate = time.time() - capture_purge_hour * 3600
	for r,d,f in os.walk(capture_directory):
		for file in f:
			timestamp = os.path.getmtime(os.path.join(r,file))
			if maxdate > timestamp and file.endswith('.jpg'):
				try:
					os.remove(capture_directory + file)
				except Exception,e:
					print e
					pass

# Start the key listener
keyListner = KeyListener()
keyListner.start()

# First capture
capture()

# Start the capture thread
captureThread = CaptureThread()
captureThread.start()
