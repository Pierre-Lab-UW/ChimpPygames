import sys, os, random, time, glob, logging, math
try:
    # checks if you have access to RPi.GPIO, which is available inside RPi
    import RPi.GPIO as GPIO
except:
    # In case of exception, you are executing your script outside of RPi, so import Mock.GPIO
    import Mock.GPIO as GPIO

from pygame.locals import *

channel = 23

        
while True:
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(channel, GPIO.OUT)
        GPIO.output(channel, GPIO.LOW)
        print('set to low')
        time.sleep(5)
        print('set to high')
        GPIO.cleanup()
    except KeyboardInterrupt:
          GPIO.cleanup()
         

GPIO.cleanup()
