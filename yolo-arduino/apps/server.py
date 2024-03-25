from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2

model = None
host = '0.0.0.0' # '192.168.31.201'
port = 8000


class Yolo():
  def __init__(self, path):
    global model
    # path='yolov8n.pt'
    model = YOLO(path)

    # self.test_predict()
    # self.activate_camera()

  def test_predict(self):
    model.predict(
      source='datasets/valid/images/bc642854-my_photo-18.jpg',
      show=True,
      show_labels=True,
    )

  def activate_camera(self):
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    while True:
      _, frame = cam.read()

      model.predict(
        source=frame,
        show=True,
        show_labels=True,
      )

      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cam.release()
    cv2.destroyAllWindows()


class WebServer():
  def __init__(self, image_path):
    global model
    app = Flask(__name__)
    CORS(app)

    @app.post('/yolo-image')
    def yolo_image():
      image = request.files['image']
      image.save(image_path)

      # image.stream - yolo does not support?
      results = model.predict(source=image_path)
      data = self.preparingData(results)
      return jsonify(data)

    app.run(host=host, port=port, debug=False)


  def preparingData(self, results):
    sizes = []
    classes = []
    names = []

    for result in results:
      sizes.append(result.boxes.xywh.cpu().numpy().data.tolist())
      classes.append(result.boxes.cls.cpu().numpy().data.tolist())
      names.append(result.names)

    return {
      'sizes': sizes,
      'classes': classes,
      'names': names,
    }


Yolo('/home/slavikse/code/projects/syntet-2.0/yolo-arduino/runs/detect/train3/weights/best.pt')
WebServer('/home/slavikse/code/projects/syntet-2.0/temp/image-from-client.png')
