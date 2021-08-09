# iss_tracker
ISS wHAT inky display of current ISS location over the world.  

## Requirements
Raspberry Pi (zero will work, but Pi3 and newer recommended)  
Pimoroni Inky wHAT 300x400 e-ink display  
  
## Install Instructions
Enable I2C and SPI in sudo raspi-config  
sudo pip install pyephem  
sudo pip install inky[rpi,fonts]  
sudo apt-get install python-mpltoolkits.basemap  
Make the script executable chmod +x iss.sh  
Add the following to crontab @reboot /home/pi/Projects/iss_tracker/iss.sh  
