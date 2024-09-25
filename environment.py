# /environment.py
import gym
from gym import spaces
import numpy as np
from ray.rllib.algorithms.ppo import PPO
from ray.tune.registry import register_env

class MultiAgentEnv(gym.Env):
    def __init__(self, config):
        super(MultiAgentEnv, self).__init__()
        self.num_agents = config['num_agents']
        self.max_steps = config['max_steps']
        self.current_step = 0
        
        # Action space: discrete actions for each agent
        self.action_space = spaces.Discrete(5)
        
        # Observation space: continuous state for each agent
        self.observation_space = spaces.Box(low=0, high=1, shape=(15,), dtype=np.float32)
        
        self.agents = [Agent(i) for i in range(self.num_agents)]
        self.task = None

    def reset(self):
        self.current_step = 0
        self.task = self._generate_task()
        return self._get_observations()

    def step(self, actions):
        self.current_step += 1
        
        # Apply actions and update agent states
        for i, action in enumerate(actions):
            self.agents[i].apply_action(action)
        
        # Calculate rewards
        rewards = self._calculate_rewards(actions)
        
        # Check if episode is done
        done = self.current_step >= self.max_steps
        
        return self._get_observations(), rewards, done, {}

    def _get_observations(self):
        return [agent.get_observation() for agent in self.agents]

    def _calculate_rewards(self, actions):
        task_progress = self._evaluate_task_progress()
        return [self._individual_reward(i, action, task_progress) for i, action in enumerate(actions)]

    def _individual_reward(self, agent_id, action, task_progress):
        action_effectiveness = self._evaluate_action_effectiveness(agent_id, action)
        return task_progress + action_effectiveness

    def _evaluate_task_progress(self):
        return np.random.random()  # Placeholder for task progress evaluation

    def _evaluate_action_effectiveness(self, agent_id, action):
        return np.random.random()  # Placeholder for action effectiveness evaluation

    def _generate_task(self):
        return f"Task {np.random.randint(1000)}"

class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.state = np.random.rand(15)

    def apply_action(self, action):
        self.state = np.clip(self.state + np.random.normal(0, 0.1, 15), 0, 1)

    def get_observation(self):
        return self.state

# Register the environment
register_env("multi_agent_env", lambda config: MultiAgentEnv(config))