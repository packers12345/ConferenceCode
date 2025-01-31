example_system_designs = {
    "SD1": {
        "IoX": [
            {"IoX_ID": "IoX_A1", "Descriptor": "Off-command", "Parameterization": {"Force": "0.5 N"}},
            {"IoX_ID": "IoX_A2", "Descriptor": "On-command", "Parameterization": {"Force": "0.5 N"}},
            {"IoX_ID": "IoX_A3", "Descriptor": "No-light", "Parameterization": {"Lumen": "<0.5 lm"}},
            {"IoX_ID": "IoX_A4", "Descriptor": "Yellow-light", "Parameterization": {"Wavelength": "580 nm [yellow]", "Lumen": "500 lm"}},
            {"IoX_ID": "IoX_C1", "Descriptor": "Water", "Parameterization": {"Pressure": "1-5 atm", "Humidity": "0-100%"}}
        ],
        "IF": [
            {"IF_ID": "IF-A1", "Descriptor": "On/off IF", "Parameterization": {"Diameter": "15 mm", "Material": "black rubber"}},
            {"IF_ID": "IF-A2", "Descriptor": "Light IF", "Parameterization": {"Diameter": "57 mm", "Material": "clear plastic"}},
            {"IF_ID": "IF-C1", "Descriptor": "Water IF", "Parameterization": {"Volume": "14,478 mm³", "Diameter": "57 mm", "Length": "254 mm", "Material": "black plastic"}}
        ]
    },
    "SD2": {
        "IoX": [
            {"IoX_ID": "IoX_B1", "Descriptor": "Off-command", "Parameterization": {"Torque": "0.5 Nm", "Rotation": "roll", "Position": "0 degrees", "Direction": "clockwise"}},
            {"IoX_ID": "IoX_B2", "Descriptor": "On-command 1", "Parameterization": {"Torque": "0.5 Nm", "Rotation": "roll", "Position(s)": "120 degrees", "Direction": "counterclockwise"}},
            {"IoX_ID": "IoX_B3", "Descriptor": "On-command 2", "Parameterization": {"Torque": "0.5 Nm", "Rotation": "roll", "Position(s)": "240 degrees", "Direction": "counterclockwise"}},
            {"IoX_ID": "IoX_B4", "Descriptor": "On-command 3", "Parameterization": {"Torque": "0.5 Nm", "Rotation": "roll", "Position(s)": "120 degrees", "Direction": "clockwise"}},
            {"IoX_ID": "IoX_B5", "Descriptor": "No-light", "Parameterization": {"Lumen": "<0.5 lm"}},
            {"IoX_ID": "IoX_B6", "Descriptor": "Yellow-light 1", "Parameterization": {"Wavelength": "590 nm [yellow]", "Lumen": "250 lm"}},
            {"IoX_ID": "IoX_B7", "Descriptor": "Yellow-light 2", "Parameterization": {"Wavelength": "590 nm [yellow]", "Lumen": "750 lm"}},
            {"IoX_ID": "IoX_C1", "Descriptor": "Water", "Parameterization": {"Pressure": "1-6 atm", "Humidity": "0-100%"}}
        ],
        "IF": [
            {"IF_ID": "IF-B1", "Descriptor": "On/off IF", "Parameterization": {"Diameter": "50 mm", "Material": "black plastic"}},
            {"IF_ID": "IF-B2", "Descriptor": "Light IF", "Parameterization": {"Diameter": "45 mm", "Material": "clear plastic"}},
            {"IF_ID": "IF-C1", "Descriptor": "Water IF", "Parameterization": {"Volume": "12,800 mm³", "Diameter": "50 mm", "Length": "250 mm", "Material": "black plastic"}}
        ]
    },
    "SD3": {
        "IoX": [
            {"IoX_ID": "IoX_A1", "Descriptor": "Off-command", "Parameterization": {"Force": "0.5 N"}},
            {"IoX_ID": "IoX_A2", "Descriptor": "On-command", "Parameterization": {"Force": "0.5 N"}},
            {"IoX_ID": "IoX_A3", "Descriptor": "No-light", "Parameterization": {"Lumen": "<0.5 lm"}},
            {"IoX_ID": "IoX_A4", "Descriptor": "Yellow-light", "Parameterization": {"Wavelength": "580 nm [yellow]", "Lumen": "500 lm"}},
            {"IoX_ID": "IoX_A5", "Descriptor": "No-power", "Parameterization": {"Voltage": "<0.01 V"}},
            {"IoX_ID": "IoX_A6", "Descriptor": "Power", "Parameterization": {"Voltage": "3 V"}},
            {"IoX_ID": "IoX_C1", "Descriptor": "Water", "Parameterization": {"Pressure": "1-5 atm", "Humidity": "0-100%"}}
        ],
        "IF": [
            {"IF_ID": "IF-A1", "Descriptor": "On/off IF", "Parameterization": {"Diameter": "15 mm", "Material": "black rubber"}},
            {"IF_ID": "IF-A2", "Descriptor": "Light IF", "Parameterization": {"Diameter": "57 mm", "Material": "clear plastic"}},
            {"IF_ID": "IF-A3", "Descriptor": "Power IF", "Parameterization": {"Material": "black plastic"}},
            {"IF_ID": "IF-C1", "Descriptor": "Water IF", "Parameterization": {"Volume": "14,478 mm³", "Diameter": "57 mm", "Length": "254 mm", "Material": "black plastic"}}
        ]
    },
    "SD4": {
        "IoX": [
            {"IoX_ID": "IoX_B1", "Descriptor": "Off-command", "Parameterization": {"Torque": "0.5 Nm", "Rotation": "roll", "Position": "0 degrees", "Direction": "clockwise"}},
            {"IoX_ID": "IoX_B2", "Descriptor": "On-command 1", "Parameterization": {"Torque": "0.5 Nm", "Rotation": "roll", "Position(s)": "120 degrees", "Direction": "counterclockwise"}},
            {"IoX_ID": "IoX_B3", "Descriptor": "On-command 2", "Parameterization": {"Torque": "0.5 Nm", "Rotation": "roll", "Position(s)": "240 degrees", "Direction": "counterclockwise"}},
            {"IoX_ID": "IoX_B4", "Descriptor": "On-command 3", "Parameterization": {"Torque": "0.5 Nm", "Rotation": "roll", "Position(s)": "120 degrees", "Direction": "clockwise"}},
            {"IoX_ID": "IoX_B5", "Descriptor": "No-light", "Parameterization": {"Lumen": "<0.5 lm"}},
            {"IoX_ID": "IoX_B6", "Descriptor": "Yellow-light 1", "Parameterization": {"Wavelength": "590 nm [yellow]", "Lumen": "250 lm"}},
            {"IoX_ID": "IoX_B7", "Descriptor": "Yellow-light 2", "Parameterization": {"Wavelength": "590 nm [yellow]", "Lumen": "750 lm"}},
            {"IoX_ID": "IoX_B8", "Descriptor": "No-power", "Parameterization": {"Voltage": "<0.01 V"}},
            {"IoX_ID": "IoX_B9", "Descriptor": "Power 1", "Parameterization": {"Voltage": "1.5 V"}},
            {"IoX_ID": "IoX_B10", "Descriptor": "Power 2", "Parameterization": {"Voltage": "3 V"}},
            {"IoX_ID": "IoX_C1", "Descriptor": "Water", "Parameterization": {"Pressure": "1-6 atm", "Humidity": "0-100%"}}
        ],
        "IF": [
            {"IF_ID": "IF-B1", "Descriptor": "On/off IF", "Parameterization": {"Diameter": "50 mm", "Material": "black plastic"}},
            {"IF_ID": "IF-B2", "Descriptor": "Light IF", "Parameterization": {"Diameter": "45 mm", "Material": "clear plastic"}},
            {"IF_ID": "IF-B3", "Descriptor": "Power IF", "Parameterization": {"Material": "black plastic"}},
            {"IF_ID": "IF-C1", "Descriptor": "Water IF", "Parameterization": {"Volume": "12,800 mm³", "Diameter": "50 mm", "Length": "250 mm", "Material": "black plastic"}}
        ]
    }
}
