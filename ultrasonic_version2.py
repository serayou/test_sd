import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

TRIG = 4 
ECHO = 17

print ("Distance Measurement In Progress")

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)	

def measure():
	
	GPIO.output(TRIG, GPIO.LOW)
        #print ("Waiting For Sensor To Settle")
	time.sleep(2)

    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)
        
    while GPIO.input(ECHO)==0:
        Start = time.time()       # save Start Time 

    while GPIO.input(ECHO)==1:
        End = time.time()         # save End Time

    TimeDuration = End - Start

    distance = TimeDuration * 17150     # multiply with speed 17150 cm/s(34300 cm/s)

    distance = round(distance, 1)

def average():
	distance1 = measure()	# takes 3 distances
	time.sleep(0.1)
	distance2 = measure()
	time.sleep(0.1)
	distance3 = measure()

	distance = distance1 + distance2 + distance3
	distance = distance / 3

	return distance
	
try:
    while True:
	    
		distance = average()
        print ("Distance:",distance,"cm")
        time.sleep(1)

except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    GPIO.cleanup()
