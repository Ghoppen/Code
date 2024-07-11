#!/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/pi/Documents
sleep 90
cd /home/pi/Documents/dev
sudo pon provider
while :
do
		sudo poff provider
		/usr/bin/python3 nmeaReadSend.py
		echo Coordinates should have been sent
		sleep 3
done
