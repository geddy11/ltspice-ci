# !/usr/bin/enc python3
# MIT License
#
# Copyright (c) 2024, Geir Drange
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import PyLTSpice.LTSpice_RawRead as RawRead
from PyLTSpice import RawRead
from PyLTSpice.log.ltsteps import LTSpiceLogReader
import codecs

plt.rcParams["figure.figsize"] = [12, 6]

PM_MIN = 50.0  # phase margin specification in dB


def plot_bode(fname):
    """Create bode plot of frequency response."""
    LTR = RawRead("../ltspice/" + fname)
    Vfb = LTR.get_trace("V(vfb)")
    Vin = LTR.get_trace("V(vin)")
    f = LTR.get_trace("frequency")  # get frequency axis
    steps = LTR.get_steps()
    fig, ax = plt.subplots()
    # magnitude
    for step in range(len(steps)):
        if step == 0:
            (l1,) = ax.plot(
                np.abs(f.get_wave(0)),
                20 * np.log10(np.abs(Vfb.get_wave(step) / Vin.get_wave(step))),
                color="tab:blue",
                label="Amplitude",
            )
        else:
            ax.plot(
                np.abs(f.get_wave(0)),
                20 * np.log10(np.abs(Vfb.get_wave(step) / Vin.get_wave(step))),
                color="tab:blue",
            )
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude (dB)")
    ax.set_xscale("log")
    ax.grid(True, which="both", axis="both")
    # phase
    ax2 = ax.twinx()
    for step in range(len(steps)):
        ph = np.degrees(
            np.unwrap(np.angle(Vfb.get_wave(step) / Vin.get_wave(step), deg=False))
        )
        if step == 0:
            ax2.plot(
                np.abs(f.get_wave(0)),
                ph,
                linestyle="--",
                color="tab:orange",
                label="Phase",
            )
        else:
            ax2.plot(np.abs(f.get_wave(0)), ph, linestyle="--", color="tab:orange")
    ax2.set_ylabel("Phase (degrees)")
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
    fig.suptitle("Open loop response")
    plt.tight_layout()
    plt.savefig("./" + fname.replace(".raw", ".png"), dpi=100)


def process_simdata(pmarg):
    """Create summary table of measurements in the simulation and bode plot"""
    # create summary table
    res = ["Pass"]
    if pmarg < PM_MIN:
        res[0] = "Fail"
    dfs = pd.DataFrame(
        {
            "Spec. (dB)": [PM_MIN],
            "Phase margin (°)": [pmarg],
            "Result": res,
        }
    )
    dfs = dfs.rename(index={0: "Min."})
    with open("./opamp_open_loop.md", "w") as f:
        f.write("## Simulation results for opamp_open_loop\n")
        f.write(dfs.to_markdown())
        f.write("\n\n")
    # create bode plot
    plot_bode("opamp_open_loop.raw")


def main():
    # convert .log file from ANSI to UTF-8
    with codecs.open("../ltspice/opamp_open_loop.log", "r", encoding="cp1252") as file:
        lines = file.read()
    with codecs.open("opamp_open_loop_utf.log", "w", encoding="utf8") as file:
        file.write(lines)
    # extract measurement with PyLTSpice
    data = LTSpiceLogReader("opamp_open_loop_utf.log")
    meas_names = data.get_measure_names()
    mlist = [f"{data[name][0]}" for name in meas_names]
    pm = tuple(mlist[0].replace("(", "").replace(")", "").split(","))
    process_simdata(float(pm[1].strip("°")))
    exit(0)


if __name__ == "__main__":
    main()
