# shared/utils.py
import string

def split_alphabet_among_proposers(num_proposers):
    """
    Splits a-z into letter ranges based on the number of proposers.
    Returns a list of lists like [['a','b','c'], ['d','e','f'], ...]
    """
    letters = list(string.ascii_lowercase)
    chunk_size = len(letters) // num_proposers
    remainder = len(letters) % num_proposers

    ranges = []
    start = 0

    for i in range(num_proposers):
        end = start + chunk_size + (1 if i < remainder else 0)
        ranges.append(letters[start:end])
        start = end

    return ranges
