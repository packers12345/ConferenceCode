# verification_requirements.py
example_verification_requirements = {
    "VRPS2": {
        "IoX": [
            {"IoX_ID": "IoX_S1", "Descriptor": "Off-command", "Parameterization": {"N/A"}},
            {"IoX_ID": "IoX_S2", "Descriptor": "On-command", "Parameterization": {"N/A"}},
            {"IoX_ID": "IoX_S3", "Descriptor": "No-light", "Parameterization": {"Lumen": "<0.5 lm"}},
            {"IoX_ID": "IoX_S4", "Descriptor": "Yellow-light", "Parameterization": {"Wavelength": "570-590 nm [yellow]", "Lumen": "200-1,000 lm"}}
        ],
        "IF": [
            {"IF_ID": "IF-S1", "Descriptor": "On/off IF", "Parameterization": {"N/A"}},
            {"IF_ID": "IF-S2", "Descriptor": "Light IF", "Parameterization": {"N/A"}}
        ]
    },
    "VRPS4": {
        "IoX": [
            {"IoX_ID": "IoX_S1", "Descriptor": "Off-command", "Parameterization": {"N/A"}},
            {"IoX_ID": "IoX_S2", "Descriptor": "On-command", "Parameterization": {"N/A"}},
            {"IoX_ID": "IoX_S3", "Descriptor": "No-light", "Parameterization": {"Lumen": "<0.5 lm"}},
            {"IoX_ID": "IoX_S4", "Descriptor": "Blue-light", "Parameterization": {"Wavelength": "450-495 nm [blue]", "Lumen": "200-1,000 lm"}}
        ],
        "IF": [
            {"IF_ID": "IF-S1", "Descriptor": "On/off IF", "Parameterization": {"N/A"}},
            {"IF_ID": "IF-S2", "Descriptor": "Light IF", "Parameterization": {"N/A"}}
        ]
    },
    "VRPS5": {
        "IoX": [
            {"IoX_ID": "IoX_S1", "Descriptor": "0", "Parameterization": {"N/A"}},
            {"IoX_ID": "IoX_S2", "Descriptor": "1", "Parameterization": {"N/A"}},
            {"IoX_ID": "IoX_S3", "Descriptor": "0", "Parameterization": {"N/A"}},
            {"IoX_ID": "IoX_S4", "Descriptor": "1", "Parameterization": {"N/A"}}
        ],
        "IF": [
            {"IF_ID": "IF-S1", "Descriptor": "Input IF", "Parameterization": {"N/A"}},
            {"IF_ID": "IF-S2", "Descriptor": "Output IF", "Parameterization": {"N/A"}}
        ]
    }
}
