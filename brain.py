# PRIVATE AND CONFIDENTIAL [Intellectual Property Of Brett Palmer mince@foldingcircles.co.uk]
# [No Copying Or Reading Or Use Permitted !]
"""
Copyright (c) 2023, Brett Palmer (Mince@foldingcircles.co.uk)

All rights reserved. No permission is granted for anyone, except the software owner, Brett Palmer, to use, copy, modify,
distribute, sublicense, or otherwise deal with the software in any manner.

Any unauthorized use, copying, or distribution of this software without the explicit written consent of the software
owner is strictly prohibited.

For permission requests, please contact the software owner, Brett Palmer, at Mince@foldingcircles.co.uk.
"""

# FoldingCircles Making The Unknown Known

# Deep Learn [try]
__version__ = "0.0.0001"

from game import get_score

print(f'brain.py {__version__}')

# brain.py


import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import glob



class Brain(nn.Module):
    def __init__(self, num_sensors, num_actions, Load_Model=False, Model_Directory='', Model_file_ext='.pth',
                 Find=False, default_model='model.pth'):

        super(Brain, self).__init__()
        self.layer1 = nn.Linear(num_sensors, 128)
        self.layer2 = nn.Linear(128, 64)
        self.output_layer = nn.Linear(64, num_actions)
        self.optimizer = optim.Adam(self.parameters(), lr=0.0113211)

        # One-hot encoding of actions
        # self.action_mappings = np.identity(num_actions, dtype=np.uint8) # be more conventional
        self.action_mappings = torch.eye(num_actions)

        self.load_a_model = Load_Model
        self.model_file = default_model if Load_Model else 'model.pth'

        if Load_Model:
            model_path = self.find_latest_model(Model_Directory, Model_file_ext) if Find else os.path.join(
                Model_Directory, 'model' + Model_file_ext)
            self.load_model(model_path)

    def forward(self, sensor_inputs):
        x = torch.relu(self.layer1(sensor_inputs))
        x = torch.relu(self.layer2(x))
        action_outputs = self.output_layer(x)
        return action_outputs

    def find_latest_model(self, directory, file_ext):
        list_of_files = glob.glob(os.path.join(directory, '*' + file_ext))  # Include directory in search
        if not list_of_files:  # If no files are found, raise an exception
            raise FileNotFoundError(f"No model file found in directory {directory} with extension {file_ext}")
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def load_model(self, filepath):
        if os.path.isfile(filepath):
            print(f'Loading model from {filepath}')
            self.load_state_dict(torch.load(filepath))
            self.eval()  # Set the model to evaluation mode after loading
            self.model_file = filepath
        else:
            raise FileNotFoundError(f"Model file not found at {filepath}")

    def decide_action(self, state):
        self.eval()  # Set the network to evaluation mode
        state_tensor = torch.tensor(state, dtype=torch.float)
        with torch.no_grad():  # No need to track gradients here
            action_outputs = self.forward(state_tensor)

        # simple action to .eye matrix type
        # action = self.action_mappings[torch.argmax(action_outputs).item()]  # readability
        action_index = torch.argmax(action_outputs).item()
        action = self.action_mappings[action_index]

        # For a full action decision matrix, you could use softmax to get probabilities
        action_probabilities = torch.nn.functional.softmax(action_outputs, dim=0).numpy()
        return action_index, action, action_probabilities

    def learn(self, state, action, reward, done, current_score, score_target=0.9):
        self.train()
        state_tensor = torch.tensor(state, dtype=torch.float)
        action_tensor = torch.tensor(action, dtype=torch.long)
        reward_tensor = torch.tensor(reward, dtype=torch.float)

        # Adjust reward based on how close the score is to the target
        score_distance = score_target - current_score
        adjusted_reward = reward + (score_target - score_distance) / score_target

        # Forward pass
        pred = self.forward(state_tensor)[action_tensor]

        gamma = 0.999
        next_Q = torch.max(self.forward(state_tensor))

        # Calculate the target Q-value
        target_Q = adjusted_reward + (gamma * next_Q).detach()  # detach to prevent gradients from being calculated

        # Calculate loss
        target = adjusted_reward
        if not done:
            target = target_Q

        loss = F.mse_loss(pred, target)

        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def action_learn(self, state, action, reward, done, current_score, score_target=None):
        self.train()
        state_tensor = torch.tensor(state, dtype=torch.float)
        action_tensor = torch.tensor(action, dtype=torch.long)
        reward_tensor = torch.tensor(reward, dtype=torch.float)

        # Adjust reward based on how close the score is to the target
        score_distance = score_target - current_score
        adjusted_reward = reward + (score_target - score_distance) / score_target

        # Forward pass
        pred = self.forward(state_tensor)[action_tensor]

        gamma = 0.999

        next_Q = torch.max(self.forward(state_tensor))

        # Calculate the target Q-value
        target_Q = adjusted_reward + (gamma * next_Q).detach()  # detach to prevent gradients from being calculated

        # Calculate loss
        target = reward_tensor
        if not done:
            # If the game is not over, use expected future reward to update the target
            target = target_Q
            # print(f'Target:{target}  pred:{pred}')

        loss = F.mse_loss(pred, target)

        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def get_weights(self, layer_name='layer1'):
        # Return the weight matrix of the specified layer
        # Here, accessing the weights of layer1 as an example
        layer = getattr(self, layer_name, None)
        if layer is not None:
            return layer.weight.data.cpu().numpy()  # Assuming you want to work with NumPy arrays
        else:
            print(f"Layer {layer_name} not found in the model.")
            return None

    def save_model(self, filepath='model.pth'):
        if self.load_a_model:
            filepath = self.model_file
        print(f'Saving Model. [ {filepath} ]')
        torch.save(self.state_dict(), filepath)
