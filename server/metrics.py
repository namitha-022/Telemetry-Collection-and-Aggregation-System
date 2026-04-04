from collections import defaultdict
import time
from threading import Lock

last_seq = {}
packet_loss = defaultdict(int)
total_received = 0
start_time = time.time()

seq_lock = Lock()


def update_sequence(system_id, seq):
    global total_received

    with seq_lock:
        total_received += 1

        if system_id in last_seq:
            expected = last_seq[system_id] + 1
            if seq > expected:
                lost = seq - expected
                packet_loss[system_id] += lost

            last_seq[system_id] = seq
        else:
            last_seq[system_id] = seq


def get_stats():
    elapsed = time.time() - start_time

    total_expected = sum(last_seq[s] + 1 for s in last_seq)
    total_lost = sum(packet_loss.values())

    packet_loss_percent = (total_lost / total_expected * 100) if total_expected > 0 else 0

    return {
        "total_received": total_received,
        "throughput": total_received / elapsed if elapsed > 0 else 0,
        "packet_loss": dict(packet_loss),
        "packet_loss_percent": round(packet_loss_percent, 2)
    }