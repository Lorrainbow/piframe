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

if (green_input_state == False):
    green_invert = True
else:
    green_invert = False

   
if (red_input_state == False):
    red_invert = True
else:
    red_invert = False

    
    
    
       
recording = 0


#how many files have we sent?
import os

def fcount(path):
    """ Counts the number of files in a directory """
    count = 0
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            count += 1

    return count  

log_file=open('/home/pi/errors.log', 'a')

message_ready = False     
while True:    
    red_input_state = GPIO.input(red_button) # Sense the button
    green_input_state = GPIO.input(green_button) # Sense the button

    time.sleep(0.05)           
    
    #any files to listen to?    
    new_files = sorted(glob.glob('/home/pi/piframe_in/*'))
    if not message_ready and new_files:
        message_ready = True        
        if (green_input_state == False):
            green_invert = True
        else:
            green_invert = False        
    
    
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
        
        message_ready = False
        
    
    #they've pressed the red button
    if red_input_state == red_invert:        
        if (recording == 0):
            #print ("Recording...")
            log_file.write("recording")
            #turn the red light on - we're recording
            GPIO.output(red_led, GPIO.HIGH)            
            
            #get the datetime
            f_time = datetime.now().strftime('%d%m%Y-%H%M%s')
           
            
            #set the filename: datetime+the number audio file it is 
            audio_filename = "%s.wav" %(f_time)
            #set the path/file name
            audio_filepathname = "/home/pi/piframe_out/%s" %audio_filename
            
            
            #setup a process and call it
            cmd1 = ["arecord", audio_filepathname, "-r", "48000", "-f", "S16_LE"]
            pro1 = subprocess.Popen(cmd1)   

            log_file.write("recorded")
            recording = 1
            
    if red_input_state != red_invert:
        if (recording == 1):
            #print ("stop recording")
            log_file.write("stop recorded")
            #stop recording - kill the process
            pro1.kill()
            log_file.write("stop recorded1\n")
            #turn the light off red
            GPIO.output(red_led, GPIO.LOW)
            
            
            #setup the message            
            subject = 'piframe ' + f_time
            log_file.write("stop recorded2\n")
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = settings.me
            msg['To'] = settings.toaddr
            msg.preamble = "Audio @ " + f_time            
            log_file.write("stop recorded3\n")
            log_file.write(audio_filepathname)
            fp = open(audio_filepathname, 'rb')            
            log_file.write("stop recorded4\n")
            aud = MIMEAudio(fp.read())
            log_file.write("stop recorded5\n")
            fp.close()
            msg.attach(aud)
            log_file.write("stop recorded6\n")
            try:
                log_file.write("stop recorded7\n")
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(user=settings.me, password=settings.password)
                log_file.write("stop recorded8\n")
                s.sendmail(settings.me, settings.toaddr, msg.as_string())
                log_file.write("stop recorded9\n")
                s.quit()                               
            except smtplib.SMTPException as error:                                            
                error_log_file=open('/home/pi/errors.log', 'a')
                error_log_file.write(error)
                error_log_file.close()     
             
        
            #print ("message sent")
            log_file.write("message sent")
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