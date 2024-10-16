# BDX related Readme

Follow the instructions of the main readme to install the necessary dependencies and run the code.

## To train bdx :

```bash
python3 legged_gym/scripts/train.py --task=bdx_amp --num_envs <X> --run_name <run_name>
```

(I use `num_envs = 8000` on a RTX4090 GPU)

## To evaluate bdx :

```bash
python3 legged_gym/scripts/play.py --task=bdx_amp --num_envs=8
```

This will play the latest checkpoint in the `logs/bdx_amp/<run_name>` folder.

(I use `num_envs = 8` to play locally on my laptop)

## Some critical parameters :

In `legged_gym/envs/bdx/bdx_amp_config.py`
- `dt` : has a significant effect on the stability of the simulation. I found `0.002` is good for this robot
- `decimation` : Controls the control frequency. With `dt = 0.002` and `decimation = 6`, the control frequency is `(1/0.002)/6 ~= 83Hz`
- `stiffness_all`, `damping_all` : Still trying to find the optimal values.
- `action_scale` : has a significant effect on training stability. Default is `0.25`
- `disc_grad_penalty` : I found it works best with `0.01`, but the original paper suggests `10`. There seems to be implementation differences between the original code and this one, such that the scale of this parameter is different.
- `amp_task_reward_lerp`: This parameter controls the balance between the task reward and the adversarial reward. Default is `0.3`
- `MOTION_FILES`: Paths to the reference motion files. They are generated using this script : https://github.com/apirrone/mini_BDX/blob/main/experiments/placo/placo_record_amp.py (TODO document this)

## Tuning the PD controller

The custom PD controller is in `legged_gym/envs/base/legged_robot.py:_compute_torques()`.

To tune it I fix the robot in space using `fix_base_link`, set it a little above the ground so that the feet don't touch the ground

```python
class init_state(...):
    pos = [0.0, 0.0, 0.3]  # x,y,z [m]
```

Set the `action_scale` to `1.0`.

Then replay the motion file through the PD controller in `legged_robot.py:step()`

```python
actions = torch.zeros(
    self.num_envs,
    self.num_actions,
    dtype=torch.float,
    device=self.device,
    requires_grad=False,
)

target_pos = self.amp_loader.get_joint_pose_batch(
    self.amp_loader.get_full_frame_at_time_batch(
        np.zeros(self.num_envs, dtype=np.int),
        self.envs_times.cpu().numpy().flatten(),
    )
)

target_pos[:] -= self.default_dof_pos

actions[:, :] = target_pos
```

I run play.py with a random checkpoint (does not matters since we override the policy actions) for a few seconds, then plot it using:

```bash
python3 plot_action_obs.py
```

## Parameters that "work" for walking forward


- `MOTION_FILES` = `["datasets/bdx/new_placo_moves/bdx_walk_forward_medium.txt"]`
```python
class commands:
    class ranges:
        lin_vel_x = [0.15, 0.15]
```
- `stiffness_all = 10`
- `damping_all = 0.01`
- `action_scale = 0.25`
- `decimation = 6`
- `dt = 0.002`
- `disc_grad_penalty = 0.01`
- `amp_task_reward_lerp = 0.1`


# Adversarial Motion Priors Make Good Substitutes for Complex Reward Functions #

Codebase for the "[Adversarial Motion Priors Make Good Substitutes for Complex Reward Functions](https://bit.ly/3hpvbD6)" project. This repository contains the code necessary to ground agent skills using small amounts of reference data (4.5 seconds). All experiments are performed using the A1 robot from Unitree. This repository is based off of Nikita Rudin's [legged_gym](https://github.com/leggedrobotics/legged_gym) repo, and enables us to train policies using [Isaac Gym](https://developer.nvidia.com/isaac-gym).

**Maintainer**: Alejandro Escontrela
**Affiliation**: University of California at Berkeley
**Contact**: escontrela@berkeley.edu

### Useful Links ###
Project website: https://bit.ly/3hpvbD6
Paper: https://drive.google.com/file/d/1kFm79nMmrc0ZIiH0XO8_HV-fj73agheO/view?usp=sharing

### Installation ###
1. Create a new python virtual env with python 3.6, 3.7 or 3.8 (3.8 recommended). i.e. with conda:
    - `conda create -n amp_hw python==3.8`
    - `conda activate amp_hw`
2. Install pytorch 1.10 with cuda-11.3:
    - `pip3 install lxml transformations setuptools==59.5.0 pyquaternion lxml transformations torch==1.10.0+cu113 torchvision==0.11.1+cu113 tensorboard==2.8.0 pybullet==3.2.1 opencv-python==4.5.5.64 torchaudio==0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html`
3. Install Isaac Gym
   - Download and install Isaac Gym Preview 3 (Preview 2 will not work!) from https://developer.nvidia.com/isaac-gym
   - `cd isaacgym/python && pip install -e .`
   - Try running an example `cd examples && python 1080_balls_of_solitude.py`
   - For troubleshooting check docs `isaacgym/docs/index.html`)
4. Install rsl_rl (PPO implementation)
   - Clone this repository
   -  `cd AMP_for_hardware/rsl_rl && pip install -e .`
5. Install legged_gym
   - `cd ../ && pip install -e .`

6. Lastly, build and install the interface to Unitree's SDK. The Unitree [repo](https://github.com/unitreerobotics/unitree_legged_sdk) has been releasing new SDK versions. For convenience, we have included the version that we used in `third_party/unitree_legged_sdk`.

   First, make sure the required packages are installed, following Unitree's [guide](https://github.com/unitreerobotics/unitree_legged_sdk). Most nostably, please make sure to install `Boost` and `LCM`:

   ```bash
   sudo apt install libboost-all-dev liblcm-dev
   ```

   Then, go to `third_party/unitree_legged_sdk` and create a build folder:
   ```bash
   cd third_party/unitree_legged_sdk
   mkdir build && cd build
   ```

   Now, build the libraries and move them to the main directory by running:
   ```bash
   cmake ..
   make
   mv robot_interface* ../../..
   ```

   And install the pygame library for joystick control:
   ```bash
   pip install attrs filterpy pygame gym
   ```

### Additional Setup for Real Robot
Follow these steps if you want to run policies on the real robot.

1. **Setup correct permissions for non-sudo user**

   Since the Unitree SDK requires memory locking and high process priority, root priority with `sudo` is usually required to execute commands. To run the SDK without `sudo`, write the following to `/etc/security/limits.d/90-unitree.conf`:

   ```bash
   <username> soft memlock unlimited
   <username> hard memlock unlimited
   <username> soft nice eip
   <username> hard nice eip
   ```

   Log out and log back in for the above changes to take effect.

2. **Connect to the real robot**

   Connect from computer to the real robot using an Ethernet cable, and set the computer's IP address to be `192.168.123.24` (or anything in the `192.168.123.X` range that does not collide with the robot's existing IPs). Make sure you can ping/SSH into the robot's TX2 computer (by default it is `unitree@192.168.123.12`).

### CODE STRUCTURE ###
1. Each environment is defined by an env file (`legged_robot.py`) and a config file (`legged_robot_config.py`). The config file contains two classes: one conatianing all the environment parameters (`LeggedRobotCfg`) and one for the training parameters (`LeggedRobotCfgPPo`).
2. Both env and config classes use inheritance.
3. Each non-zero reward scale specified in `cfg` will add a function with a corresponding name to the list of elements which will be summed to get the total reward. The AMP reward parameters are defined in `LeggedRobotCfgPPO`, as well as the path to the reference data.
4. Tasks must be registered using `task_registry.register(name, EnvClass, EnvConfig, TrainConfig)`. This is done in `envs/__init__.py`, but can also be done from outside of this repository.
5. Reference data can be found in the `datasets` folder. The `retarget_kp_motions.py` script can be used to convert keypoints to AMP reference trajectories, and `legged_gym/scripts/replay_amp_data.py` can be used to replay the reference trajectories.

### Usage ###
1. Train:
  ```python legged_gym/scripts/train.py --task=a1_amp``
    -  To run on CPU add following arguments: `--sim_device=cpu`, `--rl_device=cpu` (sim on CPU and rl on GPU is possible).
    -  To run headless (no rendering) add `--headless`.
    - **Important**: To improve performance, once the training starts press `v` to stop the rendering. You can then enable it later to check the progress.
    - The trained policy is saved in `AMP_for_hardware/logs/<experiment_name>/<date_time>_<run_name>/model_<iteration>.pt`. Where `<experiment_name>` and `<run_name>` are defined in the train config.
    -  The following command line arguments override the values set in the config files:
     - --task TASK: Task name.
     - --resume:   Resume training from a checkpoint
     - --experiment_name EXPERIMENT_NAME: Name of the experiment to run or load.
     - --run_name RUN_NAME:  Name of the run.
     - --load_run LOAD_RUN:   Name of the run to load when resume=True. If -1: will load the last run.
     - --checkpoint CHECKPOINT:  Saved model checkpoint number. If -1: will load the last checkpoint.
     - --num_envs NUM_ENVS:  Number of environments to create.
     - --seed SEED:  Random seed.
     - --max_iterations MAX_ITERATIONS:  Maximum number of training iterations.
2. Play a trained policy:
```python legged_gym/scripts/play.py --task=a1_amp```
    - By default the loaded policy is the last model of the last run of the experiment folder.
    - Other runs/model iteration can be selected by setting `load_run` and `checkpoint` in the train config.
3. Record video of a trained policy
```python legged_gym/scripts/record_policy.py --task=a1_amp```
    - This saves a video of the in the base directory.

### Adding a new environment ###
The base environment `legged_robot` implements a rough terrain locomotion task. The corresponding cfg does not specify a robot asset (URDF/ MJCF) and no reward scales.

1. Add a new folder to `envs/` with `'<your_env>_config.py`, which inherit from an existing environment cfgs
2. If adding a new robot:
    - Add the corresponding assets to `resourses/`.
    - In `cfg` set the asset path, define body names, default_joint_positions and PD gains. Specify the desired `train_cfg` and the name of the environment (python class).
    - In `train_cfg` set `experiment_name` and `run_name`
3. (If needed) implement your environment in <your_env>.py, inherit from an existing environment, overwrite the desired functions and/or add your reward functions.
4. Register your env in `isaacgym_anymal/envs/__init__.py`.
5. Modify/Tune other parameters in your `cfg`, `cfg_train` as needed. To remove a reward set its scale to zero. Do not modify parameters of other envs!


### Troubleshooting ###
1. If you get the following error: `ImportError: libpython3.8m.so.1.0: cannot open shared object file: No such file or directory`, do: `sudo apt install libpython3.8`

### Known Issues ###
1. The contact forces reported by `net_contact_force_tensor` are unreliable when simulating on GPU with a triangle mesh terrain. A workaround is to use force sensors, but the force are propagated through the sensors of consecutive bodies resulting in an undesireable behaviour. However, for a legged robot it is possible to add sensors to the feet/end effector only and get the expected results. When using the force sensors make sure to exclude gravity from trhe reported forces with `sensor_options.enable_forward_dynamics_forces`. Example:
```
    sensor_pose = gymapi.Transform()
    for name in feet_names:
        sensor_options = gymapi.ForceSensorProperties()
        sensor_options.enable_forward_dynamics_forces = False # for example gravity
        sensor_options.enable_constraint_solver_forces = True # for example contacts
        sensor_options.use_world_frame = True # report forces in world frame (easier to get vertical components)
        index = self.gym.find_asset_rigid_body_index(robot_asset, name)
        self.gym.create_asset_force_sensor(robot_asset, index, sensor_pose, sensor_options)
    (...)

    sensor_tensor = self.gym.acquire_force_sensor_tensor(self.sim)
    self.gym.refresh_force_sensor_tensor(self.sim)
    force_sensor_readings = gymtorch.wrap_tensor(sensor_tensor)
    self.sensor_forces = force_sensor_readings.view(self.num_envs, 4, 6)[..., :3]
    (...)

    self.gym.refresh_force_sensor_tensor(self.sim)
    contact = self.sensor_forces[:, :, 2] > 1.
```
