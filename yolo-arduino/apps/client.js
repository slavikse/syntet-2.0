'use strict'

const http = require('http')
// const five = require('johnny-five')

// const board = new five.Board()

// let ledRed
// let ledYellow

// board.on('ready', () => {
//   ledRed = new five.Led(13)
//   ledYellow = new five.Led(12)

//   ledYellow.toggle()
//   // board.on('exit', () => {})
// })

const headTemplate = `
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
</head>
`

const styleTemplate = `
<style>
  body {
    margin: 5px auto 0;
    width: 100%;
    max-width: 800px;
  }

  button {
    padding: 8px;
    font-size: 20px;
  }

  .mt-1 {
    margin-top: 1rem;
  }

  .mt-2 {
    margin-top: 2rem;
  }

  .ml-1 {
    margin-left: 1rem;
  }

  .flex {
    display: flex;
  }

  .border {
    border: 1px solid black;
  }

  .block {
    display: block;
  }
</style>
`

const bodyTemplate = `
<body>
  <canvas
    id="canvas"
    class="block border"
  ></canvas>

  <video
    id="camera"
    class="mt-1 block border"
  ></video>

  <div class="mt-2 flex">
    <!--
    <button
      onclick="sendCommand('ledRed.toggle()')"
    >
      ledRed
    </button>
    -->
  </div>
</body>
`

const scriptTemplate = `
<script>
const pythonApi = 'http://192.168.31.201:8000/'
const arduinoApi = 'http://192.168.31.108/'

let lastActionName = ''

async function sendImage(data, endpoint) {
  const formData = new FormData()
  formData.append('image', data)

  return await fetch(pythonApi + endpoint, {
    mode: 'cors',
    method: 'POST',
    body: formData,
  })
}

async function sendArduinoAction(name) {
  if (name === lastActionName) {
    return
  }

  lastActionName = name

  const actions = {
    Green: '1',
    White: '2',
  }

  await fetch(arduinoApi + actions[name], {
    mode: 'no-cors',
    // headers: {
    //   'Content-Type': 'application/json',
    // },
  });
}

async function sendCommand(data) {
  return await fetch('/', {
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
    body: JSON.stringify({ data }),
  })
}
</script>

<script>
const ctx = canvas.getContext('2d')
const uniqueBoxes = []
const scheduleDelay = 1000

const cameraSize = {
  maxWidth: 150,
}

const canvasSize = {
  maxWidth: 300,
  width: 600,
  height: 600,
}

camera.style.width = '100%'
camera.style.maxWidth = cameraSize.maxWidth

canvas.style.width = '100%'
canvas.style.maxWidth = canvasSize.maxWidth

navigator.mediaDevices
  .getUserMedia({
    video: {
      facingMode: 'environment',
    },
  })
  .then(stream => {
    camera.srcObject = stream
    camera.play()

    conveyor()
  })

function conveyor() {
  canvas.toBlob(async blob => {
    scheduledLaunch()
    // console.log('Image:', Math.round(blob.size / 1024), 'kb')

    const response = await sendImage(blob, 'yolo-image')
    const { sizes, classes, names } = await response.json()

    drawCanvas()

    sizes[0].forEach((size, sizeIndex) => {
      const cls = classes[0][sizeIndex]
      const name = names[0][cls]
      const hash = name + String(cls)

      if (uniqueBoxes.includes(hash)) {
        return
      }

      uniqueBoxes.push(hash)
      drawBox(size, cls, name)

      console.log('name', name)
      sendArduinoAction(name)
    })
  })
}

function drawCanvas() {
  canvas.width = canvasSize.width
  canvas.height = canvasSize.height

  ctx.drawImage(camera, 0, 0, canvasSize.width, canvasSize.height)
}

function drawBox(size, cls, name) {
  xA = size[0]
  xB = size[2]
  yA = size[1]
  yB = size[3]

  xA -= xB / 2
  yA -= yB / 2

  ctx.beginPath()
  ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'
  ctx.fillRect(xA, yA, xB, yB)

  ctx.font = '30px bold sans'
  ctx.fillStyle = 'rgba(255, 0, 0, 1)'

  const title = name + ': ' + cls
  ctx.fillText(title, xA + 20, yA + 40)
}

function scheduledLaunch() {
  uniqueBoxes.length = 0
  setTimeout(conveyor, scheduleDelay)
}
</script>
`

const html = headTemplate + styleTemplate + bodyTemplate + scriptTemplate

http
  .createServer((req, res) => {
    res.end(html)

    if (req.method === 'POST') {
      executeCommand(req)
    }
  })
  .listen(8080)

function executeCommand(req) {
  let data = ''

  req.on('data', (chunk) => {
    data += chunk.toString()
  })

  req.on('end', () => {
    const body = JSON.parse(data)
    console.log('body', body.data)
    // для выполнения команд (вызов функции) на Nodejs сервере.
    // eval(body.data)
  })
}

console.log('http://192.168.31.201:8080')
