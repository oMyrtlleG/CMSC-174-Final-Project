# Note, before using, please download the following libraries
# !pip install mediapipe opencv-python pandas scikit-learn

# Import the necessary libraries/dependencies
import cv2
import mediapipe as mp
import csv
import numpy as np
from collections import deque

# Function responsible for displaying the real-time capturing of the landmarks
def realtime_display():
    # get the functions from the mediapipe for landmarking
    mp_drawing = mp.solutions.drawing_utils 
    mp_holistic = mp.solutions.holistic 

    # get access to the local camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to open webcam.")
        return

    # Create a queue to store the rows of data
    data_queue = deque(maxlen=100)  # Adjust maxlen based on your needs

    # display in real-time the mapping of the landmarks
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():          
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to capture frame.")
                break
            
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = holistic.process(image)
            
            image.flags.writeable = True   
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            draw_landmarks(image, results, mp_drawing, mp_holistic)
            
            class_name = "Play_Left_Hand"
            
            # Export coordinates
            try:                
                # Extract right hand landmarks
                right_hand = results.right_hand_landmarks.landmark if results.right_hand_landmarks else []
                right_hand_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in right_hand]).flatten())
                                
                # Extract left hand landmarks
                left_hand = results.left_hand_landmarks.landmark if results.left_hand_landmarks else []
                left_hand_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in left_hand]).flatten())
                
                # Extract Pose landmarks
                pose = results.pose_landmarks.landmark if results.pose_landmarks else []
                pose_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())
                
                # Concate rows, get coordinated for all these landmarks
                row = right_hand_row + left_hand_row + pose_row
                
                # Append class name 
                row.insert(0, class_name)
                
                # Append the row to the queue
                data_queue.append(row)
                
                # Write the batch of data to the CSV file when the queue is full
                if len(data_queue) == data_queue.maxlen:
                    with open('LandMark_Coords.csv', mode='a', newline='') as f:
                        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        csv_writer.writerows(data_queue)
                    data_queue.clear()
                
            except Exception as e:
                print(f"Error: {e}")
                pass

            cv2.imshow('Raw Webcam Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    
    # Write any remaining data in the queue to the CSV file
    if data_queue:
        with open('LandMark_Coords.csv', mode='a', newline='') as f:
            csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(data_queue)
    
# Function for adding the landmark/skeletal framework of the hands and body of a person
def draw_landmarks(image, results, mp_drawing, mp_holistic):
    # Specific landmarks are shown here https://i.imgur.com/AzKNp7A.png
    # Landmark for the right hand
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                            mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                            mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                            )

    # Landmark for the left hand
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                            mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                            mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                            )

    # Landmark for the whole body
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                            mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                            mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                            )

# The main function
def main():
    realtime_display()

if __name__ == "__main__":
    main()
