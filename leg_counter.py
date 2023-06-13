import cv2
import mediapipe as mp
import numpy as np
mp_drawing=mp.solutions.drawing_utils  #gives drawing utilities
mp_pose=mp.solutions.pose #importing pose estimation model

def calculate_angle(a,b,c):
    a= np.array(a) #first
    b=np.array(b) #mid
    c=np.array(c) #end
    radians= np.arctan2(c[1]-b[1], c[0]-b[0])-np.arctan2(a[1]-b[1],a[0]-b[0])
    angle=np.abs(radians*180.0/np.pi)
    
    if angle>180.0:
        angle= 360- angle
    return angle 

cap=cv2.VideoCapture(0) 
cap.set(3,640)  #width
cap.set(4,480)  #height

total_time=8
reset=0
# curl counter variable
counter=0
stage=None

# setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.2, min_tracking_confidence=0.2) as pose: #we use 0.5 which is 50%, for higher super accracy increse the percentage but it wot work if the body is not perfect
    while True:
        success, img= cap.read()
        
        #recoloring image to RGB
        # when we pass image to mediapipe, it has to be of form of RGB
        image= cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image.flags.writeable=False  # it saves space, pass object by read only 
        
        # VERY IMPORTANT | make detection
        results= pose.process(image) #storing the detection in results
        
        #recoloring image to BGR
        image.flags.writeable=True
        image= cv2.cvtColor(image, cv2.COLOR_RGB2BGR )
        
        #extracting landmarks
        try:
            landmarks= results.pose_landmarks.landmark
            
            #getting coordinates
            hip= [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee= [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle= [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                    
            # calculate angle
            angle=calculate_angle(hip, knee, ankle)
            
            #visualise 
            cv2.putText(image, str(angle),
                       tuple(np.multiply(knee, [640,480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),2,cv2.LINE_AA)
            
            cv2.rectangle(image,(0,0),(255,73),(245,117,16),-1)
               
            # curl counter logic
            if angle>160:
                stage='down'
                total_time=8
                cv2.putText(image, str(total_time),(200,60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
            if angle<50 and stage=='down':
                stage='up'
                #counter+=1

            if(stage=='up' and angle<50 and total_time>=1):
                    cv2.putText(image, str(total_time),(200,60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
                    #print(total_time)
                    time.sleep(1)
                    total_time=total_time-1
            if (total_time==1):
                counter+=1
                
            if(total_time<8 and total_time >1 and angle>50):
#                 print('keep ur hands curled')
                cv2.putText(image, 'Keep your knee bent',(150,150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2,cv2.LINE_AA)
            
                   
                    
#                 reset=1
#                 else:
#                     reset=0
          
        except:
            pass
        
        #render curl counter
        #setup status box
        
        
        #rep data
        cv2.putText(image, "REPS",(15,12),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(image, str(counter),(10,60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
        #stage data
        cv2.putText(image, "STAGE",(60,12),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(image, stage,(60,60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(image, "TIME",(200,12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),1,cv2.LINE_AA)
        
        
        
        
        
        #render detection
        #----drawing utilties----        ------landmarks------
        # to learn more run "mp_drawing.draw_landmarks??"
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), #color of dots
                                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)  #color of lines
                                 )
        
        
        cv2.imshow('Mediapipe Feed',image)
        if cv2.waitKey(10) & 0xFF==ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()