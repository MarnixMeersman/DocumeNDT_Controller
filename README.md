# DocumeNDT Control Software - WALL-E

## Quick Start
First copy this repository to your pc running the following in your python terminal (Python 3.9 recommended)
```
git clone https://github.com/MarnixMeersman/DocumeNDT_Controller
```

Then install al required libraries using: 
```
pip install -r requirements.txt
```


Then proceed with reading this README. Have fun!

## Performing your first cycle: main_grid.py
When you cloned this repo, you will see two main_...py files: main_grid and main_inputfile. We recommend to use main_grid for your first test
cycle and use the output of your first cycle to re-run the other cycles uing main_inputfile.py. 

### This is what you need to do first

1. Adjust your portname, if you are using mac is should be something like: ```portname = '/dev/tty.usbmodem2101'```. For Windows, try  ```portname = 'COM3' ``` or ```portname = COM4```. 
  - If you struggle to find your portname, have a look 
    - here for Mac : https://stackoverflow.com/questions/14074413/serial-port-names-on-mac-os-x
    - here for Windows: https://www.folkstalk.com/2022/09/problem-in-choosing-port-in-arduino-stack-overflow-with-code-examples.html
2. Define the speed limit for WALL-E. We recommend to not go above 15 000 steps per second for the lifetime of the motors.
    <img width="361" alt="image" src="https://user-images.githubusercontent.com/57674797/203263717-124901b5-f781-4642-8077-2b286b65fa57.png">

3. Run your file. Your terminal should show you a clickable link. It should automatically open your browser. If not, paste the url in your browser (only tested for Chrome and Safari).

    <img width="318" alt="image" src="https://user-images.githubusercontent.com/57674797/203264250-99ce2169-5fcd-4d6f-92fa-2361064fd65c.png">

4. You should see something like this:
![ezgif-4 com-gif-maker](https://user-images.githubusercontent.com/57674797/203266417-7e67f9df-a6b1-4438-8881-09e594050bf9.gif)

Hopefully the interface in intuitive by itself, still here a few highlights:
  * To start, DISABLE the power of WALL-E and place the head at your origin location, then turn on two power buttons.
  * Secondly, open your interface and click the big red SET ORIGIN! button. This saves the cureent location as the origin. 
  * Measure the width and height of the working area relative to the origin point and enter it into the input bars.
  


