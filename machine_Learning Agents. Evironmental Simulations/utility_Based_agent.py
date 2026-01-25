import random
import math
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

class Action(Enum):
    """Possible actions the agent can take"""
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    PICKUP = "pickup"
    DROP = "drop"
    USE = "use"
    WAIT = "wait"

@dataclass
class WorldState:
    """Represents the current state of the world"""
    agent_position: Tuple[int, int]
    items_at_position: List[str]
    agent_inventory: List[str]
    world_map: List[List[str]]
    time: int
    energy: float
    score: int

class UtilityBasedAgent:
    """A utility-based agent that chooses actions based on maximizing expected utility"""
    
    def __init__(self, 
                 name: str = "UtilityAgent",
                 energy_decay_rate: float = 0.1,
                 discount_factor: float = 0.9):
        """
        Initialize the utility-based agent
        
        Args:
            name: Name of the agent
            energy_decay_rate: Rate at which energy decays per action
            discount_factor: Discount factor for future utility
        """
        self.name = name
        self.energy_decay_rate = energy_decay_rate
        self.discount_factor = discount_factor
        self.utility_weights = {
            'energy': 1.0,
            'score': 2.0,
            'inventory_value': 1.5,
            'item_proximity': 0.8,
            'safety': 1.2
        }
        
    def calculate_utility(self, state: WorldState, action: Action) -> float:
        """
        Calculate the expected utility of taking an action in a given state
        
        Args:
            state: Current world state
            action: Action being considered
            
        Returns:
            Total utility value
        """
        # Get predicted next state
        predicted_state = self.predict_next_state(state, action)
        
        # Calculate various utility components
        energy_utility = self._energy_utility(predicted_state)
        score_utility = self._score_utility(predicted_state)
        inventory_utility = self._inventory_utility(predicted_state)
        proximity_utility = self._proximity_utility(predicted_state)
        safety_utility = self._safety_utility(predicted_state)
        
        # Weight and combine utilities
        total_utility = (
            self.utility_weights['energy'] * energy_utility +
            self.utility_weights['score'] * score_utility +
            self.utility_weights['inventory_value'] * inventory_utility +
            self.utility_weights['item_proximity'] * proximity_utility +
            self.utility_weights['safety'] * safety_utility
        )
        
        return total_utility
    
    def _energy_utility(self, state: WorldState) -> float:
        """Calculate utility based on energy level"""
        # Normalized energy utility (0 to 1)
        return state.energy / 100.0
    
    def _score_utility(self, state: WorldState) -> float:
        """Calculate utility based on score"""
        # Score increases utility logarithmically
        return math.log1p(state.score) / 10.0
    
    def _inventory_utility(self, state: WorldState) -> float:
        """Calculate utility based on inventory value"""
        # Assign values to different items
        item_values = {
            'gold': 10.0,
            'food': 5.0,
            'tool': 8.0,
            'key': 6.0,
            'treasure': 15.0
        }
        
        total_value = sum(item_values.get(item, 1.0) for item in state.agent_inventory)
        return total_value / 50.0  # Normalize
    
    def _proximity_utility(self, state: WorldState) -> float:
        """Calculate utility based on proximity to valuable items"""
        max_distance = len(state.world_map) + len(state.world_map[0])
        
        # Find distances to valuable items
        valuable_items = ['gold', 'treasure', 'food']
        min_distance = max_distance
        
        for i, row in enumerate(state.world_map):
            for j, cell in enumerate(row):
                if any(item in cell for item in valuable_items):
                    distance = abs(i - state.agent_position[0]) + abs(j - state.agent_position[1])
                    min_distance = min(min_distance, distance)
        
        # Invert distance (closer is better)
        return 1.0 - (min_distance / max_distance)
    
    def _safety_utility(self, state: WorldState) -> float:
        """Calculate utility based on safety (avoid edges)"""
        map_height = len(state.world_map)
        map_width = len(state.world_map[0])
        
        # Calculate distance from edges
        dist_from_top = state.agent_position[0]
        dist_from_bottom = map_height - 1 - state.agent_position[0]
        dist_from_left = state.agent_position[1]
        dist_from_right = map_width - 1 - state.agent_position[1]
        
        # Minimum distance to any edge
        min_edge_dist = min(dist_from_top, dist_from_bottom, dist_from_left, dist_from_right)
        
        return min_edge_dist / max(map_height, map_width)
    
    def predict_next_state(self, state: WorldState, action: Action) -> WorldState:
        """
        Predict the next state given current state and action
        
        Args:
            state: Current world state
            action: Action to take
            
        Returns:
            Predicted next state
        """
        # Create a copy of the current state
        next_state = WorldState(
            agent_position=state.agent_position,
            items_at_position=state.items_at_position.copy(),
            agent_inventory=state.agent_inventory.copy(),
            world_map=[row.copy() for row in state.world_map],
            time=state.time + 1,
            energy=state.energy - self.energy_decay_rate,
            score=state.score
        )
        
        # Apply the action
        x, y = next_state.agent_position
        
        if action == Action.MOVE_UP and x > 0:
            next_state.agent_position = (x - 1, y)
        elif action == Action.MOVE_DOWN and x < len(next_state.world_map) - 1:
            next_state.agent_position = (x + 1, y)
        elif action == Action.MOVE_LEFT and y > 0:
            next_state.agent_position = (x, y - 1)
        elif action == Action.MOVE_RIGHT and y < len(next_state.world_map[0]) - 1:
            next_state.agent_position = (x, y + 1)
        elif action == Action.PICKUP and next_state.items_at_position:
            # Pick up all items at current position
            next_state.agent_inventory.extend(next_state.items_at_position)
            next_state.items_at_position.clear()
        elif action == Action.DROP and next_state.agent_inventory:
            # Drop first item in inventory
            if next_state.agent_inventory:
                item = next_state.agent_inventory.pop(0)
                next_state.items_at_position.append(item)
        
        # Update score based on actions
        if action in [Action.PICKUP, Action.USE]:
            next_state.score += 10
        
        return next_state
    
    def choose_action(self, state: WorldState, available_actions: List[Action]) -> Action:
        """
        Choose the best action based on utility calculation
        
        Args:
            state: Current world state
            available_actions: List of possible actions
            
        Returns:
            Chosen action
        """
        if not available_actions:
            return Action.WAIT
        
        # Calculate utilities for all available actions
        action_utilities = []
        for action in available_actions:
            utility = self.calculate_utility(state, action)
            action_utilities.append((action, utility))
        
        # Choose action with highest utility
        best_action = max(action_utilities, key=lambda x: x[1])[0]
        
        # Add some exploration (epsilon-greedy)
        if random.random() < 0.1:  # 10% chance to explore
            best_action = random.choice(available_actions)
        
        return best_action
    
    def update_weights(self, reward: float, state: WorldState, action: Action):
        """
        Update utility weights based on received reward
        
        Args:
            reward: Reward received
            state: State where action was taken
            action: Action that was taken
        """
        # Simple weight update: increase weights for components that contributed to positive reward
        predicted_utility = self.calculate_utility(state, action)
        
        if reward > 0:
            # Slightly increase all weights proportionally
            scale_factor = 1 + (reward / 100.0)
            for key in self.utility_weights:
                self.utility_weights[key] *= scale_factor
        else:
            # Decrease weights slightly for negative reward
            scale_factor = 1 + (reward / 200.0)  # Less aggressive decrease
            for key in self.utility_weights:
                self.utility_weights[key] = max(0.1, self.utility_weights[key] * scale_factor)

class Environment:
    """Simple grid world environment for the agent"""
    
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self.grid = [['.' for _ in range(width)] for _ in range(height)]
        self.items = {
            'gold': [(2, 3), (7, 8)],
            'food': [(1, 1), (5, 5), (8, 2)],
            'treasure': [(9, 9)]
        }
        self._initialize_grid()
    
    def _initialize_grid(self):
        """Place items on the grid"""
        for item_type, positions in self.items.items():
            for x, y in positions:
                self.grid[x][y] = item_type[0]  # First letter
    
    def get_state(self, agent_pos: Tuple[int, int], inventory: List[str], 
                  energy: float, score: int, time: int) -> WorldState:
        """Get current world state"""
        items_here = []
        x, y = agent_pos
        cell = self.grid[x][y]
        
        # Check what item is at current position
        if cell == 'g':
            items_here = ['gold']
        elif cell == 'f':
            items_here = ['food']
        elif cell == 't':
            items_here = ['treasure']
        
        return WorldState(
            agent_position=agent_pos,
            items_at_position=items_here,
            agent_inventory=inventory.copy(),
            world_map=self.grid.copy(),
            time=time,
            energy=energy,
            score=score
        )
    
    def execute_action(self, agent_pos: Tuple[int, int], action: Action, 
                       inventory: List[str]) -> Tuple[Tuple[int, int], List[str], float]:
        """
        Execute an action and return new position, inventory, and reward
        
        Returns:
            Tuple of (new_position, new_inventory, reward)
        """
        x, y = agent_pos
        new_pos = agent_pos
        new_inventory = inventory.copy()
        reward = 0.0
        
        if action == Action.MOVE_UP and x > 0:
            new_pos = (x - 1, y)
        elif action == Action.MOVE_DOWN and x < self.height - 1:
            new_pos = (x + 1, y)
        elif action == Action.MOVE_LEFT and y > 0:
            new_pos = (x, y - 1)
        elif action == Action.MOVE_RIGHT and y < self.width - 1:
            new_pos = (x, y + 1)
        elif action == Action.PICKUP:
            cell = self.grid[x][y]
            if cell != '.':
                # Add to inventory and remove from grid
                if cell == 'g':
                    new_inventory.append('gold')
                    reward = 20.0
                elif cell == 'f':
                    new_inventory.append('food')
                    reward = 10.0
                elif cell == 't':
                    new_inventory.append('treasure')
                    reward = 50.0
                self.grid[x][y] = '.'  # Remove item from grid
        
        # Small penalty for moving (energy cost)
        if action in [Action.MOVE_UP, Action.MOVE_DOWN, Action.MOVE_LEFT, Action.MOVE_RIGHT]:
            reward -= 1.0
        
        return new_pos, new_inventory, reward

# Example usage and simulation
def simulate_agent(episodes: int = 5, steps_per_episode: int = 100):
    """Run a simulation of the utility-based agent"""
    
    env = Environment(width=10, height=10)
    agent = UtilityBasedAgent(name="Explorer", energy_decay_rate=0.2)
    
    available_actions = [action for action in Action]
    
    for episode in range(episodes):
        print(f"\n=== Episode {episode + 1} ===")
        
        # Reset agent state
        agent_pos = (0, 0)
        inventory = []
        energy = 100.0
        score = 0
        total_reward = 0
        
        for step in range(steps_per_episode):
            if energy <= 0:
                print(f"Agent ran out of energy at step {step}")
                break
            
            # Get current state
            state = env.get_state(agent_pos, inventory, energy, score, step)
            
            # Choose action
            action = agent.choose_action(state, available_actions)
            
            # Execute action in environment
            new_pos, new_inventory, reward = env.execute_action(agent_pos, action, inventory)
            
            # Update agent state
            agent_pos = new_pos
            inventory = new_inventory
            energy -= agent.energy_decay_rate
            score += max(0, int(reward))
            total_reward += reward
            
            # Update agent's utility weights based on reward
            agent.update_weights(reward, state, action)
            
            # Print progress
            if step % 20 == 0:
                print(f"Step {step}: Pos={agent_pos}, Energy={energy:.1f}, "
                      f"Score={score}, Inventory={inventory}")
        
        print(f"Episode {episode + 1} completed:")
        print(f"  Final Score: {score}")
        print(f"  Total Reward: {total_reward:.2f}")
        print(f"  Final Inventory: {inventory}")
        print(f"  Utility Weights: {agent.utility_weights}")

if __name__ == "__main__":
    # Run simulation
    simulate_agent(episodes=3, steps_per_episode=50)
    
    # Alternatively, create and test agent directly
    print("\n" + "="*50)
    print("Direct Agent Testing")
    print("="*50)
    
    # Create a test environment
    test_env = Environment(width=5, height=5)
    test_agent = UtilityBasedAgent()
    
    # Test state
    test_state = test_env.get_state(
        agent_pos=(2, 2),
        inventory=['gold'],
        energy=80.0,
        score=50,
        time=0
    )
    
    # Test utility calculation for different actions
    test_actions = [Action.MOVE_UP, Action.MOVE_DOWN, Action.PICKUP, Action.WAIT]
    
    for action in test_actions:
        utility = test_agent.calculate_utility(test_state, action)
        print(f"Utility of {action.value}: {utility:.2f}")