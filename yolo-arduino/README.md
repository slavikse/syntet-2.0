# Local WiFi network

Get an ip address for local network access `hostname -I` `[ip:8000]`.\
Disable or allow the port in the firewall `ufw allow 9000/tcp`.

navigator.mediaDevices.getUserMedia with http server:\
`chrome://flags/#unsafely-treat-insecure-origin-as-secure`

# CLI Project

```
npm run server (launching Yolo on Flask)
npm run client (a connected arduino is required to start)
npm run tunnel (access to the client via the Internet)
```

# CLI Yolo

```
yolo mode=train \
  data=config.yaml \
  model=yolov8n.pt \
  task=detect \
  epochs=100 \
  batch=3 \
  imgsz=640

yolo mode=predict \
  model=runs/detect/train2/weights/best.pt \
  task=detect \
  source=datasets/valid/images/bc642854-my_photo-18.jpg \
  show=True

yolo mode=val \
  data=config.yaml
  task=detect
  model=datasets/valid/images/bc642854-my_photo-18.jpg \
```

# Directory

```
/datasets
  /train
    /images
    /labels
  /test
    /images
    /labels
  /valid
    /images
    /labels
```

# Arguments

```
model: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
mode: train, val, predict
task: detect, segment, classify
```

# Install

[anaconda](https://anaconda.com/download)\
[flask](https://flask.palletsprojects.com/en/latest/quickstart)\
[label-studio](https://labelstud.io/guide/quick_start)\
[yolo](https://docs.ultralytics.com/quickstart) download model: yolo model=yolov8s.pt\
[arduino](https://arduino.cc/en/software)\
[johnny-five](https://johnny-five.io/platform-support/#arduino-uno)\
firmware arduino for use via node.js:\
File - Examples - Firmata - StandardFirmataPlus\
[Chrome USB debugging](https://developer.android.com/studio/run/device)

[Iskra JS Linux](https://easimonenko.github.io/blog/2016/12/07/iskra-js-in-linux-getting-started-guide.html)
sudo usermod -a -G dialout [username]
