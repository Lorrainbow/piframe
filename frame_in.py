import settings
import imaplib
import email
import datetime

M = imaplib.IMAP4_SSL("imap.gmail.com")
M.login(settings.me, settings.password)
M.select("inbox")

last_id = 1

error_log_file=open('/home/pi/errors.log', 'a')

try:
    
    #find the id of the last file we downloaded
    f = open("/home/pi/last_id", "r")
    last_id = int(f.read())
    f.close()
    
except IOError:
    last_id = 1
    error_log_file.write("last id not read\n")

#search the email for all emails with the subject piFrame and the last id
result, data = M.uid('search', None, '(HEADER Subject "piFrame")', 'UID %d:*' %last_id)

data = data[0].split()

#put all the ids as ints into a list
ids=[int(x) for x in data]

#go through the emails

for emailid in data:
    
    #get the email
    resp, data = M.uid('fetch', emailid, "(BODY.PEEK[])")
    
    email_body = data[0][1]
    mail = email.message_from_bytes(email_body)    
    filename = mail['Subject'].replace(" ","")
    
    #go through the email and find the audio file
    for part in mail.walk():        
        if (part.get_content_maintype() == 'audio'):            
            open('/home/pi/piframe_in' + '/' + filename+'.wav', 'wb').write(part.get_payload(decode=True))
            
    #set the email as deleted
    M.uid('STORE', emailid, '+FLAGS', '(\Deleted)')  
    M.expunge()             
            
if (ids):
    #get the biggest id in the list
    maxid = max(ids)
    #print ("new file")
    
    #print (maxid)
    #last_id stores the id of the latest file we've just downloaded
    f=open("last_id", "w")
    f.write (str(maxid+1))
    f.close()
    
error_log_file.close()    