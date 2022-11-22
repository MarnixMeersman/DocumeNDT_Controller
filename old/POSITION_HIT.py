import numpy as np
import matplotlib.pyplot as plt

#TODO: add sliders for all parameters, i.e. freq, test time and number of hits

# Upper limit is 10 Hz!!!!
# Recommended frequency 3 Hz

freq = 3 # Hz
number_of_hits = 25 #[]

t_wait = np.round(1/(2*freq), 4)

f = open('../dynamic_text_files/grbl.gcode', 'a')
f.truncate(0) # delete previous code
f.write('M08\n')
f.write('G01 Z-10 F50\n')
f.write('G4 P0.5\n')
f.write('M09\n')
f.write('G4 P0.5\n')
f.write('M08\n')
f.write('G38.5 Z150 F100\n') # probe up to 150 mm deep
f.write('G01 Z-0.25 F500\n') # move back 1mm

for i in range(number_of_hits): #start hitting at t_wait interval for i times
    f.write('M09\n')
    f.write('G4 P' + str(t_wait) + '\n')
    f.write('M08\n')
    f.write('G4 P' + str(t_wait) + '\n')

f.close()


