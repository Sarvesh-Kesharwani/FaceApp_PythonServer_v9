import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
 
RELAIS_1_GPIO = 17
RELAIS_2_GPIO = 27
RELAIS_3_GPIO = 5
RELAIS_4_GPIO = 6
GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
GPIO.setup(RELAIS_2_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_3_GPIO, GPIO.OUT)
GPIO.setup(RELAIS_4_GPIO, GPIO.OUT)

def extendActuator()
	print("Extneding")
	GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
	GPIO.output(RELAIS_2_GPIO, GPIO.LOW)

def retractActuator()
	print("Retracting")
	GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
	GPIO.output(RELAIS_2_GPIO, GPIO.HIGH)

def stopActuator()
	print("Stop")
	GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
	GPIO.output(RELAIS_1_GPIO, GPIO.LOW)

try:
	while True:
		extendActuator()
		time.sleep(5)
	
		stopActuator()
		time.sleep(2)
	
		retractActuator()
		time.sleep(5)

		stopActuator()
		time.sleep(2)

except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()