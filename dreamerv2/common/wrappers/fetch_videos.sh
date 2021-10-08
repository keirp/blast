#!/bin/bash
wget -c https://s3.amazonaws.com/kinetics/700_2020/train/k700_train_171.tar.gz
tar -xf k700_train_171.tar.gz
rm k700_train_171.tar.gz

mv driving\ car driving_car

VIDEOS=driving_car/*.mp4

mkdir videos

for file in $VIDEOS;
do
    ffmpeg -i $file -vf scale=64:64,setsar=1 "videos/$(basename $file)"
done
rm -rf driving_car