% drone_params.m
% Initializes physical constants and simulation parameters for quadrotor model

clear; clc;

%% 1. Physical Constants
g = 9.81;                 % Gravity acceleration (m/s^2)
rho = 1.225;              % Air density (kg/m^3)

%% 2. Quadrotor Mechanical Parameters
m = 1.2;                  % Total mass of quadrotor (kg)
l = 0.225;                % Arm length from center of mass to motor axis (m)

% Inertia Tensor (Assumes symmetric structure along principal axes)
Ixx = 0.015;              % Roll moment of inertia (kg*m^2)
Iyy = 0.015;              % Pitch moment of inertia (kg*m^2)
Izz = 0.028;              % Yaw moment of inertia (kg*m^2)
I = diag([Ixx, Iyy, Izz]);% Inertia Matrix

%% 3. Motor & Aerodynamic Coefficients
% Thrust F = C_T * omega^2, Torque Tau = C_Q * omega^2
C_T = 1.105e-5;           % Thrust coefficient (N / (rad/s)^2)
C_Q = 1.779e-7;           % Drag/Torque coefficient (N*m / (rad/s)^2)

max_rotor_speed = 1000;   % Max motor angular velocity (rad/s)
min_rotor_speed = 0;      % Min motor angular velocity (rad/s)

%% 4. Motor Mixing Matrix
% Maps squared rotor speeds [Omega1^2; Omega2^2; Omega3^2; Omega4^2] 
% to total thrust and moments [F_total; Tau_x; Tau_y; Tau_z]
% Configured for standard 'X' frame geometry:
% Forward allocation matrix (Rotor Speeds^2 -> [Fz; Tx; Ty; Tz])
M = [
    C_T,           C_T,           C_T,           C_T;         
   -C_T*l*0.707,   C_T*l*0.707,   C_T*l*0.707,  -C_T*l*0.707; 
   -C_T*l*0.707,  -C_T*l*0.707,   C_T*l*0.707,   C_T*l*0.707; 
   -C_Q,           C_Q,          -C_Q,           C_Q          
];

% Control mixing matrix ([Fz; Tx; Ty; Tz] -> Rotor Speeds^2)
m_mix = inv(M);  % Inverse mixer for controller allocation

%% 5. Simulation Initial Conditions
init_pos = [0; 0; 0];      % Initial Position [x, y, z] (m)
init_vel = [0; 0; 0];      % Initial Velocity [u, v, w] (m/s)
init_att = [0; 0; 0];      % Initial Euler Angles [phi, theta, psi] (rad)
init_rates = [0; 0; 0];    % Initial Body Angular Rates [p, q, r] (rad/s)

disp('Quadrotor parameters successfully loaded into workspace.');