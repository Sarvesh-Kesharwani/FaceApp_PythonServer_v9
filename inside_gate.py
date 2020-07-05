#inside_Gate
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

RELAIS_1_GPIO = 17
RELAIS_2_GPIO = 27
RELAIS_3_GPIO = 5
RELAIS_4_GPIO = 6
pirPin = 22

GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
GPIO.setup(RELAIS_2_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_3_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_4_GPIO, GPIO.OUT)
GPIO.setup(pirPin, GPIO.IN)

def extendActuator():
	print("Extneding")
	GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
	GPIO.output(RELAIS_2_GPIO, GPIO.LOW)
	GPIO.output(RELAIS_3_GPIO, GPIO.HIGH)
	GPIO.output(RELAIS_4_GPIO, GPIO.LOW)

def retractActuator():
	print("Retracting")
	GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
	GPIO.output(RELAIS_2_GPIO, GPIO.HIGH)
	GPIO.output(RELAIS_3_GPIO, GPIO.LOW)
	GPIO.output(RELAIS_4_GPIO, GPIO.HIGH)

def stopActuator():
	print("Stop")
	GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
	GPIO.output(RELAIS_2_GPIO, GPIO.LOW)
	GPIO.output(RELAIS_3_GPIO, GPIO.LOW)
	GPIO.output(RELAIS_4_GPIO, GPIO.LOW)

def operation(pirPin):
	extendActuator()
	time.sleep(10)
	
	stopActuator()
	time.sleep(1)
	
	retractActuator()
	time.sleep(10)

	stopActuator()
	time.sleep(1)

print("Gate Control (CTRL+C to exit)")
time.sleep(.2)
print("Ready")

try:
	GPIO.add_event_detect(pirPin, GPIO.RISING, callback=operation)
	while 1:
            time.sleep(1)
		
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()