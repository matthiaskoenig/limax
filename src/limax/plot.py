"""Visualization of DOB curves."""
from pathlib import Path
from typing import Optional

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from limax.model import LX


# ------------------------------------------------------------------------------
SMALL_SIZE = 12
MEDIUM_SIZE = 15
BIGGER_SIZE = 25

matplotlib.rc("font", size=SMALL_SIZE)  # controls default text sizes
matplotlib.rc("axes", titlesize=SMALL_SIZE)  # fontsize of the axes title
matplotlib.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
matplotlib.rc("xtick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
matplotlib.rc("ytick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
matplotlib.rc("legend", fontsize=SMALL_SIZE)  # legend fontsize
matplotlib.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title
# ------------------------------------------------------------------------------


def plot_lx_matplotlib(lx: LX, fig_path: Optional[Path] = None) -> None:
    """Plot DOB curve using matplotlib."""
    ax1: Axes
    ax2: Axes
    f: Figure
    f, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
    f.subplots_adjust(hspace=0.3)

    f.suptitle(
        f"mID: {lx.metadata.mid}",
        fontdict={
            "size": 12,
        },
    )
    ax1.set_title(
        str(lx.metadata),
        fontdict={
            "family": "monospace",
            "size": 10,
        },
    )

    for ax in (ax1, ax2):
        ax.plot(np.array(lx.data.time) / 60, lx.data.dob, "-o", color="black")
        ax.grid(True)
        ax.set_xlabel("Time [min]", fontdict={"weight": "bold"})
    ax1.set_ylabel("DOB", fontdict={"weight": "bold"})
    ax2.set_yscale("log")
    ax2.set_ylim(bottom=1.0)

    # add information to plot

    plt.show()
    if fig_path:
        f.savefig(fig_path)


if __name__ == "__main__":
    from limax import EXAMPLE_LIMAX_PATIENT1_PATH
    from limax.io import parse_limax_file

    lx: LX = parse_limax_file(EXAMPLE_LIMAX_PATIENT1_PATH)
    print(lx.to_df())
    plot_lx_matplotlib(lx)
