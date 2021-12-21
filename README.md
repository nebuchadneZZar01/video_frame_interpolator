# video_frame_interpolator
This is a project for a university subject (Multimedia).

This Python program simulates *ffmpeg*'s `minterpolate` command.

## Requirements
In order execute this program in a Python environment, you need to install the following modules using `pip`:
* opencv
* numpy 

```bash
pip opencv
pip numpy
```

## Usage
```bash
python video_frame_interpolator.py
```
The program will ask to choose an input video file; in this repo is provided a file `asahi.mp4`, used as test during the developement of this script.

Next, is required to enter the desidered new framerate of the output video (it must be higher than the input's one; ex: if the input is 30fps, then at least 31fps must be inserted).

After this, the user has to choose between two interpolation modes:
* `dup`: all the "missing frames" in the output video are equal to their predecessor (so, the frame *i* is a **dup**licate of the frame *i-1*) [FAST];
* `blend`: all the "missing frames" in the output video are given by the mean between their predecessor and their successor (so, the frame *i* is extimated by an average between the frame *i-1* and the frame *i+1*) [SLOW].

The output file name will have the form **`out_<new_framerate>fps_<interpolation_mode>.mp4`**.

## Known bugs
* Giving an odd framerate output (i.e.: 31, 63, 77, ...) results in an output with different duration than the input.

## TO-DOs
- [ ] support to framerates lower than the input one (for example, convert a 30fps video in a 15fps one);
- [ ] `mci` ffmpeg command: **m**otion **c**ompensated **i**interpolation via **motion vectors**.
- [ ] minor usability changes. 
