#!/usr/bin/env python3
"""MuJoCo simulation for MyCobot Pro 450"""
import numpy as np

try:
    import mujoco
    HAS_MUJOCO = True
except ImportError:
    HAS_MUJOCO = False
    print("MuJoCo not installed. Run: pip install mujoco")

if HAS_MUJOCO:
    model = mujoco.MjModel.from_xml_path('mycobot_pro_450_primitives.xml')
    data = mujoco.MjData(model)

    def set_angles(deg):
        """Set joint angles in degrees, return end effector position in mm"""
        for i, d in enumerate(deg):
            data.qpos[model.jnt_qposadr[i]] = d / 180.0 * np.pi
        mujoco.mj_forward(model, data)
        return data.xpos[model.body('link5').id][:3] * 1000

    # Demo: move through known postures
    for name, angles in [
        ("Home (safe)", [0, 0, 0, 0, 0, 0]),
        ("Bent posture", [0, -20, -30, 0, 0, 0]),
        ("Extended", [0, 0, 0, 0, 0, 0]),
        ("J1 rotation", [90, 0, 0, 0, 0, 0]),
    ]:
        pos = set_angles(angles)
        print(f"{name:15s} angles={angles}  end_effector=({pos[0]:7.1f}, {pos[1]:7.1f}, {pos[2]:7.1f}) mm")

    print("\nTo render: python3 -m mujoco.viewer mycobot_pro_450_primitives.xml")

else:
    print("Install MuJoCo: pip install mujoco")
    print("Then run: python3 sim_arm.py")
    print("To render: python3 -m mujoco.viewer mycobot_pro_450_primitives.xml")
