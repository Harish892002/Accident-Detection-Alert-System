import cv2
from . import views
import warnings
warnings.filterwarnings("ignore")
from django.core.mail import send_mail
from django.conf import settings
import pusher
from .models import *
import numpy as np
import torch

def check(t1,img,model):
    results = model(img)
    results.print()
    dummy_array = np.array(results.xyxy[0])
    dummy_array = dummy_array.astype(int)
    dummy_array = dummy_array[dummy_array[:,0].argsort()]
    return detect(dummy_array,t1)    

def send_notification(id,flag):
    detected_location = views.current_loc_identify()
    pusher_client = pusher.Pusher(
    app_id='1328110',
    key='4da6311b184ace45d1dc',
    secret='469709e6b17fadfab16f',
    cluster='ap2',
    ssl=True
    )
    if flag:
        notif = Notifications(notification="Alert - Accident happened",latitude=detected_location['lat'],longitude=detected_location['lng'],accepted=0)
        notif.save()
    if id==1:
        pusher_client.trigger('my-channel', 'my-event', {'message2': 'Urgent\n please send ambulance as soon as possible at xyz address.'})
    if id==2:
        pusher_client.trigger('my-channel', 'my-event', {'request': 'Request Sent'})
    return

def detect(boxes,t1):
    n = len(boxes)
    for i in range(n):
        x1,y1,w1,h1 = boxes[i][0],boxes[i][1],boxes[i][2],boxes[i][3]
        for j in range(i+1,n):
            x2,y2,w2,h2 = boxes[j][0],boxes[j][1],boxes[j][2],boxes[j][3]
            if x2<(w1):
                xmin, xmax = min(x1,x2), max(w1,w2)
                ymin, ymax = min(y1,y2), max(h1,h2)
                print(xmin,xmax,ymin,ymax)
                print((xmin>=t1[0] & t1[0]<=xmax) | (xmin>=t1[2] & t1[2]<=xmax))
                print((ymin>=t1[1] & t1[1]<=ymax) | (ymin>=t1[3] & t1[3]<=ymax))
                if ((xmin>=t1[0] & t1[0]<=xmax) | (xmin>=t1[2] & t1[2]<=xmax)) & ((ymin>=t1[1] & t1[1]<=ymax) | (ymin>=t1[3] & t1[3]<=ymax)):
                    return True

    return False

def get_hospital_emails(lat,long):
    # detected_location = views.current_loc_identify()
    hospitals_in_radius = views.find_nearby_hospitals(lat,long)

    print('List of Hospitals in the proximity of Accident Location')
    hospital_emails = [i['Email'] for i in hospitals_in_radius]

    #Adding default email address for verification purpose
    hospital_emails.append("")

    print("Mailing List:", hospital_emails)
    return hospital_emails

def sendmail():
    detected_location = views.current_loc_identify()
    email_subject = "Urgent: Please Send Ambulance"
    email_body = (
        f"Accident happened the following Location"
        f"Please send an ambulance as soon as possible \n"
        f"Google Map Link: https://www.google.com/maps/search/?api=1&query={detected_location['lat']},{detected_location['lng']}"
    )

    try:
        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            get_hospital_emails(detected_location['lat'],detected_location['lng']),
            fail_silently = False
        )
        print("Email sent Successfully")
    except Exception as e:
        # print(f"Error sending email: {e}")
        print(e)

    return

class streaming(object):
    def __init__(self):
        print("hello")
        self.flag=True
        # self.video_capture = cv2.VideoCapture(0)
        self.video_capture = cv2.VideoCapture('video.mp4')
        self.model1=torch.hub.load('ultralytics/yolov5', 'custom', path='best (1).pt',device='cpu')
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='accident.pt',device='cpu')

    def get_frame(self):
        ret, frame = self.video_capture.read()
        cv2.imwrite("img.jpg",frame)
        imgs = cv2.imread("img.jpg")
        results = self.model1(imgs)
        get = results.print()

        dummy_array = np.array(results.xyxy[0])
        dummy_array = dummy_array.astype(int)

        if ret==False:
            pass
        else:
            jpeg = cv2.imencode('.jpg', frame)[1]

            for i in dummy_array:
                if check(i,imgs,self.model) and self.flag:
                    print("&"*60)
                    print("Accident Detected")
                    send_notification(1,True)
                    send_notification(2,False)
                    sendmail()
                    self.flag = False
            return jpeg.tobytes()
    