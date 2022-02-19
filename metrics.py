from bz2 import compress
from email import header
import cv2
from matplotlib.pyplot import axis
import numpy as np
import pandas as pd
from skimage.metrics import structural_similarity as ssim

def input_video(filepath):
    in_vid = cv2.VideoCapture(filepath)
    width = int(in_vid.get(3))                                                      
    height = int(in_vid.get(4))
    size = (width, height)

    return in_vid, size

def read_video(filepath):
    in_vid, size = input_video(filepath)
    ret, frame = in_vid.read()

    frames_in = []

    while (in_vid.isOpened()):
        prev_frame = frame[:]
        ret, frame = in_vid.read()
        if ret:
            if (frame is not None):
                frames_in.append(frame)
        else: break
    
    in_vid.release()
    return frames_in, size

def avg(list): return sum(list)/len(list)

def PSNR(original, interpolated, size):
    mse = np.mean((original - interpolated)**2)

    if (mse == 0): return 100
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel/np.sqrt(mse))
    return psnr

def PSNR_video(original_video, interpolated_video, size):
    video_length = len(interpolated_video)

    PSNRs = [ ]

    for i in range(video_length):
        PSNRs.append(PSNR(original_video[i], interpolated_video[i], size))

    min_psnr = min(PSNRs)
    max_psnr = max(PSNRs)
    avg_psnr = avg(PSNRs)

    return min_psnr, max_psnr, avg_psnr

def MSE_video(original_video, interpolated_video):
    video_length = len(interpolated_video)

    MSEs = [ ]

    for i in range(video_length):
        MSEs.append(np.mean((original_video[i] - interpolated_video[i])**2))

    min_mse = min(MSEs)
    max_mse = max(MSEs)
    avg_mse = avg(MSEs)

    return min_mse, max_mse, avg_mse

def SSIM_video(original_video, interpolated_video):
    video_length = len(interpolated_video)

    SSIMs = [ ]

    for i in range(video_length):
        SSIMs.append(ssim(original_video[i], interpolated_video[i], multichannel=True))

    min_ssim = min(SSIMs)
    max_ssim = max(SSIMs)
    avg_ssim = avg(SSIMs)

    return min_ssim, max_ssim, avg_ssim


ov_path = input("Original video path: ")
ov_frames, size = read_video(ov_path)

dup_path = input("Duplication video path: ")
dup_frames, size = read_video(dup_path)

blend_path = input("Blending video path: ")
blend_frames, size = read_video(blend_path)

farneback_path = input("Farneback video path: ")
farneback_frames, size = read_video(farneback_path)

lk_path = input("Lucas-Kanade video path: ")
lk_frames, size = read_video(lk_path)

dup_min_mse, dup_max_mse, dup_avg_mse = MSE_video(ov_frames, dup_frames)
dup_min_psnr, dup_max_psnr, dup_avg_psnr = PSNR_video(ov_frames, dup_frames, size)
dup_min_ssim, dup_max_ssim, dup_avg_ssim = SSIM_video(ov_frames, dup_frames)

blend_min_mse, blend_max_mse, blend_avg_mse = MSE_video(ov_frames, blend_frames)
blend_min_psnr, blend_max_psnr, blend_avg_psnr = PSNR_video(ov_frames, blend_frames, size)
blend_min_ssim, blend_max_ssim, blend_avg_ssim = SSIM_video(ov_frames, blend_frames)

farneback_min_mse, farneback_max_mse, farneback_avg_mse = MSE_video(ov_frames, farneback_frames)
farneback_min_psnr, farneback_max_psnr, farneback_avg_psnr = PSNR_video(ov_frames, farneback_frames, size)
farneback_min_ssim, farneback_max_ssim, farneback_avg_ssim = SSIM_video(ov_frames, farneback_frames)

lk_min_mse, lk_max_mse, lk_avg_mse = MSE_video(ov_frames, lk_frames)
lk_min_psnr, lk_max_psnr, lk_avg_psnr = PSNR_video(ov_frames, lk_frames, size)
lk_min_ssim, lk_max_ssim, lk_avg_ssim = SSIM_video(ov_frames, lk_frames)

dup_mse = pd.DataFrame({'dup_mse': [dup_min_mse, dup_max_mse, dup_avg_mse]})
dup_psnr = pd.DataFrame({'dup_psnr': [dup_min_psnr, dup_max_psnr, dup_avg_psnr]})
dup_ssim = pd.DataFrame({'dup_ssim': [dup_min_ssim, dup_max_ssim, dup_avg_ssim]})

blend_mse = pd.DataFrame({'blend_mse': [blend_min_mse, blend_max_mse, blend_avg_mse]})
blend_psnr = pd.DataFrame({'blend_psnr': [blend_min_psnr, blend_max_psnr, blend_avg_psnr]})
blend_ssim = pd.DataFrame({'blend_ssim': [blend_min_ssim, blend_max_ssim, blend_avg_ssim]})

farneback_mse = pd.DataFrame({'farneback_mse': [farneback_min_mse, farneback_max_mse, farneback_avg_mse]})
farneback_psnr = pd.DataFrame({'farneback_psnr': [farneback_min_psnr, farneback_max_psnr, farneback_avg_psnr]})
farneback_ssim = pd.DataFrame({'farneback_ssim': [farneback_min_ssim, farneback_max_ssim, farneback_avg_ssim]})

lk_mse = pd.DataFrame({'lk_mse': [lk_min_mse, lk_max_mse, lk_avg_mse]})
lk_psnr = pd.DataFrame({'lk_psnr': [lk_min_mse, lk_avg_psnr, lk_max_psnr]})
lk_ssim = pd.DataFrame({'lk_ssim': [lk_min_ssim, lk_avg_ssim, lk_max_ssim]})

df = pd.concat([dup_mse, dup_psnr, dup_ssim,\
                blend_mse, blend_psnr, blend_ssim,\
                farneback_mse, farneback_psnr, farneback_ssim,\
                lk_mse, lk_psnr, lk_ssim], axis=1)

df.index = ['min', 'max', 'avg']

print(df)

save_fp = input("Enter save path: ")

df.to_csv(save_fp)

