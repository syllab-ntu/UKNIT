# **uKNIT framework**

An automated framework to design ciphers catering to specific needs using a genetic algorithm. Currently, it supports the design of ciphers specializing in ultra-low latency. Please check out our paper: [redacted]

---

## 📌 **Table of Contents**

- [Prerequisites](#pre-requisites)
- [Usage](#usage)

---

## **Prerequisites**

To install the python dependencies, please use

```bash
pip -r requirements.txt
```

For this project, we will require ~~three~~ two additional prerequisites.

~~##### OpenLane (for latency computation)~~

~~Download [OpenLane](https://github.com/The-OpenROAD-Project/OpenLane). Follow the instructions to install via the Docker method.~~

~~Note that as the newer version of the flow.tcl script does not seem to allow the synthesis step only, we will be replacing some of the scripts in the `OpenLane` directory to suit the requirements. The exact files that we are replacing can be found in `setup.sh`~~

##### Kissat (or any SAT solver of your choosing)

Download [kissat](https://github.com/arminbiere/kissat.git). Follow the instuctions to install.
Please ensure that the solver is added to your `PATH`. Alternatively, you can indicate the path to the executable in `config.py`.

##### Espresso

Download [espresso-logic](https://github.com/classabbyamp/espresso-logic.git). This is used to optimize the number of CNF clauses.
Please ensure that `espresso/bin` is added to your `PATH`. Alternatively, you can indicate the path to the executable in `config.py`.

---

## **Usage**

All the working codes are in the current folder.

The configuration file is `config.py`. In there, you will be able to see all the configurations for the parameters. Please adjust the parameters accordingly to the requirements.

Finally, run

```bash
python main.py
```

to execute and the results can be found in the `runs` directory.

---
