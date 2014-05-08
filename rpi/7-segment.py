### Uses GPIO to display numbers on a ELS-321HDB 7-segment display connected via the GPIO pins to a Raspberry Pi 

import RPi.GPIO as GPIO
import time



segments = [('A', 'B', 'C','D','E','F' ),
            ('B','C'), #1
            ('A','B','D','E','G'), #2
            ('A','B','C','D','G'), #3
            ('B','C', 'F','G'), #4
            ('A','C', 'D','F','G'), #5
            ('A','C', 'D','E','F','G'), #6
            ('A','B','C'), #7
            ('A','B','C', 'D','E','F','G'), #8
            ('A','B','C', 'D','F','G'), #9
	    ('A','E','F','G')]
pins = {'A': 17, 'B':27, 'C':22, 'D':25, 'E':24, 'F':18, 'G':23}

#GPIO functions

def init_gpio():
  GPIO.setmode(GPIO.BCM)

def display_nothing():
  GPIO.cleanup()

def display_number(num):
  for pin in segments[num]:
    print pins[pin]
    GPIO.setup(pins[pin], GPIO.OUT)
    GPIO.output(pins[pin], GPIO.HIGH)
  time.sleep(1)
  print "reset"
  display_nothing()

init_gpio()
display_nothing()
for i in range (11):
  display_number(i)


