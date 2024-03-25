'use strict'

const _CANVAS_ELEMENT = document.querySelector('#canvas')
const _CTX = _CANVAS_ELEMENT.getContext('2d')

const _FIELD_SIZE = 9
const _FIELD_BLOCKED_INDEX = 4
const _CELL_QUANTITY = 3
const _BORDER_SIZE = 10

const _CELL_BLOCKED_COLOR = '#222222'
const _CELL_EMPTY_COLOR = '#555555'
const _CELL_PLAYER_COLOR = 'limegreen'
const _CELL_MACHINE_COLOR = 'crimson'
const _CELL_SIZE = _CANVAS_ELEMENT.width / _CELL_QUANTITY

function getFieldSize() {
  return _FIELD_SIZE
}

function getCellQuantity() {
  return _CELL_QUANTITY
}

function neighbors8Render() {
  _createField()
  _createPlayer()

  _renderField()
}

function _createField() {
  state.field = Array.from({ length: getFieldSize() })
  state.field[_FIELD_BLOCKED_INDEX] = getBlocked()
}

function _createPlayer() {
  while (
    state.player.cellIndex === -1
    || state.player.cellIndex === _FIELD_BLOCKED_INDEX
    ) {
    state.player.cellIndex = randomIntFromInterval(0, state.field.length - 1)
  }

  state.field[state.player.cellIndex] = getPlayer()
}

function _renderField() {
  _CTX.clearRect(0, 0, _CANVAS_ELEMENT.width, _CANVAS_ELEMENT.height)

  let rowIndex = -1

  state.field.forEach((cellValue, absoluteCellIndex) => {
    if (absoluteCellIndex % _CELL_QUANTITY === 0) {
      rowIndex += 1
    }

    const cellIndex = absoluteCellIndex - rowIndex * _CELL_QUANTITY
    const pointX = cellIndex * _CELL_SIZE
    const pointY = rowIndex * _CELL_SIZE

    _paintBorder(pointX, pointY)
    _paintCell(cellValue, pointX, pointY)
  })
}

/**
 * @param pointX {number} Horizontal rendering point.
 * @param pointY {number} Vertical rendering point.
 */
function _paintBorder(pointX, pointY) {
  _CTX.fillStyle = _CELL_BLOCKED_COLOR

  _CTX.fillRect(
    pointX - _BORDER_SIZE,
    pointY - _BORDER_SIZE,
    _CELL_SIZE + _BORDER_SIZE,
    _CELL_SIZE + _BORDER_SIZE,
  )
}

/**
 * @param cellValue {number} The value of the cell of the playing field.
 * @param pointX {number} Horizontal rendering point.
 * @param pointY {number} Vertical rendering point.
 */
function _paintCell(cellValue, pointX, pointY) {
  _CTX.fillStyle = _getCellColor(cellValue)

  _CTX.fillRect(
    pointX,
    pointY,
    _CELL_SIZE,
    _CELL_SIZE,
  )
}

/**
 * @param cellValue {number} The value of the cell of the playing field.
 * @returns {string}
 */
function _getCellColor(cellValue) {
  if (cellValue === getPlayer()) {
    return _CELL_PLAYER_COLOR
  }

  if (cellValue === getBlocked()) {
    return _CELL_BLOCKED_COLOR
  }

  return _CELL_EMPTY_COLOR
}
