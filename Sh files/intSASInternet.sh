#!/bin/bash
sleep 10s

while :
do
read -r url < /root/heartBitUrl.txt
if curl -m 10 "$url" > /dev/null
then
echo "Modem IS Connected"
sleep 5m
else
sudo killall pppd
usb_modeswitch -R -v 12d1 -p 1001
sudo pppd call gprs updetach debug
ifconfig ppp0
fi
sleep 2s
done
