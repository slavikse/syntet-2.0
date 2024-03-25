'use strict'

const _BLOCKED = -0.99
const _PLAYER = -0.95

const _POSITIVE = 0.9
const _NEGATIVE = -0.8
const _PROBABLY = 0.2

const _TF = window.tf
const _UNITS = 2 ** 5
const _EPOCHS = 200

const _training = {
  inputs: [],
  labels: [],

  clear() {
    this.inputs = []
    this.labels = []
  },
}

function getBlocked() {
  return _BLOCKED
}

function getPlayer() {
  return _PLAYER
}

function getPositive() {
  return _POSITIVE
}

function getNegative() {
  return _NEGATIVE
}

function getProbably() {
  return _PROBABLY
}

/**
 * @param inputs {Array<number>}
 * @param labels {Array<number>}
 */
function addTrainingData({ inputs, labels }) {
  _training.inputs.push(inputs)
  _training.labels.push(labels)
}

const _model = _setupModel()

function _setupModel() {
  const model = _TF.sequential()

  model.add(_TF.layers.dense({
    inputShape: getFieldSize() + 2, // + player.cellIndex, neighbors.
    activation: 'relu',
    units: _UNITS,
  }))

  model.add(_TF.layers.dense({
    activation: 'sigmoid',
    units: getFieldSize(),
  }))

  model.compile({
    optimizer: 'adam',
    loss: 'meanSquaredError',
  })

  return model
}

async function modelFit() {
  await _model.fit(
    _TF.tensor2d(_training.inputs),
    _TF.tensor2d(_training.labels),
    { epochs: _EPOCHS },
  )

  _training.clear()
}

/**
 * @param state {number[]}
 * @returns {Promise<number[]>}
 */
async function modelPredict(state) {
  return await _model.predict(_TF.tensor2d([state])).data()
}

/** todo
 * скрытые поля - агенты исследователи (случайные действия).
 * одно поле отображено для отображения процесса обучения модели.
 */
/** todo
 * Условие выигрыша - раскрашенные ячейки должны быть рядом. расстояние между ними 1.
 * Решения принимаемые ML отображаются - одно игровое поле
 */
// todo машине нужно будет выставить знак в пустую ячейку, иначе _NEGATIVE_REINFORCEMENT
// todo проверять, занята ячейка или нет. центральная и игрока
function neighbors8RL() {
}
