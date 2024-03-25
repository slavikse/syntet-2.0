from nn.gym_v1 import NeuralNetwork


class MountainCar(NeuralNetwork):
  def __init__(self, **kwargs):
    super(MountainCar, self).__init__(**kwargs)


# TODO Not completed!

MountainCar(
  env_name='MountainCar-v0',
  episode_length=200,
  units_output=3,

  layers_hidden=6,
  units_hidden=600,
  learning_rate=1e-5,

  reward_normal=0.5,
  reward_penalty=0,

  researchers=0.4,
  exploitation=False,
)
