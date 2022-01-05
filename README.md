# video_frame_interpolator
This is a project for a university subject (Multimedia).

This Python program simulates *ffmpeg*'s `minterpolate` command.

## Requirements
In order execute this program in a Python environment, you need to install the following modules using `pip`:
* numpy
* opencv
* pyqt5

```bash
pip install numpy
pip install opencv-python
pip install pyqt5
```

## Usage (to be updated, not the script has a GUI)
```bash
python interpolator.py
```
The program will ask to choose an input video file; in this repo is provided a file `asahi.mp4`, used as test during the developement of this script.

Next, is required to enter the desired new framerate of the output video (higher or lower than the input one).

If the choosen framerate is higher than the input one, the user has to choose between two interpolation modes:
* `dup`: all the "missing frames" in the output video are equal to their predecessor (so, the frame *i* is a **dup**licate of the frame *i-1*) [**FAST**];
* `blend`: all the "missing frames" in the output video are **blend**ed calculating the mean between their predecessor and their successor (so, the frame *i* is extimated by an average between the frame *i-1* and the frame *i+1*) [**SLOW**].

If, instead, the choosen framerate is lower than the input one, the output will result in a video with a **reduced** framerate (for example, from 30fps to 5fps).

The output file name will have the form **`out_<new_framerate>fps_<interpolation_mode>.mp4`**.

## Known bugs
* Giving an odd framerate output (i.e.: 31, 63, 77, ...) results in an output with different duration than the input;
* ~~Commandline gives an ambiguous `[ERROR:0] global /.../opencv/modules/videoio/src/cap_ffmpeg_impl.hpp (2811) open VIDEOIO/FFMPEG: Failed to initialize VideoWriter`, but it actually calls it and successfully writes the output video.~~

## TO-DOs
- [x] support to framerates lower than the input one (for example, convert a 30fps video in a 15fps one);
- [x] GUI in pyQt5;
- [ ] `mci` ffmpeg command: **m**otion **c**ompensated **i**interpolation via **motion vectors**.
