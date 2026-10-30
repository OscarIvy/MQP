% drone_params.m
% Initializes physical constants and simulation parameters for quadrotor model

clear; clc;

%% 1. Physical Constants
p.g = 9.81;                 % Gravity acceleration (m/s^2)
p.rho = 1.225;              % Air density (kg/m^3)

%% 2. Quadrotor Mechanical Parameters
p.m = 1.2;                  % Total mass of quadrotor (kg)
p.L = 0.225;                % Arm length from center of mass to motor axis (m)
p.gamma = deg2rad(30);

% Inertia Tensor (Assumes symmetric structure along principal axes)
p.Ixx = 0.015;              % Roll moment of inertia (kg*m^2)
p.Iyy = 0.015;              % Pitch moment of inertia (kg*m^2)
p.Izz = 0.028;              % Yaw moment of inertia (kg*m^2)
I = diag([p.Ixx, p.Iyy, p.Izz]);% Inertia Matrix

%% 3. Motor & Aerodynamic Coefficients
% Thrust F = C_T * omega^2, Torque Tau = C_Q * omega^2
C_T = 1.105e-5;           % Thrust coefficient (N / (rad/s)^2)
C_Q = 1.779e-7;           % Drag/Torque coefficient (N*m / (rad/s)^2)

max_rotor_speed = 1000;   % Max motor angular velocity (rad/s)
min_rotor_speed = 0;      % Min motor angular velocity (rad/s)

p.s = [1,-1,1,-1];
p.KT = 0.65;
p.KD = 0.65;
%% 4. Motor Mixing Matrix


%% 5. Simulation Initial Conditions
p.init_pos = [0; 0; 0];      % Initial Position [x, y, z] (m)
p.init_vel = [0; 0; 0];      % Initial Velocity [u, v, w] (m/s)
p.init_att = [0; 0; 0];      % Initial Euler Angles [phi, theta, psi] (rad)
p.init_rates = [0; 0; 0];    % Initial Body Angular Rates [p, q, r] (rad/s)


p.omega_h = sqrt(p.m*p.g / sum(p.KT));      % rad/s, hover speed
omega_h   = p.omega_h*ones(4,1);            % 4x1 vector for the integrator
disp('Quadrotor parameters successfully loaded into workspace.');