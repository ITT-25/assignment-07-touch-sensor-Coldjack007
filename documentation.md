# Build a Camera-Based Touch Sensor

## Build Process
- I elected to use the stand the camera came with, so as to not have to tape the camera to the box. Instead, I marked the spots on which the stand stands with pencil. This was done to make potential assembly and disassembly easier.
- The area the camera captures is marked on the paper on top.
- The correct rotation of the box is aided by the label "Zu dir" on the box, which should face you. Same goes for the acryllic sheet.
- The acryllic sheet can be placed nicely on the box vertically. When placing it horizontally, the left line of the paper is to be placed on the left side of the box, so that the lines overlap.

## Calibration step
- Once the pprogram starts, the program waits for a bit to let the camera get used to the lighting environment.
- Then it records images for three seconds, takes the mean of these images and then calculates the absdiff from every future incoming image.

## Touch Detection
- I decided to reuse multiple techniques from previous ITT projects, as I worked with limmited time.
- The touch detection is similar to the fingertip detection from the Aruco-markers, detecting contours in the image, and using the topmost point of the contour that fits a fingertip most closely.
- The program differentiates between taps and movement. If the finger for less than a certain amount of time, it is registered as a tap. If it exceeds that time, it continuously tracks it as movement until the finger is no longer detected.


# Touch-based Text Input

## Concepts
- I planned to use the 1$-Recognizer to detect the characters.
- For the necessary data, I would have used the program from the gesture recognition assignment.