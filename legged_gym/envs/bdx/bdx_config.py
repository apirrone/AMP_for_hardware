# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin

from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

MOTION_FILES = ["datasets/bdx/placo_moves/bdx_walk_forward.txt"]
NO_FEET = False  # Do not use feet in the amp observations and data


class BDXRoughCfg(LeggedRobotCfg):
    class env(LeggedRobotCfg.env):
        num_envs = 8
        include_history_steps = None  # Number of steps of history to include.
        num_observations = 51
        num_privileged_obs = 57
        num_actions = 15
        env_spacing = 1.0
        reference_state_initialization = False
        ee_names = ["left_foot", "right_foot"]
        get_commands_from_joystick = False
        amp_motion_files = MOTION_FILES
        get_commands_from_joystick = False
        get_commands_from_keyboard = False
        no_feet = NO_FEET
        debug_save_obs = False

        num_rma_obs=0

    class init_state(LeggedRobotCfg.init_state):
        pos = [0.0, 0.0, 0.16]  # x,y,z [m]
        default_joint_angles = {
            "left_hip_yaw": -0.03455234018541292,
            "left_hip_roll": 0.055730747490168285,
            "left_hip_pitch": 0.5397158397618105,
            "left_knee": -1.3152788306721914,
            "left_ankle": 0.6888361815639528,
            "neck_pitch": -0.1745314896173976,
            "head_pitch": -0.17453429522668937,
            "head_yaw": 0,
            "left_antenna": 0,
            "right_antenna": 0,
            "right_hip_yaw": -0.03646051060835733,
            "right_hip_roll": -0.03358034284950263,
            "right_hip_pitch": 0.5216150220237578,
            "right_knee": -1.326235199315616,
            "right_ankle": 0.7179857110436013,
        }

    class control(LeggedRobotCfg.control):
        # PD Drive parameters:
        control_type = "P"
        override_effort = True
        effort = 0.93  # Nm
        # effort = 0.52  # Nm

        dof_friction = 0.00

        stiffness_all = 10  # 10 [N*m/rad]
        damping_all = 0.03  # 0.03
        stiffness = {
            "left_hip_yaw": stiffness_all,
            "left_hip_roll": stiffness_all,
            "left_hip_pitch": stiffness_all,
            "left_knee": stiffness_all,
            "left_ankle": stiffness_all,
            "neck_pitch": stiffness_all,
            "head_pitch": stiffness_all,
            "head_yaw": stiffness_all,
            "left_antenna": 1,
            "right_antenna": 1,
            "right_hip_yaw": stiffness_all,
            "right_hip_roll": stiffness_all,
            "right_hip_pitch": stiffness_all,
            "right_knee": stiffness_all,
            "right_ankle": stiffness_all,
        }

        damping = {
            "left_hip_yaw": damping_all,
            "left_hip_roll": damping_all,
            "left_hip_pitch": damping_all,
            "left_knee": damping_all,
            "left_ankle": damping_all,
            "neck_pitch": damping_all,
            "head_pitch": damping_all,
            "head_yaw": damping_all,
            "left_antenna": 0,
            "right_antenna": 0,
            "right_hip_yaw": damping_all,
            "right_hip_roll": damping_all,
            "right_hip_pitch": damping_all,
            "right_knee": damping_all,
            "right_ankle": damping_all,
        }

        # action scale: target angle = actionScale * action + defaultAngle
        action_scale = 0.25  # 0.25
        # action_scale = 1.0  # 0.25

        # decimation: Number of control action updates @ sim DT per policy DT
        decimation = 4  # 4

    class terrain(LeggedRobotCfg.terrain):
        mesh_type = "plane"
        measure_heights = False
        static_friction = 5.0
        dynamic_friction = 5.0

    class asset(LeggedRobotCfg.asset):
        file = "{LEGGED_GYM_ROOT_DIR}/resources/robots/bdx/urdf/bdx.urdf"
        foot_name = "foot"
        penalize_contacts_on = []
        terminate_after_contacts_on = [
            "body_module",
            "head",
            "left_antenna",
            "right_antenna",
            "leg_module",
            "leg_module_2",
        ]
        flip_visual_attachments = False
        self_collisions = 1  # 1 to disable, 0 to enable...bitwise filter

    class sim(LeggedRobotCfg.sim):
        dt = 0.004  # 0.004
        substeps = 2  # 2

    class domain_rand:
        randomize_friction = False
        friction_range = [0.95, 1.05]
        randomize_base_mass = False
        added_mass_range = [-0.05, 0.05]
        push_robots = False
        push_interval_s = 15
        max_push_vel_xy = 0.5  # 0.3
        randomize_gains = False
        stiffness_multiplier_range = [0.95, 1.05]
        damping_multiplier_range = [0.95, 1.05]
        randomize_torques = False
        torque_multiplier_range = [0.95, 1.05]
        randomize_com = False
        com_range = [-0.01, 0.01]

    class noise:
        add_noise = False
        noise_level = 1.0  # scales other values

        class noise_scales:
            dof_pos = 0.01
            dof_vel = 0.01  # 1.5
            lin_vel = 0.01
            ang_vel = 0.01
            gravity = 0.01
            height_measurements = 0.1

    class rewards(LeggedRobotCfg.rewards):
        soft_dof_pos_limit = 0.9
        base_height_target = 0.15
        tracking_sigma = 0.25  # tracking reward = exp(-error^2/sigma)

        class scales(LeggedRobotCfg.rewards.scales):
            termination = 0.0
            # tracking_lin_vel = 1.5 * 1.0 / (0.002 * 8)
            # tracking_ang_vel = 0.5 * 1.0 / (0.002 * 8)
            tracking_lin_vel = 1.5
            tracking_ang_vel = 0.5
            lin_vel_z = 0.0
            ang_vel_xy = 0.0
            orientation = -0.1
            torques = -0.000025  # -0.000025
            dof_vel = 0.0
            dof_acc = 0.0
            base_height = -0.1
            feet_air_time = 0.2
            collision = 0.0
            feet_stumble = 0.0
            action_rate = -0.1
            stand_still = 0.0
            dof_pos_limits = 0.0
            close_default_position = -0.5

    class commands:
        curriculum = False  # False
        max_curriculum = 0.2
        num_commands = 4  # default: lin_vel_x, lin_vel_y, ang_vel_yaw, heading (in heading mode ang_vel_yaw is recomputed from heading error)
        resampling_time = 10.0  # time before command are changed[s]
        heading_command = False  # if true: compute ang vel command from heading error

        class ranges:
            lin_vel_x = [0.1, 0.1]  # min max [m/s]
            lin_vel_y = [0.0, 0.0]  # min max [m/s]
            ang_vel_yaw = [0.0, 0.0]  # min max [rad/s]
            heading = [0, 0]

    class viewer(LeggedRobotCfg.viewer):
        ref_env = 0
        pos = [0, 0, 1]  # [m]
        lookat = [11.0, 5, 1.0]  # [m]


class BDXRoughCfgPPO(LeggedRobotCfgPPO):
    class algorithm(LeggedRobotCfgPPO.algorithm):
        entropy_coef = 0.01

    class runner(LeggedRobotCfgPPO.runner):
        run_name = ""
        experiment_name = "bdx"
