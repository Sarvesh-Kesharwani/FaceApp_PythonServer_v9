import time
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led1 = 17
led2 = 27

GPIO.setup(led1,GPIO.OUT)
GPIO.setup(led2,GPIO.OUT)

print("Lights on")
GPIO.output(led1,GPIO.HIGH)
GPIO.output(led2,GPIO.HIGH)

time.sleep(5)

print("Light off")
GPIO.output(led1,GPIO.LOW)
GPIO.output(led2,GPIO.LOW)

GPIO.cleanup()