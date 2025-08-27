import os
from difflib import get_close_matches

def get_answer(question):
    with open(os.path.join("knowledge", "instructions.txt"), "r", encoding="utf-8") as f:
        blocks = f.read().split("\n\n")
        qa_pairs = dict(block.split("\n", 1) for block in blocks if "\n" in block)
    matches = get_close_matches(question, qa_pairs.keys(), n=1, cutoff=0.4)
    if matches:
        return qa_pairs[matches[0]].strip()
    return None
