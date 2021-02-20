# F1 Manager Parts Optimizer

@author William M. Boler

@date Feb 20, 2021

Uses linear regression to optimize part selection for the popular mobile F1 Manager game.

## Setup

The project uses `pipenv`.  With Pipenv and an appropriate Python installed, execute the following after cloning: 

```bash
pipenv install
```

## Execution

You'll want to have some data collected before you start.  First, generate a `master_equipment.csv` with the following format for all parts in your garage:

```csv
name,type,class,lvl,power,aero,grip,reliability,pit_stop_time
```

### Combination Generation
Next, generate all combinations to file using the following command: 

```bash
pipenv run python generate_combinations.py ./data/master_equipment.csv -o ./data/combinations.csv
```
The resulting `combinations.csv` file will be used as a lookup table for calculating your best parts.

### Data Collection
Next, run a few races and collect your best parts and times.  An example `rankings.csv` lookas as the foolowing:

```csv
Brakes,Gearbox,Rear Wing,Front Wing,Suspension,Engine,Track,Qual Rain,Race Rain,Win,Points
Minimax,The Getaway,Lock & Load,Bullet,Compressor,The Brute,Hanoi,0,0,0,43
Minimax,The Getaway,Lock & Load,Bullet,Compressor,The Brute,Spain,0,0,0,44
Minimax,The Getaway,Lock & Load,Bullet,Compressor,The Brute,Spain,0,0,1,45
```

`Qual Rain`, `Race Rain`, and `Win` are all boolean values (0 or 1).  Points are the points you win among the race (1 to 47).  Be sure you do not misspell any of the part names. 

### Optimization
Based on your collected `rankings.csv`, determine the best setup by executing the following:

```bash
pipenv run python tell_best.py ./data/combinations.csv -p ./data/rankings.csv
```

Example Results: 
```bash
Coeffs: [0.18920426 0.16721772 0.22509051 0.10212378 0.05781894]
Brakes              Minimax
Engine             Big Bore
Front Wing               FX
Gearbox             Sliders
Rear Wing              BASE
Suspension       Compressor
power                    73
aero                     59
grip                     72
reliability              51
pit_stop_time          3.45
fitness             45.2921
Name: 201132, dtype: object
```

### Custom Coefficients
The coefficients were learned from the input `rankings.csv` file.  You can provide your own coefficents with the following: 

```bash
pipenv run python tell_best.py ./data/combinations_2.csv -c 1 1 1 1 -1
```

Example Results:
```
Brakes              Minimax
Engine             Big Bore
Front Wing           Bullet
Gearbox             Sliders
Rear Wing              BASE
Suspension       Compressor
power                    85
aero                     60
grip                     59
reliability              52
pit_stop_time          3.39
fitness              252.61
Name: 201130, dtype: object
```