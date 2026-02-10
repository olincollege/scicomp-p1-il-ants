# Scientific Computing Project 1: Ants

Ant trail following simulation, reproducing results from the paper
[Modelling the Formation of Trail Networks by Foragin Ants (Watmough and Edelstein-Keshet, 1995)](https://personal.math.ubc.ca/~keshet/pubs/JamesAnts.pdf).

![Simulation Screenshot](img/output/3C.png)

## Usage

The simulation can be run online
[here!](https://olincollege.github.io/scicomp-p1-il-ants/)

Alternatively, you can clone and run the code locally:

```bash
# Clone the repository
git clone https://github.com/olincollege/scicomp-p1-il-ants.git
cd scicomp-p1-il-ants

# Create virtual environment
python -m venv ants-venv

# Activate virtual environment
# Linux / macOS:
source ants-venv/bin/activate
# Windows:
ants-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run simulation
python main.py
```

## Constants

The simulation is depended on a set of constants, which can be modified using
the UI. Here is a brief description of each constant, further explanation can be
found in the [Algorithm Overview](#algorithm-overview) section.

- **seed**: Random seed for reproducibility.
- **fidelity min**: Minimum random chance (out of 256) for an ant to lose the
  trail it's following. See [Fidelity Function](#fidelity-function).
- **fidelity delta**: Maximum increase in fidelity based on pheromone
  concentration. See [Fidelity Function](#fidelity-function).
- **pheromone deposition**: Amount of pheromones deposited by each ant at each
  time step.
- **pheromone saturation**: Pheromone concentration at which fidelity reaches
  its maximum value. See [Fidelity Function](#fidelity-function).
- **turning kernel**: Probability distribution used to determine how an ant
  turns when it moves randomly. $B_n$ is the probability of turning
  $n \times 45°$. See [Turning Kernel](#turning-kernel).

Constant presets match of specific figures from the paper, see
[Results](#results) for more details.

## Algorithm Overview

### Ants

Ants are the main creatures of the simulation. Each ant is represented by a
position and a heading. The heading is one of 8 possible directions (N, NE, E,
SE, S, SW, W, NW).

### Main Simulation Loop

This simulation shows the trail formation of ants on a 256x256 grid world. As
ants traverse the world, they deposit pheromones that other ants can sense and
follow. The simulation performs the following steps at each time step:

1. A new ant is spawned in the center of world, facing a random diagonal
   direction.
2. Each ant deposits pheromones at their current location. The amount of
   pheromones deposited is determined by $\tau$, `pheromone_deposition`.
3. Each ant moves according to the **trail following algorithm** (explained
   below).
4. Ants that move out of bounds are removed from the simulation.
5. Pheromones everywhere evaporate by 1 unit.

### Trail Following Algorithm

Each ant senses pheromones in the spaces directly in front, 45° to the left, and
45° to the right of where it's facing. It moves according to the following
algorithm:

1. There is a random chance for the ant lose the trail it's following,
   determined by the **fidelity function** (explained below). If the ant loses
   the trail, it moves randomly according to the **turning kernel** (explained
   below).
2. If there are pheromones directly in front of the ant, it moves forward.
3. If there are pheromones to the left and right of the ant, it turns in the
   direction with more pheromones.
4. If there are equal amounts of pheromones to the left and right of the ant, it
   moves randomly according to the **turning kernel** (explained below).

### Fidelity Function

The fidelity function is used to determine the probability that an ant will lose
the trail it's following. It is a function of the amount of pheromones in the
ant's current location, $C$. The following constants are used in the fidelity
function:

- $\phi_{min}$: `fidelity_min`
- $\phi\Delta$: `fidelity_delta`
- $C_s$: `pheromone_saturation`

The fidelity function is defined as follows:

![fidelity function](img/paper/fidelity_fn.png)

![graph of fidelity function](img/paper/fidelity_graph.png)

The ant has a $\frac{\phi(C)}{256}$ chance to lose the trail it's following.

### Turning Kernel

The turning kernel $B$, is a probability distribution used to determine how an
ant turns when it moves randomly. The turning kernel $B$, is a list of 5
numbers, $(B_0, B_1, B_2, B_3, B_4)$, where $B_n$ is the probability of turning
$n \times 45°$. After turning amount is determined, there is an equal chance of
turning left or right.

## Results

### Figure 3

In figure 3, all constants were kept the same except for fidelity minimum,
$\phi_{min}$. The following constants were used:

- fidelity delta, $\phi\Delta$= 0
- pheromone deposition, $\tau$ = 8
- pheromone saturation, $C_s$ = 0
- turning kernel, $B$ = (0.581, 0.36, 0.047, 0.008, 0.004)
- simulation run for 1500 time steps

#### Figure 3A, $\phi_{min}$ = 255

<img src="img/output/crop/3A_crop.png" height="300" />
<img src="img/paper/paper_3A.png" height="300" />

_Left: output from my simulation, Right: figure 3A from the paper_

#### Figure 3B, $\phi_{min}$ = 251

<img src="img/output/crop/3B_crop.png" height="300" />
<img src="img/paper/paper_3B.png" height="300" />

_Left: output from my simulation, Right: figure 3B from the paper_

#### Figure 3C, $\phi_{min}$ = 247

<img src="img/output/crop/3C_crop.png" height="300" />
<img src="img/paper/paper_3C.png" height="300" />

_Left: output from my simulation, Right: figure 3C from the paper_

In all three of these figures, my simulation yielded much higher trail density
with many more ants still in the simulation. Curiously, the figures in the paper
write that less than 500 ants remain in the simulation at the end of 1500 time
steps for all three examples, while in each of my simulations ~1100 ants remain.
The result from the paper would imply that 1000 ants leave the world in the 1500
time steps, which seems unlikely. Some of my peers have speculated that the
number of ants in the paper is capped to a certain value, which could explain
the discrepancy.

### Figure 4

In figure 4, all constants were kept the same except for pheromone deposition,
$\tau$. The following constants were used:

- fidelity minimum, $\phi_{min}$ = 247
- fidelity delta, $\phi\Delta$= 0
- pheromone saturation, $C_s$ = 0
- turning kernel, $B$ = (0.581, 0.36, 0.047, 0.008, 0.004)
- simulation run for 4000 time steps

#### Figure 4A, $\tau$ = 12

<img src="img/output/crop/4A_crop.png" height="300" />
<img src="img/paper/paper_4A.png" height="300" />

_Left: output from my simulation, Right: figure 4A from the paper_

#### Figure 4B, $\tau$ = 8

<img src="img/output/crop/4B_crop.png" height="300" />
<img src="img/paper/paper_4B.png" height="300" />

_Left: output from my simulation, Right: figure 4B from the paper_

#### Figure 4C, $\tau$ = 4

<img src="img/output/crop/4C_crop.png" height="300" />
<img src="img/paper/paper_4C.png" height="300" />

_Left: output from my simulation, Right: figure 4C from the paper_

A similar result to figure 3. My simulation yielded much higher trail density
with many more ants still in the simulation. Figure 4C looks quite similar
between my simulation and the paper, likely the low pheromone deposition means
most trails evaporate, leaving only the large "X" pattern.

### Figure 5

In figure 5, a new turning kernel is used, favoring narrower turns. All
constants were kept the same except for fidelity minimum, $\phi_{min}$. The
following constants were used:

- fidelity delta, $\phi\Delta$= 0
- pheromone deposition, $\tau$ = 8
- pheromone saturation, $C_s$ = 0
- turning kernel, $B$ = (0.822, 0.135, 0.031, 0.008, 0.004)
- simulation run for 1500 time steps

#### Figure 5A, $\phi_{min}$ = 255

<img src="img/output/crop/5A_crop.png" height="300" />
<img src="img/paper/paper_5A.png" height="300" />

_Left: output from my simulation, Right: figure 5A from the paper_

#### Figure 5B, $\phi_{min}$ = 251

<img src="img/output/crop/5B_crop.png" height="300" />
<img src="img/paper/paper_5B.png" height="300" />

_Left: output from my simulation, Right: figure 5B from the paper_

#### Figure 5C, $\phi_{min}$ = 247

<img src="img/output/crop/5C_crop.png" height="300" />
<img src="img/paper/paper_5C.png" height="300" />

_Left: output from my simulation, Right: figure 5C from the paper_

These figures match up fairly well, though the my simulation still has many more
ants remaining. The narrower turning kernel results in much straighter and more
clean trails, which matches the paper's results.

#### Figure 6

In figure 6, pheromone saturation is finally introduced and is the main variable
being changed. The following constants were used:

- fidelity minimum, $\phi_{min}$ = 20
- fidelity delta, $\phi\Delta$= 235
- pheromone deposition, $\tau$ = 6
- turning kernel, $B$ = (0.581, 0.36, 0.047, 0.008, 0.004)
- simulation run not listed in paper, my simulation was run for 1500 time steps

#### Figure 6A, $C_s$ = 6

<img src="img/output/crop/6A_crop.png" height="300" />
<img src="img/paper/paper_6A.png" height="300" />

_Left: output from my simulation, Right: figure 6A from the paper_

#### Figure 6B, $C_s$ = 18

<img src="img/output/crop/6B_crop.png" height="300" />
<img src="img/paper/paper_6B.png" height="300" />

_Left: output from my simulation, Right: figure 6B from the paper_

These results also don't match up so well. In the paper, strong trails struggled
to form, while my simulation shows a network of paths simular to figure 3.
However, compared my figure 3 the trails are spareser, matching the trend of the
paper's results slightly. Again, my simulation has many more ants remaining than
the paper's.
