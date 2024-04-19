# Brett Palmer mince@foldingcircles.co.uk
# Deep Learn [try]

# from game import get_score
__version__ = "0.0.0002"
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


class WearableBrain(nn.Module):
    def __init__(self, num_sensors, num_actions, Load_Model=False, Model_Directory='', Model_file_ext='.pth',
                 Find=False, default_model='model.pth'):
        super(WearableBrain, self).__init__()

        # Assuming num_sensors might include both scalar and time-series sensors
        self.rnn = nn.LSTM(num_sensors, 128, batch_first=True)  # Handles sequential data
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, stride=1, padding=1)  # Additional conv layer for any spatial patterns in sensor data
        self.fc1 = nn.Linear(128 + 32, 64)  # Combine features from LSTM and Conv1d
        self.output_layer = nn.Linear(64, num_actions)

        self.optimizer = optim.Adam(self.parameters(), lr=0.0113211)
        self.action_mappings = torch.eye(num_actions)
        self.load_a_model = Load_Model
        self.model_file = default_model if Load_Model else 'model.pth'
        if Load_Model:
            model_path = self.find_latest_model(Model_Directory, Model_file_ext) if Find else os.path.join(
                Model_Directory, 'model' + Model_file_ext)
            self.load_model(model_path)

    def forward(self, x_scalar, x_sequence):
        if x_scalar is not None:
            x_scalar = x_scalar.unsqueeze(1)  # Adding a channel dimension
            conv_features = torch.relu(self.conv1(x_scalar))
            conv_features = torch.flatten(conv_features, start_dim=1)
        else:
            conv_features = torch.zeros(0)  # Handle the no scalar input case

        if x_sequence is not None:
            _, (h_n, _) = self.rnn(x_sequence)
            lstm_features = h_n[-1]  # Take the last hidden state
        else:
            lstm_features = torch.zeros(0)  # Handle the no sequence input case

        # Combine features from both LSTM and Conv1d
        if x_scalar is not None and x_sequence is not None:
            combined_features = torch.cat((lstm_features, conv_features), dim=1)
        elif x_scalar is not None:
            combined_features = conv_features
        elif x_sequence is not None:
            combined_features = lstm_features
        else:
            raise ValueError("At least one of 'x_scalar' or 'x_sequence' must be provided")

        # Fully connected layers
        x = torch.relu(self.fc1(combined_features))
        x = self.output_layer(x)
        return x

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

    def decide_action(self, state=None, sequence=None):
        self.eval()  # Set the network to evaluation mode

        # Prepare tensors conditionally based on the availability of input data
        if state is not None:
            state_tensor = torch.tensor(state, dtype=torch.float).unsqueeze(0)  # Assuming state is a single sample
            if self.use_cuda:
                state_tensor = state_tensor.cuda()
        if sequence is not None:
            sequence_tensor = torch.tensor(sequence, dtype=torch.float).unsqueeze(
                0)  # Assuming sequence is a single sample
            if self.use_cuda:
                sequence_tensor = sequence_tensor.cuda()

        # Execute the forward pass depending on what inputs are available
        with torch.no_grad():  # No need to track gradients here
            if state is not None and sequence is not None:
                action_outputs = self.forward(state_tensor, sequence_tensor)
            elif state is not None:
                action_outputs = self.forward(state_tensor, None)  # Modify the forward method to handle None inputs
            elif sequence is not None:
                action_outputs = self.forward(None, sequence_tensor)
            else:
                raise ValueError("At least one of 'state' or 'sequence' must be provided")

        # Decide on action based on the network's output
        action_index = torch.argmax(action_outputs, dim=1).item()
        action = self.action_mappings[action_index]

        # Optionally return action probabilities for further analysis or logging
        action_probabilities = torch.nn.functional.softmax(action_outputs, dim=1).numpy()
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




class ConvBrain(nn.Module):
    def __init__(self, input_channels, num_actions, Load_Model=False, Model_Directory='', Model_file_ext='.pth',
                 Find=False, default_model='model.pth'):
        super(ConvBrain, self).__init__()

        # Example of adding convolutional layers
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)

        # Assuming the input size and the pooling layers, calculate the size here
        self.flattened_size = self.calculate_flattened_size()

        self.fc1 = nn.Linear(self.flattened_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.output_layer = nn.Linear(64, num_actions)

        self.optimizer = optim.Adam(self.parameters(), lr=0.0113211)
        self.action_mappings = torch.eye(num_actions)
        self.load_a_model = Load_Model
        self.model_file = default_model if Load_Model else 'model.pth'
        if Load_Model:
            model_path = self.find_latest_model(Model_Directory, Model_file_ext) if Find else os.path.join(
                Model_Directory, 'model' + Model_file_ext)
            self.load_model(model_path)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = x.view(-1, self.flattened_size)  # Flatten the output of the conv layers
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.output_layer(x)
        return x

    def calculate_flattened_size(self, input_channels=None, image_height=None, image_width=None):
        # Dummy input to calculate flattened size
        dummy_input = torch.zeros(1, input_channels, image_height, image_width)
        x = self.conv1(dummy_input)
        x = self.conv2(x)
        return x.numel()

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
        
