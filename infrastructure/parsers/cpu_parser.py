import re


def parse_typeperf(raw_output):

    lines = raw_output.splitlines()

    # Search from bottom to top
    for line in reversed(lines):

        line = line.strip()

        if not line:
            continue

        # Find a number inside the line
        numbers = re.findall(
            r'"(-?\d+(?:\.\d+)?)"',
            line
        )

        if numbers:
            return float(numbers[-1])

    raise ValueError(
        "Could not parse typeperf output"
    )