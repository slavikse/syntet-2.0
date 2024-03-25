'use strict'

const HttpModule = require('http')
const WifiModule = require('@amperka/wifi')
const RobotModule = require('@amperka/robot-2wd')

const ssid = ''
const passward = ''
const longPollingTimeout = 1000
// Should be an order of magnitude larger than longPollingTimeout.
const resetWifiTimeout = 3000
const snapshotInterval = 10000

const state = {
  wifi: {},
  longPollingTimeoutId: -1,

  httpOptions: {
    headers: {
      'Accept': 'text/html',
    },
    protocol: 'http:',
    host: 'f8a720f562e111b26b718eb85d0e136f.serveo.net',
    path: '/json',
    port: '80',
  },
}

class Tools {
  constructor() {
    this.resetTimerId = -1
  }

  snapshot() {
    const memory = process.memory()
    print(`memory: usage ${memory.usage}, free ${memory.free}`)
  }

  delayedResetWifi() {
    this.clearResetWifiTimer()

    this.resetTimerId = setTimeout(() => {
      state.wifi.reset()
    }, resetWifiTimeout)
  }

  clearResetWifiTimer() {
    clearTimeout(state.longPollingTimeoutId)
    clearTimeout(this.resetTimerId)
  }
}

const tools = new Tools()

class WiFi {
  constructor(callback) {
    this.wifi = WifiModule.setup(err => {
      this.setup(err, () => {
        this.wifi.on('err', err => {
          print(err)
          this.reset()
        })

        this.wifi.connect(ssid, passward, err => {
          this.connected(err, callback)
        })
      })
    })
  }

  setup(err, callback) {
    if (err) {
      print(err)
      this.reset()
      return
    }

    print('Wi-Fi init...')
    callback()
  }

  connected(err, callback) {
    if (err) {
      print(err)
      this.reset()
      return
    }

    print('Wi-Fi connected!')
    callback()
  }

  reset() {
    tools.clearResetWifiTimer()

    this.wifi.reset(err => {
      if (err) {
        print(err)
        return
      }

      print('Wi-Fi reseted!')
      wifiInit()
    })
  }
}

class HTTP {
  constructor() {
    // Serial3.setConsole(true)
  }

  request(requestBody, callback) {
    HttpModule.get(state.httpOptions, res => {
      let contents = ''

      res.on('data', data => {
        contents += data
      })

      res.on('close', () => {
        if (contents.length > 0) {
          callback(JSON.parse(contents))
        }
      })
    }).on('error', err => {
      // TODO
      print('повторить запрос')
      requestBody()
      print(err)
    });
  }

  longPolling(callback) {
    tools.delayedResetWifi()

    const requestBody = () => this.longPolling(callback)

    this.request(requestBody, contents => {
      tools.clearResetWifiTimer()

      state.longPollingTimeoutId = setTimeout(() => {
        requestBody()
      }, longPollingTimeout)

      if (contents) {
        callback(contents)
      }
    })
  }
}

class Robot {
  constructor() {
    this.MIN_SPEED = 0.4
    this.MAX_SPEED = 1.0
    this.TURNED_OFF = 0.0

    this.robot = RobotModule.connect()

    this.speed = this.MIN_SPEED
    this.step = 0.1
    // stop | backward | right
    this.status = 'stop'
  }

  stop() {
    if (this.status === 'stop') {
      return
    }

    this.status = 'stop'
    this.robot.stop()
  }

  // FIXME Запуская мотор вперёд - выключается wifi модуль.
  // forward() {
  //     this.robot.go({
  //       l: this.speed,
  //       r: this.speed,
  //     })
  // }

  backward() {
    if (this.status === 'backward') {
      return
    }

    this.status = 'backward'

    this.robot.go({
      l: -this.speed,
      r: -this.speed,
    })
  }

  // TODO добавить left
  right() {
    if (this.status === 'right') {
      return
    }

    this.status = 'right'

    this.robot.go({
      l: this.TURNED_OFF,
      r: -this.speed,
    })
  }

  // TODO нужно запустить двигатель с этой скоростью
  // increase() {
  //   this.speed += this.step

  //   if (this.speed > this.MAX_SPEED) {
  //     this.speed = this.MAX_SPEED
  //   }
  // }

  // TODO нужно запустить двигатель с этой скоростью
  // decrease() {
  //   this.speed -= this.step

  //   if (this.speed < this.MIN_SPEED) {
  //     this.speed = this.MIN_SPEED
  //   }
  // }

  acceleration() {
    const values = [0.25, 0.5, 0.75]
    const acceleration = values[Math.floor(Math.random() * values.length)]

    // TODO
    print('acceleration', acceleration)

    this.robot.acceleration(acceleration)
  }
}

const http = new HTTP()
const robot = new Robot()

function wifiInit() {
  state.wifi = new WiFi(() => {
    // TODO добавить звуковой сигнал после подключения к wifi
    // TODO отправить сигнал, что робот готов. клиент будет слушать и отобразит в интерфейсе

    http.longPolling(contents => {
      print('command', contents.command)
      // robot[contents.command]()
    })
  })
}

wifiInit()

setInterval(() => {
  tools.snapshot()
}, snapshotInterval);
