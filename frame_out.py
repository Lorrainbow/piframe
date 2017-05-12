import settings
import glob
import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
import subprocess
import time
from datetime import datetime
import smtplib
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
import os

#setup the GPIO pins for the buttons and the LEDs
green_button = 13
red_button = 6
red_led = 12
green_led = 5

GPIO.setup(red_button, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(green_button, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(red_led, GPIO.OUT) 
GPIO.setup(green_led, GPIO.OUT) 

recording = 0



def fcount(path):
    """ Counts the number of files in a directory """
    count = 0
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            count += 1

    return count  

log_file=open('/home/pi/errors.log', 'a')
    
    
#forever check for button presses/new files
while True:
    #my buttons are weird... 
    red_input_state = GPIO.input(red_button) 
    green_input_state = GPIO.input(green_button)

    if (green_input_state == False):
        green_invert = True
    else:
        green_invert = False
   
    if (red_input_state == False):
        red_invert = True
    else:
        red_invert = False

    time.sleep(0.05)        
    
    #any new files to listen to?    
    new_files= sorted(glob.glob('/home/pi/piframe_in/*'))        
        
    #if there are any new files, turn the green light on
    if new_files:
        GPIO.output(green_led, GPIO.HIGH)    
    else:
        GPIO.output(green_led, GPIO.LOW)
    
    #they've pressed the green button and the green light is on     
    if ((green_input_state == green_invert) and (new_files)):                   
                
        #play                
        subprocess.call(["aplay", new_files[0]])        
        
        #remove the file once it has played
        os.remove(new_files[0])        
        
    
    #they've pressed the red button
    if red_input_state == red_invert:        
        #they've pressed the red button for the first time
        if (recording == 0):
            #turn the red light on - we're recording
            GPIO.output(red_led, GPIO.HIGH)            
            
            #get the current date time
            f_time = datetime.now().strftime('%d%m%Y-%H%M')          
            
            #set the filename: datetime+the number audio file it is 
            audio_filename = "%s.wav" %(f_time)
            #set the path/file name
            audio_filepathname = "/home/pi/piframe_out/%s" %audio_filename           
            
            #setup a process to record and call it
            cmd1 = ["arecord", audio_filepathname, "-r", "48000", "-f", "S16_LE"]
            pro1 = subprocess.Popen(cmd1)               
            recording = 1
    
    #they've pressed the red button for the second time
    if red_input_state != red_invert:
        if (recording == 1):            
            #stop recording - kill the process
            pro1.kill()
            
            #turn the red light off
            GPIO.output(red_led, GPIO.LOW)            
            
            #setup the email message with the unique name "piframe" in the subject line
            subject = 'piframe ' + f_time            
            msg = MIMEMultipart()            
            msg['Subject'] = subject
            
            #get the to/from details from your settings file
            msg['From'] = settings.me
            msg['To'] = settings.toaddr
            msg.preamble = "Audio @ " + f_time
            fp = open(audio_filepathname, 'rb')            
            aud = MIMEAudio(fp.read())            
            fp.close()
            msg.attach(aud)
            
            #send the message
            try:                
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(user=settings.me, password=settings.password)                
                s.sendmail(settings.me, settings.toaddr, msg.as_string())                
                s.quit()                               
            except smtplib.SMTPException as error:                                            
                error_log_file=open('/home/pi/errors.log', 'a')
                error_log_file.write(error)
                error_log_file.close()     
             
            #remove the recording 
            os.remove(audio_filepathname)           
            
            #message was sent successfully, flash green            
            GPIO.output(green_led, GPIO.HIGH)
            time.sleep(1)            
            GPIO.output(green_led, GPIO.LOW)
            time.sleep(1)            
            GPIO.output(green_led, GPIO.HIGH)
            time.sleep(1)            
            GPIO.output(green_led, GPIO.LOW)            
            
            recording = 0
        
GPIO.cleanup()