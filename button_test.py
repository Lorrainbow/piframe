import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

green_button = 13
red_button = 6
red_led = 12
green_led = 5

GPIO.setup(red_button, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(green_button, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(red_led, GPIO.OUT) 
GPIO.setup(green_led, GPIO.OUT) 

red_input_state = GPIO.input(red_button) # Sense the button
green_input_state = GPIO.input(green_button) # Sense the button

print ("red is currently %d" %red_input_state)
print ("green is currently %d" %green_input_state)

GPIO.output(red_led, 1)
GPIO.output(green_led, 1)

if (green_input_state == False):
    green_invert = True
else:
    green_invert = False

    
if (red_input_state == False):
    red_invert = True
else:
    red_invert = False

print ("red invert is currently %d" %red_invert)
print ("green invert is currently %d" %green_invert)

while True:
    time.sleep(0.2)

    red_input_state = GPIO.input(red_button) # Sense the button
    if red_input_state == red_invert:
        print('RED Button Pressed')
        time.sleep(0.2)
        # Switch on LED
        GPIO.output(red_led, 1)
    else:
        # Switch off LED
        GPIO.output(red_led, 0)    

    green_input_state = GPIO.input(green_button) # Sense the button
    if green_input_state == green_invert:
        print('GREEN Button Pressed')
        time.sleep(0.2)
        # Switch on LED
        GPIO.output(green_led, 1)
    else:
        # Switch off LED
        GPIO.output(green_led, 0)    