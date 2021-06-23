from mega_handler import MegaHandler, InsufficientStorageError
from camera import WebcamVideoStream
from sys import exit
import cv2 as cv
import datetime
import logging
import time

cap = WebcamVideoStream().start()
frames = []
start_time = datetime.datetime.now().second

m = MegaHandler()
logger = logging.getLogger(__name__)


# Flushes the buffer to a video file
def save_to_vid(video):
    path = f"{datetime.datetime.now().strftime('%m-%d-%y %H.%M.%S')}.avi"
    height, width, _ = video[0].shape
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    # Will have to tweak frame-rate once we figure out how long it takes to process frame with YOLO model
    out = cv.VideoWriter(path, fourcc,
                         240, (width, height))
    for frame in frames:
        out.write(frame)

    out.release()
    return path


# Handle all frame processing
def gen_frame():
    global start_time
    while cap:
        frame = cap.read()

        # TODO: This is where to analyze frame with YOLO

        # Draw timestamp in bottom left
        timestamp = datetime.datetime.now()
        cv.putText(frame, timestamp.strftime('%b %d %Y, %I:%M:%S %p EST'), (10, frame.shape[0] - 10),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Add frame to buffer
        frames.append(frame)

        # TODO: Change condition to if motion is detected
        current_time = datetime.datetime.now().second
        # Need abs because seconds are clamped from 0-60
        if abs(current_time - start_time) > 3:
            print(len(frames))
            # if(len(frames) > xxx) Let the buffer fill before immediately flushing, useful with real condition
            path = save_to_vid(frames)
            # try:
            #     link = m.put_video(path)
            # except InsufficientStorageError:
            #     logger.critical(f'Insufficient storage remaining to upload {path}. Please free up space.')
            #  ***send alert here (sms? popup? other?)***

            frames.clear()
            start_time = datetime.datetime.now().second
            continue

        # Convert to byte stream to display on website
        convert = cv.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n')
