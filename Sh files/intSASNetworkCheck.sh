#!/bin/bash
sleep 5m

read -r url < /root/heartBitUrl.txt
if curl -m 10 "$url" > /dev/null
then
echo "Connected"
else
sudo reboot
fi
