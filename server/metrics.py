from collections import defaultdict

last_seq = {}
packet_loss = defaultdict(int)
total_received = 0

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
    return {
        "total_received": total_received,
        "packet_loss": dict(packet_loss)
    }