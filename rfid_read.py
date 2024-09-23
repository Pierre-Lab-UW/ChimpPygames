import serial

device = serial.Serial('/dev/serial0',9600,timeout=1)
while True:
    tag = device.read(16)  # Tries to read the ISO tag format made of 14 digits
    if len(tag) != 0:  # If something has been read, print it then break out of the loop
        print(tag)
        break