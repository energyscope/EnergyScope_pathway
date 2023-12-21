import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    # state = []
    # action = []
    # 0th environment using the monthly version of esmy
    id='esmymo-v0',
    entry_point='gym_esmy.envs:EsmyMoV0',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 0.1th environment using the monthly version of esmy
    id='esmymo-v01',
    entry_point='gym_esmy.envs:EsmyMoV01',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 1st environment using the monthly version of esmy
    id='esmymo-v1',
    entry_point='gym_esmy.envs:EsmyMoV1',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 2nd environment using the monthly version of esmy
    id='esmymo-v2',
    entry_point='gym_esmy.envs:EsmyMoV2',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 2.1nd environment using the monthly version of esmy
    id='esmymo-v21',
    entry_point='gym_esmy.envs:EsmyMoV21',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 3rd environment using the monthly version of esmy
    id='esmymo-v3',
    entry_point='gym_esmy.envs:EsmyMoV3',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 3.1rd environment using the monthly version of esmy
    id='esmymo-v31',
    entry_point='gym_esmy.envs:EsmyMoV31',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 3.2rd environment using the monthly version of esmy
    id='esmymo-v32',
    entry_point='gym_esmy.envs:EsmyMoV32',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 4th environment using the monthly version of esmy
    id='esmymo-v4',
    entry_point='gym_esmy.envs:EsmyMoV4',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 4.1th environment using the monthly version of esmy
    id='esmymo-v41',
    entry_point='gym_esmy.envs:EsmyMoV41',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 5th environment using the monthly version of esmy
    id='esmymo-v5',
    entry_point='gym_esmy.envs:EsmyMoV5',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 6th environment using the monthly version of esmy
    id='esmymo-v6',
    entry_point='gym_esmy.envs:EsmyMoV6',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 7th environment using the monthly version of esmy
    id='esmymo-v7',
    entry_point='gym_esmy.envs:EsmyMoV7',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    # 8th environment using the monthly version of esmy
    id='esmymo-v8',
    entry_point='gym_esmy.envs:EsmyMoV8',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    id='esmy-v8',
    entry_point='gym_esmy.envs:EsmyV8',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    id='esmy-v9',
    entry_point='gym_esmy.envs:EsmyV9',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    id='esmy-v10',
    entry_point='gym_esmy.envs:EsmyV10',
    max_episode_steps = 50,
)

register(
    # state = []
    # action = []
    id='esmy-v11',
    entry_point='gym_esmy.envs:EsmyV11',
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