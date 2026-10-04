"""Loading of the p0_y data files produced by generate_stat_data.py."""

from pathlib import Path

# The stat_analysis/ directory with the data files (the parent of the
# helpers/ package containing this module); data files are resolved
# inside it regardless of the current working directory.
DATA_DIR = Path(__file__).resolve().parent.parent


def load_p0_y(filename: str) -> tuple[list[float], list[int]]:
    """
    Reads a p0_y data file: one "<p0>, <y> " pair per line.

    Each line holds p0 — the probability of a random death on the
    fatal directions of the chart — and y = {0, 1} — the actually
    observed outcome.

    The filename is resolved inside the stat_analysis/ directory;
    an absolute path is used as is.
    """
    p0_list: list[float] = []
    y_list: list[int] = []

    path = Path(filename)
    if not path.is_absolute():
        path = DATA_DIR / path

    with open(path, encoding='utf-8') as f:
        for line in f:
            p0, y = line.strip().split(', ')
            p0_list.append(float(p0))
            y_list.append(int(y))

    return p0_list, y_list
