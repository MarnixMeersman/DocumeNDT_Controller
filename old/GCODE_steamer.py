import serial
import time

# Open grbl serial port
s = serial.Serial('/dev/tty.usbmodem101', 115200)

# Open g-code file
f = open('../dynamic_text_files/grbl.gcode', 'r');

# Wake up grbl
print("Starting up DocumeNDT firmware...")
temp = "\r\n\r\n"
s.write(temp.encode())
time.sleep(2)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input

# Stream g-code to grbl
for line in f:
    l = line.strip() # Strip all EOL characters for consistency
    print('Sending: ' + l)
    tempo = l + '\n'
    s.write(tempo.encode()) # Send g-code block to grbl
    grbl_out = s.readline() # Wait for grbl response with carriage return
    print(' : ' + str(grbl_out.strip()))

# Wait here until grbl is finished to close serial port and file.
input("  Press <ENTER> to exit and disable the control firmware.")

# Close file and serial port
f.close()
s.close()