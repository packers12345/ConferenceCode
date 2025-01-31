example_system_requirements = """
ID# Description
SR1 The system shall accept an input of “off-command” through IF-1
    - Note: IF-1 has undefined parameters to open the design space
    - Note: The off-command has undefined parameters to open the design space
SR2 The system shall accept an input of “on-command” through IF-1
    - Note: IF-1 has undefined parameters to open the design space
    - Note: The on-command has undefined parameters to open the design space
SR3 The system shall provide no-light after accepting the “off-command” through IF-2
    - Note: IF-2 has undefined parameters to open the design space
    - Lumen: <0.5 lm
SR4 The system shall provide an output of light through IF-2 after accepting the “on-command”:
    - Wavelength: 570-590 nm [yellow]
    - Lumen: 200-1,000 lm
    - Note: IF-2 has undefined parameters to open the design space
SR5 The system shall reject water through IF-3 according to the following standard:
    - Pressure: pressure within 1-5 atm
    - Humidity: 0-100%
    - Note: IF-3 has undefined parameters to open the design space
"""
