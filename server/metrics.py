from collections import defaultdict
import time

last_seq = {}
packet_loss = defaultdict(int)
total_received = 0
start_time = time.time()


def update_sequence(system_id, seq):
    global total_received
    total_received += 1

    if system_id in last_seq:
        expected = last_seq[system_id] + 1
        if seq > expected:
            lost = seq - expected
            packet_loss[system_id] += lost

    last_seq[system_id] = seq


def get_stats():
    elapsed = time.time() - start_time

    return {
        "total_received": total_received,
        "throughput": total_received / elapsed if elapsed > 0 else 0,
        "packet_loss": dict(packet_loss)
    }