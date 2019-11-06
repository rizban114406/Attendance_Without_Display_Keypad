#!/bin/bash

sleep 15s
while :
do
read -r url < /root/heartBitUrl.txt
if curl -m 10 "$url" > /dev/null
then
cd /
cd /root/
sudo python sasEventsPrevious.py
cd /
sleep 10s
fi
sleep 2s
done

