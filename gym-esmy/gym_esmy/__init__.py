import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='ESMY-v0',
    entry_point='gym_esmy.envs:ESMYInitV0',
    max_episode_steps = 50,
)