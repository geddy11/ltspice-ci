# Continuous Integration with LTspice
This repo is a demonstration of how to run LTspice simulations in a continuous integration pipeline. LTspice is a professional electronics circuit simulator from Analog Devices, which can be downloaded free of charge.

Why do we want to run LTspice simulations in a CI pipeline?
  * Run long simulations on a build server
  * Automatically generate documentation from simulation results
  * Run multiple simulations in parallel

Any probably many other good reasons too!

## Test circuit
The circuit to be analyzed in this repo is a simple amplifier with a capacitive load. The purpose of this simulation is to determine the phase margin of the amplifier. The phase margin can be analyzed by inserting a small signal generator between the amplifier input and output (feedback):

![circuit](https://github.com/geddy11/ltspice-ci/raw/main/img/circuit.png)

The phase margin can be measured with a `.meas` statement, and the results of these measurements are output in the `.log` file produced by LTspice. We are also interested in the waveforms, which LTspice stores in the `.raw` file.

## LTspice in Docker
LTspice is a Windows program only, but it officially supports Wine (a compatibility layer allowing Windows programs to run on Linux). This means we can run LTspice in a Docker image on a Linux server. One issue with running GUI programs like LTspice in a terminal-only environment is that they tend to throw errors because there is no display available. To the rescue comes `xvfb` (X virtual framebuffer) which emulates a dumb framebuffer.

The Docker image with LTspice used here is made by Aanas Sayed. [Dockerfile link](https://github.com/aanas-sayed/docker-ltspice).

## Post-processing LTspice outputs
LTspice produces two output files we want to process:
  * .log-file (text file with measurements)
  * .raw-file (binary file with waveforms)

Thankfully there is a Python package called `PyLTSpice` that can interact with LTspice designs. Using `PyLTSpice` makes it simple to extract measurements from the log and waveforms from the raw-file. What we want to make is a bode plot like this:

![circuit](https://github.com/geddy11/ltspice-ci/raw/main/img/freq_resp.png)

## The pipeline
The pipeline consists of two jobs:
  * LTspice simulation.
    * The two output files (`.log` and `.raw`) are made available as artifacts to the next job.
  * Post processing.
    * A Python script utilizing `PyLTSpice` extracts the phase margin and bode plot data and outputs a markdown report.
    * The tool CML (Continuous Machine Learning) is used to publish the report as a comment to the commit on GitHub. This means you get an email with the report (including plot) too.

That's it, enjoy automation of LTspice simulations!
