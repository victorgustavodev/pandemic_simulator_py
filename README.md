# 🦠 Disease Spread Simulation

This project simulates the spread of a disease within a population using a cellular automata model. The visualization demonstrates how individuals, represented as colored cells, interact over time and how a disease propagates through this network.

---

## 🎯 Objectives

* Model the spread of a disease in a 2D population grid.
* Visually demonstrate the dynamic behavior of the disease.
* Explore the impact of different parameters such as **infection rate**, **recovery time**, and **immunity**.

---

## 🖼️ Example Output

Below is an example image generated by the simulation:

* 🟥 **Red**: Infected
* 🟩 **Green**: Healthy
* 🟨 **Yellow**: Immune/Recovered
* 🟦 **Blue**: Dead (or other defined state, depending on simulation logic)
* 🟪 **Purple**: Asymptomatic

*(Consider adding an actual image or a placeholder link here, e.g., `![Simulation Output](./example_output.png)`)*

---

## 💻 Technologies

* 🐍 Python

---

## 🧑‍🏫 How to Use

1.  **Configure Transition Probabilities:**

    You need to define the state transition probabilities in your Python script. This matrix determines the likelihood of an individual transitioning from one state to another in each time step.

    ```python
    self.transitionProbabilities = [
        #  H     S     A     D     I   (States: Healthy, Sick, Asymptomatic, Dead, Immune)
        [1.0,  0.0,  0.0,  0.0,  0.0 ],  # Healthy
        [0.2,  0.3,  0.11, 0.34, 0.05],  # Sick
        [0.3,  0.0,  0.6,  0.0,  0.1 ],  # Asymptomatic
        [0.0,  0.0,  0.0,  1.0,  0.0 ],  # Dead
        [0.7,  0.0,  0.0,  0.0,  0.3 ]   # Immune
    ]
    ```

2.  **Adjust Simulation Parameters:**

    Pay attention to the following parameters in your script:

    ```python
    # Probability of getting sick after interaction with a sick individual
    self.contagionFactor = 0.7

    # Probability of avoiding contact due to social distancing
    self.socialDistanceEffect = 0.0
    ```

3.  **Set Main Simulation Settings:**

    In your `main` execution block (or equivalent configuration section), configure these settings:

    ```python
    numberOfRuns = 1          # Number of times the simulation is executed
    gridSize = 156            # Size of the matrix (e.g., 156x156) corresponding to ~24,500 individuals
    numberOfGenerations = 51  # Number of weeks (51, as 0 often counts, for 52 weeks * 7 days = 364 days ~ 1 year)
    saveImages = True         # Save output images? (True or False)
    verbose = True            # Display details in the console? (True or False)
    ```

4.  **Run the Simulation:**

    Open your terminal, navigate to the project directory, and execute:

    ```bash
    python ./simulation_default.py
    ```

---