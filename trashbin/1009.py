# ──────────────────────────────────────────
# 오늘은 10월 09일 HI SERA~? I'M HEEOK
# ──────────────────────────────────────────



import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import random
# MAX distance 37..
# ──────────────────────────────────────────
# distance measurement
# ──────────────────────────────────────────
def measure():
    #print ("Waiting For Sensor To Settle")
    #time.sleep(2)

    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    while GPIO.input(ECHO)==0:
        Start = time.time()
        
    while GPIO.input(ECHO)==1:
        End = time.time()

    TimeDuration = End - Start

    distance = TimeDuration * 17150
    distance = round(distance, 2)

    return distance

# ──────────────────────────────────────────
# distance average
# ──────────────────────────────────────────
def average():
    
    i=3
    distance = 0
    
    while i > 0:                # take 3 measurements
        dst = measure()
        time.sleep(0.1)
        if dst > 1000:          # out of the range:  continue
            #print("out of the range")
            continue
        
        distance += dst
        i = i-1
    
    distance = distance / 3
    distance = round(distance, 2)
    return distance             # return the average

# ──────────────────────────────────────────
# fill-level measurement
# ──────────────────────────────────────────
def fill_level():                   #trash_bin 15.3cm
    
    dst = average()
    print("Distance:",dst,"cm")

    if dst < 5:             # 90%
        return 1

    elif dst < 9:           # 70% 
        return 2

    elif dst < 13:          # 30%
        return 3
    
    elif dst < 17:          # 0%
        return 4
    
    else:
        return 5

# ──────────────────────────────────────────
# fill-level verification
# ──────────────────────────────────────────
def level_check():
    
    level1 = fill_level()
    time.sleep(0.1)
    level2 = fill_level()
    time.sleep(0.1)
    level3 = fill_level()
                #time.sleep(0.1)

    if level1==level2 and level1==level3:
        return level1
    return 0

# ──────────────────────────────────────────
# random value
# ──────────────────────────────────────────
def random_value():
    rnd = random.randint(1,20)
    
    #print ("rnd :",rnd)
    time.sleep(0.1)
    
    if(rnd == 1):
        return 1
    else:
        return 0
# ──────────────────────────────────────────

GPIO.setmode(GPIO.BCM)

# ultrasoic
TRIG = 4 
ECHO = 17

# button & led
key_pin =23
led_pin =24

print ("Distance Measurement In Progress")
# MQTT pub
mqttc = mqtt.Client("SMART TRASHBIN")
mqttc.connect("192.168.0.4", 1883)


# ultrasoic
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, GPIO.LOW)

# button & led
GPIO.setup(key_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)#Button to GPIO23
GPIO.setup(led_pin, GPIO.OUT)  #LED to GPIO24

NOW_LEVEL=0
FULL=0
EMERGENCY=0
FLAG=1

TOPIC="trashbin"

try:
    while True:
    
# ───── is EMERGENCY ─────────────────────────────────────────────
        if EMERGENCY == 1:
            
            button_state = GPIO.input(key_pin)  #버튼 활성화하고 #E
            GPIO.output(led_pin, True)
            
            if FLAG == 1:
                mqttc.publish(TOPIC,"#E")
                print('Send message: #E')
                time.sleep(0.2)
                
                FLAG = 0
                
            if button_state == False:           #버튼을 누르면 #S
                
                mqttc.publish(TOPIC,"#S")
                print('Send message: #S')
                GPIO.output(led_pin, False)
                time.sleep(0.2)
                
                FLAG = 1
                EMERGENCY=0
            
                    
# ───── is not EMERGENCY  ────────────────────────────────────────
        elif EMERGENCY == 0:
            
    # ───── is FULL         
            if FULL == 1:
                
                button_state = GPIO.input(key_pin)  #버튼 활성화
                if button_state == False:
                    
                    mqttc.publish(TOPIC,"#C")       #버튼을 누르면 #C
                    print('Send message: #C')
                    time.sleep(0.2)
                    
                    FULL=0
                    NOW_LEVEL = 0

    # ───── is not FULL                    
            else:
                
                #EMERGENCY = random_value()

                level = level_check()                   #fill-level 3중 체크          
                if(level != 0):
                    if (level != NOW_LEVEL):
                        NOW_LEVEL = level               #NOW_LEVEL update
                    
                        MESSAGE ="#{}".format(NOW_LEVEL)
                        mqttc.publish(TOPIC,MESSAGE)
                        print("Send message: #",NOW_LEVEL)

                        if NOW_LEVEL == 1:              #fill_level이 80%이상이라면           
                            FULL=1

# ──────────────────────────────────────────────────────────────────                  
 
        
except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    GPIO.cleanup()

mqttc.loop(2)
    
