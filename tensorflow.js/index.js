'use strict'

/**
 * It is regulated for the power of the system being started.
 * @type {number} Transferring control to the browser for each N tick.
 */
const _BROWSER_CONTROL = 100_000
const _RENDER_TIMEOUT = 10 // todo 1_000

const _EXECUTION_TIME = executionTime()

/**
 * @type {function} Global reference to a functions with calculations.
 */
const _taskRender = neighbors8Render
const _taskPlay = neighbors8Play
const _taskRL = neighbors8RL

let _is_playable = true
let _tick = 0

_taskRender()
_gameLoop()

async function _gameLoop() {
  _EXECUTION_TIME.start()

  await _workload()

  _EXECUTION_TIME.end(_tick)
  _ticker()

  await executionDelay()

  // todo
  //_nextMicroTask()
}

// todo когда можно не ждать _taskPlay - modelPredict
async function _workload() {
  _render()
  await _taskPlay()
  _taskRL()
}

function _render() {
  if (_is_playable) {
    _is_playable = false

    setTimeout(() => requestAnimationFrame(() => {
      _taskRender()
      _is_playable = true
    }), _RENDER_TIMEOUT)
  }
}

function _ticker() {
  _tick += 1

  if (_tick === Number.MAX_SAFE_INTEGER) {
    _tick = 0
  }
}

function _nextMicroTask() {
  if (_tick % _BROWSER_CONTROL === 0) {
    setTimeout(_gameLoop)
  } else {
    //queueMicrotask(_runner)
    _gameLoop()
  }
}
