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
    # First environment using the monthly version of esmy
    id='esmymo-v01',
    entry_point='gym_esmy.envs:EsmyMoV01',
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
    # Second environment using the monthly version of esmy
    id='esmymo-v2',
    entry_point='gym_esmy.envs:EsmyMoV2',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v21',
    entry_point='gym_esmy.envs:EsmyMoV21',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v3',
    entry_point='gym_esmy.envs:EsmyMoV3',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v31',
    entry_point='gym_esmy.envs:EsmyMoV31',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v32',
    entry_point='gym_esmy.envs:EsmyMoV32',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v4',
    entry_point='gym_esmy.envs:EsmyMoV4',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v41',
    entry_point='gym_esmy.envs:EsmyMoV41',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v5',
    entry_point='gym_esmy.envs:EsmyMoV5',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # Second environment using the monthly version of esmy
    id='esmymo-v6',
    entry_point='gym_esmy.envs:EsmyMoV6',
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