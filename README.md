# DriveSafePi

## **Environment Setup**

### Hardware

- Camera setup: Make sure the camera is fixed (use tape) in a right place so that it can capture the clear face picture
- GPS setup: Wait for GPS module searching satellited and make sure it is fixed to the satellite (the build-in LED blinks indicate GPS module is prepaired)
- Network setup: Use a smartphone to provide hotspot to RPi.

### Software (Environment Dependency)

Python 3.7.3 version has been tested  

- For gps function `sudo apt-get install gpsd gpsd-clients`
- For face detection function
    
    Install cmake for the installation of opencv: `sudo apt-get install cmake`
    
    Then install python packages: `pip3 install imutils dlib python-opencv scipy numpy` 
    
- For warning `sudo apt-get install espeak`
- For Firebase API `pip3 install pyrebase`

### Run 
`python main.py`