from collections import defaultdict

from entities import MatchCharDict

PARTITION_SIZE = 10


# Returning a dict may be awkward for most use cases but it helps when
# you want to select one group only
def group(chars: list[MatchCharDict]) -> dict[int, list[MatchCharDict]]:
    """
    Group the characters by the number of items they have, using a certain group size.
    """
    # Merge buckets with PARTITION_SIZE to account for
    # some items being missing
    groups = defaultdict(list)
    for char in chars:
        id_set = char["items"]
        # Round to nearest PARTITION_SIZE
        # so the output will be {10: [...], 20: [...], 30: [...], ... 120: [...]}
        # for PARTITION_SIZE = 10
        rounded = round(len(id_set) / PARTITION_SIZE) * PARTITION_SIZE
        groups[rounded].append(char)
    return groups
