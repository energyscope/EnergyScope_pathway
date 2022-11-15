import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    # state = []
    # action = []
    # First environment using the monthly version of esmy
    id='esmymo-v0',
    entry_point='gym_esmy.envs:EsmyMoV0',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v1',
    entry_point='gym_esmy.envs:EsmyMoV1',
    max_episode_steps = 50,
)


register(
    # state = []
    # action = []
    # First environment using the TD version of esmy
    id='esmytd-v0',
    entry_point='gym_esmy.envs:EsmyTdV0',
    max_episode_steps = 50,
)