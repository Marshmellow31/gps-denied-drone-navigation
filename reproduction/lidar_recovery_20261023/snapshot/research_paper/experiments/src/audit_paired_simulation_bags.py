"""Check that paired simulation bags contain matched sensor inputs."""
import argparse
import hashlib
import io
import json
from pathlib import Path


def inspect_bag(path: Path, expected_scans: int | None, expected_imu: int | None) -> dict:
    import rosbag

    with rosbag.Bag(str(path)) as bag:
        topics = bag.get_type_and_topic_info()[1]
        counts = {name: topics[name].message_count for name in sorted(topics)}
        if set(counts) != {'/sim/points', '/sim/imu'}:
            raise ValueError(f'{path}: unexpected sensor topics {sorted(counts)}')
        if expected_scans is not None and counts['/sim/points'] != expected_scans:
            raise ValueError(f'{path}: expected {expected_scans} scans, found {counts["/sim/points"]}')
        if expected_imu is not None and counts['/sim/imu'] != expected_imu:
            raise ValueError(f'{path}: expected {expected_imu} IMU messages, found {counts["/sim/imu"]}')
        digest = hashlib.sha256()
        serialized_count = 0
        for _, message, _ in bag.read_messages(topics=['/sim/imu']):
            buffer = io.BytesIO()
            message.serialize(buffer)
            digest.update(buffer.getvalue())
            serialized_count += 1
    if serialized_count != counts['/sim/imu']:
        raise ValueError(f'{path}: IMU topic count changed while reading')
    return {'path': str(path), 'topic_counts': counts,
            'serialized_imu_count': serialized_count,
            'serialized_imu_sha256': digest.hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corridor', type=Path, required=True)
    parser.add_argument('--control', type=Path, required=True)
    parser.add_argument('--expected-scans', type=int)
    parser.add_argument('--expected-imu', type=int)
    args = parser.parse_args()
    corridor = inspect_bag(args.corridor, args.expected_scans, args.expected_imu)
    control = inspect_bag(args.control, args.expected_scans, args.expected_imu)
    identical = (corridor['serialized_imu_count'] == control['serialized_imu_count']
                 and corridor['serialized_imu_sha256'] == control['serialized_imu_sha256'])
    result = {'corridor': corridor, 'control': control, 'paired_imu_identical': identical}
    print(json.dumps(result, indent=2))
    if not identical:
        raise SystemExit('paired IMU streams differ')


if __name__ == '__main__':
    main()
