#!/bin/bash

sleep 13s

while  :
do
read -r url < /root/heartBitUrl.txt
if curl -m 10 "$url" > /dev/null
then
cd /
cd /root/
sudo python sasGetConfiguration.py
cd /
break
fi
sleep 2s
done

while :
do
read -r url < /root/heartBitUrl.txt
if curl -m 10 "$url" > /dev/null
then
cd /
cd /root/
sudo python sasGetConfiguration.py
cd /
sleep 10m
fi
sleep 2s
done

