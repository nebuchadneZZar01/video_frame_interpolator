"""
 # @author nebuchadnezzar
 # @email michele.ferro1998@libero.it
 # @create date 03-11-2021 12:51:37
 # @modify date 20-12-2021 18:19:34
 # @desc video interpolation project (subject: Multimedia)
"""

import numpy as np
import cv2

# ---- CALCULATION FUNCTIONS ----

def gen_out(in_a, new_length):
    old_length = len(in_a)
    step = round(new_length/old_length)
    
    # create new empty array (it will contain the frames)
    out_a = np.array([None]*new_length)                                              

    # inserting each frame of the input video with a step 
    for i in range(old_length):
        j = i * step
        if j < new_length:
            out_a[j] = in_a[i]

    return out_a, old_length, step

# dup mode: the frame i is equal to frame i-1 (his predecessor)
def dup(in_a, new_length):
    out_a, old_length, step = gen_out(in_a, new_length)

    for i in range(new_length):
        if out_a[i] is not None: pass
        else: out_a[i] = out_a[i-1]

    return out_a

# blend mode: the frame i is given by the average between frame i-1 (its predecessor) and frame i+1 (its successor)
def blend(in_a, new_length):    
    out_a, old_length, step = gen_out(in_a, new_length)

    # first case: fill the "empty frame" with the average between his successor and his predecessor
    if round(new_length/old_length) == 2:
        fake_new_length = old_length*2
        for i in range(fake_new_length):
            if out_a[i] is not None: pass
            elif i+1 < fake_new_length: out_a[i] = np.mean(np.array([out_a[i-1],out_a[i+1]], dtype='object'), axis=0).astype('uint8')
            else: 
                zero_shape = out_a[i-1].shape 
                out_a[i] = np.mean(np.array([out_a[i-1],np.zeros(zero_shape)], dtype='object'), axis=0).astype('uint8')
        # fill possible odd frames making average with black
        if new_length%old_length != 0:
            tmp = out_a[fake_new_length-1:new_length+1]
            for i in range(len(tmp)):
                if i == 0: pass
                else:
                    zero_shape = tmp[i-1].shape 
                    tmp[i] = np.mean(np.array([tmp[i-1],np.zeros(zero_shape)], dtype='object'), axis=0).astype('uint8')
    # second case: we have more than one empty frame, so when we have to calculate the average between the frame i and every frame in the step
    else: 
        for i in range(new_length):
            if i == 0: pass
            # dividing the list in chunks
            else:
                j = i * step
                if j < new_length:
                    #print(j)
                    tmp = out_a[j-step:j+1]
                    # for every chunk, calculate the average
                    for z in range(len(tmp)):
                        if tmp[z] is None:
                            #print("index: ", z-1, j)
                            tmp[z] = np.mean(np.array([tmp[z-1],tmp[-1]], dtype='object'), axis=0).astype('uint8')
                    #print(tmp)
        tmp = out_a[new_length-step:new_length]
        # print(tmp)
        # remaining odd frames: average with black
        for i in range(len(tmp)):
            if i == 0: pass
            else:
                #print(i)
                zero_shape = tmp[i-1].shape
                tmp[i] = np.mean(np.array([tmp[i-1],np.zeros(zero_shape)], dtype='object'), axis=0).astype('uint8')
        #print(out_a[new_length-step:new_length])

    return out_a


# ---- VIDEO FUNCTIONS ----

def input_video(filepath):
    in_vid = cv2.VideoCapture(filepath)
    width = int(in_vid.get(3))                                                      # le info sulle dimensioni wxh stanno rispettivamente alle posizioni 3 e 4 dell'header
    height = int(in_vid.get(4))
    fps_in = int(in_vid.get(5))
    frame_in_count = int(in_vid.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_in = frame_in_count/fps_in
    size = (width, height)

    return in_vid, size, fps_in

def read_video(filepath):
    in_vid, size, fps_in = input_video(filepath)
    ret, frame = in_vid.read()

    frames_in = []

    while (in_vid.isOpened()):
        prev_frame = frame[:]
        ret, frame = in_vid.read()
        if ret:
            if (frame is not None):
                frames_in.append(frame)
            cv2.imshow('frame', frame)
        else: break

        if cv2.waitKey(1) & 0xFF == ord('q'): break
    
    in_vid.release()
    return frames_in, size, fps_in

def generate_video(interpolation_mode, fps_output, size):
    fourcc = cv2.VideoWriter_fourcc(*'MPG4')
    filename = 'out_' + str(fps_output) + 'fps_' + interpolation_mode + '.mp4'
    output_video = cv2.VideoWriter(filename, fourcc, fps_output, size, isColor = True)

    return output_video


# ---- MAIN EXECUTION ----

filepath = input("Input video file: ")
frames_in, size, fps_in = read_video(filepath)
while True:
    fps_out = int(input("Video output FPS: "))
    if fps_out <= fps_in: print("ERROR: FPS output must be higher than input!")
    else: break
interp_mode = input("Select interpolation mode [dup,blend]: ").lower()
multiplier = round(fps_out/fps_in)
l_frames_in = len(frames_in)
l_frames_out = l_frames_in * multiplier

if interp_mode == 'dup': frames_out = dup(frames_in, l_frames_out)
elif interp_mode == 'blend': frames_out = blend(frames_in, l_frames_out)

output_video = generate_video(interp_mode, fps_out, size)

for f in frames_out:
    output_video.write(f)

output_video.release()
cv2.destroyAllWindows()