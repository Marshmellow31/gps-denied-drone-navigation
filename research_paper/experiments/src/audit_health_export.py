"""Read-only checks of a FAST-LIO diagnostic CSV and optional pose parity."""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def audit(path):
    groups = {}
    reasons = Counter()
    previous = -1
    with Path(path).open(newline="") as stream:
        reader = csv.DictReader(stream)
        assert len(reader.fieldnames) == 12, "unexpected header"
        for row in reader:
            assert None not in row and None not in row.values(), "incorrect CSV width"
            stamp = int(row["timestamp_ns"])
            assert stamp >= previous, "timestamps decrease"
            previous = stamp
            scale = float(row["lever_scale_m"])
            group = groups.setdefault(stamp, set())
            assert scale not in group, "duplicate timestamp/scale"
            group.add(scale)
            assert row["valid"] in ("true", "false")
            values = [row[f"eigenvalue_{i}"] for i in range(6)]
            if row["valid"] == "true":
                eigen = [float(x) for x in values]
                assert all(math.isfinite(x) and x >= 0 for x in eigen)
                assert eigen == sorted(eigen), "eigenvalues not ascending"
                assert int(row["accepted_count"]) >= 6
                assert not row["unavailable_reason"]
                reasons["VALID"] += 1
            else:
                assert all(x == "" for x in values), "invalid row contains eigenvalues"
                assert row["unavailable_reason"], "missing unavailable reason"
                reasons[row["unavailable_reason"]] += 1
    assert groups and all(x == {1.0, 3.0, 5.0} for x in groups.values())
    return {"timestamp_groups": len(groups), "row_counts": dict(reasons),
            "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()
    print(json.dumps(audit(args.csv), indent=2))
