#!/usr/bin/env python3
"""Simple MuJoCo simulation for MyCobot Pro 450"""
import mujoco
import numpy as np

xml = open('mycobot_pro_450_primitives.xml').read()
model = mujoco.MjModel.from_xml_string(xml)
data = mujoco.MjData(model)

def set_angles(deg):
    for i in range(6):
        data.qpos[i+7] = deg[i] / 180.0 * np.pi
    mujoco.mj_forward(model, data)
    return data.xpos[model.body('link6').id][:3]

# Test: bent posture
pos = set_angles([0, -20, -30, 0, 0, -50])
print(f"Bent: end effector at ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

# Test: straight up
pos = set_angles([0, 0, 0, 0, 0, -50])
print(f"Straight: end effector at ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

print("\nTo render: python3 -m mujoco.viewer mycobot_pro_450_primitives.xml")
