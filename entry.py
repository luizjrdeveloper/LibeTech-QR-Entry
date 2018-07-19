import subprocess
import sys
import os
import hashlib
import time
import config
import RPi.GPIO as GPIO

# Configuring BCM, GPIO Numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Configurando pino como out(Pino de Saída)
GPIO.setup(config.door_lock, GPIO.OUT)
GPIO.setup(config.status, GPIO.OUT)
GPIO.setup(config.green, GPIO.OUT)
GPIO.setup(config.red, GPIO.OUT)
# Configuring the Pin Direction
GPIO.output(config.door_lock, GPIO.LOW)
GPIO.output(config.status, GPIO.HIGH)
GPIO.output(config.green, GPIO.LOW)
GPIO.output(config.red, GPIO.LOW)

# Clearing Existing Files
with open('tmp.txt', 'w'): pass

# Starting ZBar in a Subprocess;
# The Objective and save the extract of the last QR read in the file tmp.txt
# Need change /dev/video0 for your camera device
print "Starting ZBar"
zbarcam = subprocess.Popen("./zbar/bin/zbarcam --raw --nodisplay --prescale=300x300 /dev/video0 >> tmp.txt", shell=True)
print "ZBar is running."
time.sleep(0.4)
print "Waiting for a new validation..."

try:
	while (1):
		if os.path.isfile("tmp.txt") and os.path.getsize("tmp.txt")>0:
			os.system('wget --quiet http://www.libetech.com/valid.txt')
			val = subprocess.check_output(["tail", "-n", "1", "tmp.txt"]).strip()
			try:
				val_hash = hashlib.md5(val).hexdigest()
				#print "Hashed Key from ZBAR QR Reading: %s" % val_hash
				approved = subprocess.check_output(["tail", "-n", "1", "valid.txt"])
				#print "Approved Hash from Web: %s" % approved
				os.system('rm valid.txt')
				if approved in val_hash:
					print "Valid QR Code Key"
					GPIO.output(config.door_lock, GPIO.HIGH)
					GPIO.output(config.green, GPIO.HIGH)
					time.sleep(2)
					GPIO.output(config.door_lock, GPIO.LOW)
					GPIO.output(config.green, GPIO.LOW)
					time.sleep(0.4)
					print "Waiting for a new validation..."
				else:
					print "Invalid QR Code"
					while flashes < 3:
						GPIO.output(config.red, GPIO.HIGH)
						time.sleep(0.2)
						GPIO.output(config.red, GPIO.LOW)
						time.sleep(0.2)
						flashes = flashes + 1
					flashes = 0
					time.sleep(0.4)
					print "Waiting for a new validation..."
			with open('tmp.txt', 'w'): pass

# Undoing the GPIO modifications and Closing the zbar subprocesses
except (KeyboardInterrupt, SystemExit):
	print "\nClearing Pin States (GPIO)"
	GPIO.cleanup()
	print "Clearing temporary files"
	os.system('sudo rm -f tmp.txt')
	print "Closing ZBar"
	zbarcam.terminate()
	print "Closing Aplication"
	time.sleep(0.1)
