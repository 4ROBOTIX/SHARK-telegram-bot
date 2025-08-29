import os
from difflib import get_close_matches

def get_answer(question):
    question = question.lower().strip()
    with open(os.path.join("knowledge", "instructions.txt"), "r", encoding="utf-8") as f:
        blocks = f.read().split("\n\n")
        
        qa_pairs = {}
        for block in blocks:
            if "\n" in block:
                questions, answer = block.split("\n", 1)
                for q in questions.split(","):
                    qa_pairs[q.strip().lower()] = answer.strip()

    matches = get_close_matches(question, qa_pairs.keys(), n=1, cutoff=0.4)
    if matches:
        return qa_pairs[matches[0]]
    return None
