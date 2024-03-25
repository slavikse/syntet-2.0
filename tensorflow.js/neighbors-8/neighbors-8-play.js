'use strict'

async function neighbors8Play() {
  // todo нужно только для обучения машины
  const isNeighboring = _hasNeighboring()

  const inputs = _getInputs(isNeighboring)
  const labels = _getLabels()

  const predictions = await modelPredict(inputs.concat(labels))

  // todo fn
  const maxValue = Math.max(...predictions)
  const predictionIndex = predictions.indexOf(maxValue)

  // todo покрасить ячейку
  state.machine.cellIndex = state.field[predictionIndex]

  const isNeighboringNext = _hasNeighboring()

  console.log('isNeighboringNext', isNeighboringNext)
  console.log('predictions', predictions)
  console.log('predictionIndex', predictionIndex)

  const trainingData = _getTrainingData(isNeighboringNext)

  addTrainingData(trainingData)

  if (isNeighboringNext) {
    modelFit()
    console.log('РЯДОМ!')
  }

  // todo вызывать при проигрыше  modelFit()
}

function _hasNeighboring() {
  const cellQuantity = getCellQuantity()
  const playerIndex = state.player.cellIndex
  const machineIndex = state.machine.cellIndex

  const indexesPlayerCells = [
    playerIndex - cellQuantity, // top
    playerIndex + 1, // right
    playerIndex + cellQuantity, // bottom
    playerIndex - 1, // left
  ]

  return indexesPlayerCells.includes(machineIndex)
}

/**
 * @param isNeighboring {boolean}
 * @returns {number[]}
 */
function _getInputs(isNeighboring) {
  // todo нужно делить или нет?
  const inputs = [state.player.cellIndex / getFieldSize()]

  if (isNeighboring) {
    inputs.push(getPositive())
  } else {
    inputs.push(getNegative())
  }

  return inputs
}

/**
 * @returns {number[]}
 */
function _getLabels() {
  return state.field.map(cellValue => {
    return cellValue ?? getProbably()
  })
}

/**
 * @param isNeighboring {boolean}
 * @returns {{inputs: number[], labels: number[]}}
 */
function _getTrainingData(isNeighboring) {
  return {
    inputs: _getInputs(isNeighboring),
    labels: _getLabels(),
  }
}
