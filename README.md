# Predictive Maintenance Data Generator Digital Twin

## Instructions to generate data
- Install Flownex Simulator
- Open project ICVs_v1.5 in Flownex Simulator and test the steady-state simulation
- Install Flownex Simulator (https://flownex.com/portals-and-relevant-info/download-flownex-se/). Registration and license are required. Student licenses are available.
- Install Python and the required packages listed on requirements.txt (highly recommended installing the same versions to achieve the same results).
- Execute the script ICVs_failure_simulation.py
- The resulting dataset is located in the outputs/ directory with the name synthetic_failure_data.csv.

## Project content description

- ICVs_v1.5.proj: Flownex simulation project, which contains the system topology and parameterized components;
- ICVs_v1.5_project/: Flownex simulation files directory
- inputs/: Directory containing boundary conditions and pre-processed data, inputs to the simulation process;
- notebooks/: Directory containing Jupyter notebooks with data manipulation, pre-processing, cleaning, exploratory data analysis, and machine learning modeling;
- outputs/: Directory containing the generated synthetic dataset and the trained machine learning models;
- raw_data/: Directory containing raw sensor data to be pre-processed before serving as boundary conditions;
- requirements.txt: Python packages needed to run the simulations;
- Flownex.py: Flownex Python API library;
- ICVs_failure_simulation.py: Script that automates the simulations with Flownex.