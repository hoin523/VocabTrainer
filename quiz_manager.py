import json
import random
import os

DATA_DIR = "data"
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
WORD_LIST_FILE = os.path.join(DATA_DIR, "word_list.txt")

# 초기화
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

with open(WORD_LIST_FILE, 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f if line.strip()]

def get_random_word():
    return random.choice(words)

def load_stats():
    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def update_stats(word, correct):
    stats = load_stats()
    if word not in stats:
        stats[word] = {"correct": 0, "wrong": 0}
    if correct:
        stats[word]["correct"] += 1
    else:
        stats[word]["wrong"] += 1
    save_stats(stats)
