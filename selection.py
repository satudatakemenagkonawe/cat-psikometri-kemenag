from irt import fisher_information
from config import MAX_EXPOSURE
import random


def select_next_item(theta, bank, used_ids, exposure):

    candidates = []

    for item in bank:

        if item["id"] in used_ids:
            continue

        exp_rate = exposure.get(item["id"], 0)

        if exp_rate > MAX_EXPOSURE:
            continue

        info = fisher_information(theta, item["a"], item["b"], item["c"])

        candidates.append((info, item))

    if not candidates:
        return None

    candidates.sort(reverse=True, key=lambda x: x[0])

    top = candidates[:5]

    return random.choice(top)[1]
