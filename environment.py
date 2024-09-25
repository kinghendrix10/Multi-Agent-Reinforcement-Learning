# /environment.py
import gym
from gym import spaces
import numpy as np

class MultiAgentEnv(gym.Env):
    def __init__(self, config):
        super(MultiAgentEnv, self).__init__()
        self.num_agents = config['num_agents']
        self.max_steps = config['max_steps']
        self.current_step = 0
        
        # Action space: discrete actions for each agent
        self.action_space = spaces.Discrete(5)
        
        # Observation space: continuous state for each agent
        self.observation_space = spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)
        
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
        # Implement reward calculation based on actions and task progress
        return [self._individual_reward(i, action) for i, action in enumerate(actions)]

    def _individual_reward(self, agent_id, action):
        # Implement individual reward calculation
        return np.random.random()  # Placeholder

    def _generate_task(self):
        # Generate a random task for the agents
        return f"Task {np.random.randint(1000)}"

class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.state = np.random.rand(10)

    def apply_action(self, action):
        # Update agent state based on action
        self.state = np.clip(self.state + np.random.normal(0, 0.1, 10), 0, 1)

    def get_observation(self):
        return self.state
