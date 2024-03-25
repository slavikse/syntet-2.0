'use strict'

const _EXECUTION_TIME_LOG = 1_000_000
const _EXECUTION_DELAY = 1_000

const _EXECUTION_DELAY_ELEMENT = document.querySelector('#is-execution-delay')

let _is_execution_delay = false

window.addEventListener('click', _switchExecutionDelay)

function _switchExecutionDelay() {
  _is_execution_delay = !_is_execution_delay
  _EXECUTION_DELAY_ELEMENT.textContent = _is_execution_delay
}

/**
 * Inverse function for calculating the task execution time.
 * @returns {{start(): void, end(number): void}}
 */
function executionTime() {
  let timeStart = 0

  return {
    start() {
      timeStart = performance.now()
    },

    /**
     * @param tick {number}
     */
    end(tick) {
      if (tick % _EXECUTION_TIME_LOG === 0) {
        console.info('task execution time', performance.now() - timeStart)
      }
    },
  }
}

/**
 * @returns {Promise<void>|void}
 */
async function executionDelay() {
  if (_is_execution_delay) {
    return new Promise(resolve => {
      setTimeout(resolve, _EXECUTION_DELAY)
    })
  }
}

/**
 * @param min {number}
 * @param max {number}
 * @returns {number}
 */
function randomIntFromInterval(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min)
}
