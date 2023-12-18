import os
os.environ["KERAS_BACKEND"] = "torch"
import keras
import numpy as np
import matplotlib.pyplot as plt

# Добавить промпт
# название: обратный калькулятор - обучение с учителем
# запушить этот файл в гитхаб

number_low = 1
number_high = 10 # не включая, т.е. до 9
normalizer = number_high
signs = ['+', '*', '-', '/']

learning_rate = 0.01
batch_size = 32 # default: 32
train_sets = 1_000_000
epochs = 1
passages = 1
reward = 1.0

model = keras.Sequential()

model.add(keras.layers.Dense(
  units=10**2,
  activation=keras.activations.relu,
))

model.add(keras.layers.Dense(
  units=10**2,
  activation=keras.activations.relu,
))

model.add(keras.layers.Dense(
  units=len(signs),
  activation=keras.activations.softmax,
))

model.compile(
  optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
  loss=keras.losses.MeanSquaredError(),
  metrics=[
    keras.metrics.MeanSquaredError(),
  ],
)

def get_number(min=number_low, max=number_high):
  return np.random.randint(min, max)

def get_sign():
  return signs[get_number(0, len(signs))]


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
    input_a = get_number()
    input_b = get_number()
    sign = get_sign()
    result = calc(sign, input_a, input_b)

    inputs.append([
      input_a / normalizer,
      input_b / normalizer,
      result / (normalizer ** 2),
    ])

    labels.append(
      get_rewards(sign),
    )
  return (
    keras.ops.array(inputs),
    keras.ops.array(labels),
  )


for _ in range(passages):
  inputs, labels = gen_train_sets()
  history = model.fit(
    inputs,
    labels,
    batch_size=batch_size,
    epochs=epochs,
    callbacks=[
      # keras.callbacks.EarlyStopping(baseline=0.01)
    ],
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
  # Ниже данные, которые ML не могла видеть - обучающие наборы ограничены для x,y числом 9.
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
]

for val in data:
  x_test = keras.ops.array([[
    val['x'] / normalizer,
    val['y'] / normalizer,
    val['result'] / (normalizer ** 2),
  ]])
  predictions = model.predict(x_test)
  sign = signs[predictions.argmax()]
  print('expect:', val['sign'], 'predict:', sign, '#', val['x'], sign, val['y'], '=', val['result'])


def show_plot():
  plt.plot(history.history['loss'], label='MAE (training data)')
  plt.title('MAE for Chennai Reservoir Levels')
  plt.ylabel('MAE value')
  plt.xlabel('No. epoch')
  plt.legend(loc="upper left")
  plt.show()

show_plot()
