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
from matplotlib.ticker import FormatStrFormatter
from PyLTSpice import RawRead
from PyLTSpice.log.ltsteps import LTSpiceLogReader

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
    ax.set_ylabel("Amplitude")
    plt.gca().yaxis.set_major_formatter(FormatStrFormatter("%ddB"))
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
    ax2.set_ylabel("Phase")
    plt.gca().yaxis.set_major_formatter(FormatStrFormatter("%d°"))
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax.transAxes)
    fig.suptitle("Frequency response")
    plt.tight_layout()
    plt.savefig("./" + fname.replace(".raw", ".png"), dpi=100)


def process_simdata(pmarg, pfreq):
    """Create summary table of measurements in the simulation."""
    # create summary table
    res = ["Pass"]
    if pmarg < PM_MIN:
        res[0] = "Fail"
    dfs = pd.DataFrame(
        {
            "Spec. (dB)": [PM_MIN],
            "Phase margin (°)": [pmarg],
            "Frequency (Hz)": [pfreq],
            "Result": res,
        }
    )
    dfs = dfs.rename(index={0: "Min."})
    with open("./freq_resp.md", "w") as f:
        f.write("## Simulation results for freq_resp.asc\n")
        f.write(dfs.to_markdown())
        f.write("\n\n")


def main():
    # extract measurements from log file
    data = LTSpiceLogReader("../ltspice/freq_resp.log")
    meas_names = data.get_measure_names()
    mlist = [f"{data[name][0]}" for name in meas_names]
    pm = tuple(mlist[0].replace("(", "").replace(")", "").split(","))
    process_simdata(float(pm[1].strip("°")), float(mlist[1]))
    # create bode plot from raw file
    plot_bode("freq_resp.raw")
    exit(0)


if __name__ == "__main__":
    main()
