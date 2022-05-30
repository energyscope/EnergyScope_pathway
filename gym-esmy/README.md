Gym is now being maintained, but new major features are not intended. See [this post](https://github.com/openai/gym/issues/2259) for more information.

## Gym-esmy

The aim of this code is to implement an reinforcement-learning-based agent interacting with EnergyScopeMyopic environment to end up with a robust policy to drive the energy transition of a whole-energy system.


## Installation

To install the base Gym library, use `pip install gym`.

This does not include dependencies for all families of environments (there's a massive number, and some can be problematic to install on certain systems). You can install these dependencies for one family like `pip install gym[atari]` or use `pip install gym[all]` to install all dependencies.

We support Python 3.6, 3.7, 3.8 and 3.9 on Linux and macOS. We will accept PRs related to Windows, but do not officially support it.