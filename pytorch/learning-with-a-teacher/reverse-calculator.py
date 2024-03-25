# Loss with this neural network configuration: 🤯loss: ~0.0061🤯
# The algorithm will predict the operation (one of: + - / *)
#   produced by two numbers using the result of the calculation.
# To do this, enter 3 numbers (positive or negative integers).
# Examples:
# 4 6 10 - expect addition (+), 4+6=10.
# 4 3 1 - expect minus (-), 4-3=1
# 20 10 200 - expect multiplication (*), 20*10=200.
# 6 3 3 - expect division (/), 6/3=3
# 4 -6 10 - expect minus (-), 4+6=10.
# -4 3 -7 - expect minus (-), -4-3=-7
# 20 -10 -200 - expect multiplication (*), 20*(-10)=-200.
# -6 3 -3 - expect division (/), -6/3=-3
# -6 -3 -3 - expect minus (-), -6-(-3)=-3

import os
os.environ["KERAS_BACKEND"] = "torch"
import keras
import numpy as np

print('Data generation and training preparation...')

number_low = 1
number_high = 10 # not including, i.e. up to 9
signs = ['+', '*', '-', '/'] # link to calc:ops
reward = 1.0

hidden = 3
units = 8**2
epochs = 2
learning_rate = 0.01
batch_size = 15**2
train_sets = 2_000_000


def build_model():
  model = keras.Sequential()

  for _ in range(hidden):
    model.add(keras.layers.Dense(
      units=units,
      activation=keras.activations.relu,
    ))

  model.add(keras.layers.Dense(
    units=len(signs),
    activation=keras.activations.softmax,
  ))

  model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
    loss=keras.losses.Huber(),
    metrics=[
      keras.metrics.MeanSquaredError(),
    ],
  )

  return model


model = build_model()


def get_random_number():
  number = np.random.randint(number_low, number_high)
  sign = np.random.choice([-1, 1])
  return number * sign


def get_sign():
  return signs[np.random.randint(0, len(signs))]


def calc(sign, x, y):
  ops = {
    signs[0]: x + y,
    signs[1]: x * y,
    signs[2]: x - y,
    signs[3]: x / y,
  }
  return ops[sign]


def get_rewards(sign):
  rewards = []
  for _ in signs:
    rewards.append(0.0)
  idx = signs.index(sign)
  rewards[idx] = reward
  return rewards


def gen_train_sets():
  inputs = []
  labels = []
  for _ in range(train_sets):
    input_a = get_random_number()
    input_b = get_random_number()
    sign = get_sign()
    result = calc(sign, input_a, input_b)

    inputs.append([
      input_a,
      input_b,
      result,
    ])

    labels.append(
      get_rewards(sign),
    )
  return (
    keras.ops.array(inputs),
    keras.ops.array(labels),
  )


inputs, labels = gen_train_sets()
history = model.fit(
  x=inputs,
  y=labels,
  batch_size=batch_size,
  epochs=epochs,
  # 0 = silent, 1 = progress bar, 2 = one line per epoch
  verbose=1,
)

model.summary()

data = [
  {
    'sign': '+',
    'x': 3,
    'y': 2,
    'result': 5,
  },
  {
    'sign': '-',
    'x': 8,
    'y': 5,
    'result': 3,
  },
  {
    'sign': '*',
    'x': 2,
    'y': 3,
    'result': 6,
  },
  {
    'sign': '/',
    'x': 8,
    'y': 4,
    'result': 2,
  },
  {
    'sign': '+',
    'x': -3,
    'y': 2,
    'result': -1,
  },
  {
    'sign': '-',
    'x': 8,
    'y': -5,
    'result': 13,
  },
  {
    'sign': '-',
    'x': -8,
    'y': -5,
    'result': -3,
  },
  {
    'sign': '*',
    'x': -2,
    'y': 3,
    'result': -6,
  },
  {
    'sign': '/',
    'x': 8,
    'y': -4,
    'result': -2,
  },
  # Below is the data that ML could not see - the training sets are limited to the number 9 for x,y.
  {
    'sign': '+',
    'x': 12,
    'y': 14,
    'result': 26,
  },
  {
    'sign': '*',
    'x': 14,
    'y': 16,
    'result': 224,
  },
  {
    'sign': '-',
    'x': 30,
    'y': 15,
    'result': 15,
  },
  {
    'sign': '/',
    'x': 60,
    'y': 30,
    'result': 2,
  },
  {
    'sign': '+',
    'x': 1267,
    'y': 8589,
    'result': 9856,
  },
  {
    'sign': '*',
    'x': 1267,
    'y': 8314,
    'result': 10_533_838,
  },
  {
    'sign': '+',
    'x': 12,
    'y': -14,
    'result': -2,
  },
  {
    'sign': '*',
    'x': -14,
    'y': 16,
    'result': -224,
  },
  {
    'sign': '-',
    'x': -30,
    'y': 15,
    'result': -45,
  },
  {
    'sign': '/',
    'x': -60,
    'y': 30,
    'result': -2,
  },
  {
    'sign': '+',
    'x': -1267,
    'y': 8589,
    'result': 7322,
  },
  {
    'sign': '*',
    'x': 1267,
    'y': -8314,
    'result': -10_533_838,
  },
]

def predict(val):
  x_test = keras.ops.array([[
    val['x'],
    val['y'],
    val['result'],
  ]])
  predictions = model.predict(x=x_test)
  sign = signs[predictions.argmax()]

  print('expect:', val['sign'], 'predict:', sign, '#', val['x'], sign, val['y'], '=', val['result'])


for val in data:
  predict(val)


while True:
  print('enter via enter...')
  x = int(input('Enter a positive or negative integer: '))
  y = int(input('Enter a positive or negative integer: '))
  result = int(input('Enter result operation: '))

  predict({
    'sign': '?',
    'x': x,
    'y': y,
    'result': result,
  })
