example_system_requirements = """
ID# Description
SR1: Dual-Mode Driver Command Input via IF‑1
The car shall accept a driver command input (e.g., acceleration and braking signals) via interface IF‑1.
Note: IF‑1’s parameter space is open; the input is composed of both a digital control code (range: 0x00–0xFF) and an analog signal (pedal depression, 0–100%).
These parameters are intentionally left undefined to permit scalability and to explore equivalence in the command‐to‐response mapping.

SR2: Mapping of Driver Commands to Control Signals (Morphism M₁)
The system shall process the driver command input from IF‑1 using a morphism function M₁ that transforms the open-parameter signal space into internal engine and braking control signals.
M₁ shall preserve the “intent” of the driver command with an equivalence tolerance of less than 5% deviation between the reconstructed (via M₁⁻¹) and original command.
Note: The existence of an inverse mapping M₁⁻¹ is required for self-verification purposes.

SR3: Engine Output Verification via IF‑2
Upon processing an “acceleration” command, the system shall deliver engine output data through interface IF‑2.
Output parameters shall include engine RPM (target range defined by the mapped control signal), torque, and fuel injection timing.
The mapping function (M₁) shall ensure that the engine output is morphically equivalent to the driver’s intent as specified in SR2.

SR4: Braking Response Verification via IF‑3
Upon receipt of a “braking” command from IF‑1, the system shall engage the braking subsystem and provide output on interface IF‑3.
Output parameters shall include deceleration rate (target: 4–8 m/s²) and brake pressure (range: defined by the actuator design).
A dedicated morphism function M₂ shall map the braking command into the braking actuation profile and shall guarantee that the response is equivalent (within a 5% margin) to the intended deceleration.

SR5: Environmental Adaptation via IF‑4
The car shall monitor environmental conditions (e.g., road friction, ambient temperature, and humidity) via interface IF‑4.
If environmental sensor readings deviate more than 10% from nominal values, the system shall automatically recalibrate the morphism functions (M₁ and M₂) to maintain equivalence between driver commands and physical responses.
Note: IF‑4 is defined with an open parameter space to accommodate future additional environmental variables.

SR6: Continuous Equivalence Verification and Logging
The system shall log every driver command, the corresponding internal control state, and the resulting output data along with timestamps.
This log shall include the computed deviation between the input command and the output as determined by applying the inverse mapping M₁⁻¹.
The system shall generate a confidence metric, which must remain above 95% during normal operations, and flag an error if the equivalence drops below this threshold.

SR7: Self-Diagnostic and Recalibration Routine
The car shall perform a self-diagnostic routine at least once per operational cycle (or every 12 hours, whichever is shorter) to verify the integrity of the mapping functions.
During the routine, the system shall use M₁⁻¹ to reconstruct driver commands from the current engine and braking outputs.
Any reconstruction error exceeding 5% shall trigger an automatic recalibration of the morphism functions and issue a maintenance alert.

SR8: Integration of Verification Artifacts
The system shall maintain a digital repository of all verification artifacts (driver commands, internal mappings, sensor feedback, and environmental data) that serves as a metamodel.
This repository shall enable traceability between system requirements, internal designs, and verification outcomes, thus ensuring that the verification model is morphically equivalent to the system design as defined by the hierarchical relationships.
Note: The repository’s data schema is open to further refinement as additional morphic relationships are identified.


"""
