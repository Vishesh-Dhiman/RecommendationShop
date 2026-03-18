"""
ML Model Trainer for ShopDesi Recommendation System
----------------------------------------------------
Trains and saves:
  1. TF-IDF Content-Based model  → models/tfidf_model.pkl
  2. Collaborative Filtering matrix → models/cf_model.pkl
  3. Interaction weight matrix     → models/interaction_matrix.pkl
  4. Training stats                → models/training_stats.json

Run manually:  python3 ml_trainer.py
Auto-called:   by recommender.py on first import or via /api/admin/retrain
"""
import json, pickle, math, re, time, os
from collections import defaultdict
import numpy as np

DATA_DIR   = "data/"
MODEL_DIR  = "models/"
os.makedirs(MODEL_DIR, exist_ok=True)

# ─── Weights for interaction types ───────────────────────────────────────────
WEIGHTS = {
    "view":     1.0,
    "time":     0.05,   # per second, capped
    "cart":     3.0,
    "purchase": 5.0,
    "search":   0.5,
}
INTEREST_THRESHOLD = 3   # category views → auto-interest

def load_products():
    with open(DATA_DIR + "products.json", encoding="utf-8") as f:
        return json.load(f)

def load_users():
    with open(DATA_DIR + "users.json", encoding="utf-8") as f:
        return json.load(f)

# ═══════════════════════════════════════════════════════════════════════════════
# 1.  TF-IDF Content-Based Model
# ═══════════════════════════════════════════════════════════════════════════════
def tokenize(text):
    return re.findall(r'\w+', str(text).lower())

def train_tfidf(products):
    """Build weighted TF-IDF vectors for all products."""
    print("  [TF-IDF] Building document corpus...")
    docs = {}
    for p in products:
        # Weight: name×4, brand×3, subcategory×3, category×2, tags×2, description×1
        tokens = (
            tokenize(p["name"])        * 4 +
            tokenize(p["brand"])       * 3 +
            tokenize(p["subcategory"]) * 3 +
            tokenize(p["category"])    * 2 +
            [t for t in p.get("tags", [])] * 2 +
            tokenize(p.get("description", ""))
        )
        docs[p["id"]] = tokens

    print(f"  [TF-IDF] Corpus: {len(docs)} docs")

    # TF
    tf = {}
    for pid, tokens in docs.items():
        freq = defaultdict(int)
        for t in tokens:
            freq[t] += 1
        n = len(tokens)
        tf[pid] = {t: c / n for t, c in freq.items()}

    # IDF (smooth)
    N  = len(docs)
    df = defaultdict(int)
    for tokens in docs.values():
        for t in set(tokens):
            df[t] += 1
    idf = {t: math.log((N + 1) / (n + 1)) + 1 for t, n in df.items()}

    # TF-IDF vectors
    tfidf = {}
    for pid, tf_vals in tf.items():
        tfidf[pid] = {t: v * idf.get(t, 1) for t, v in tf_vals.items()}

    # Compute ALL pairwise cosine similarities and store top-20 for each product
    print("  [TF-IDF] Computing pairwise similarities...")
    pids  = list(tfidf.keys())
    sims  = {}    # pid -> sorted list of (sim_score, other_pid)

    for i, pid_a in enumerate(pids):
        va = tfidf[pid_a]
        row = []
        for pid_b in pids:
            if pid_a == pid_b:
                continue
            vb   = tfidf[pid_b]
            common = set(va) & set(vb)
            if not common:
                continue
            dot   = sum(va[k] * vb[k] for k in common)
            mag_a = math.sqrt(sum(v*v for v in va.values()))
            mag_b = math.sqrt(sum(v*v for v in vb.values()))
            d     = mag_a * mag_b
            if d > 0:
                row.append((dot / d, pid_b))
        row.sort(reverse=True)
        sims[pid_a] = row[:20]   # keep top-20 similar products
        if i % 50 == 0:
            print(f"  [TF-IDF] Processed {i}/{len(pids)}...")

    vocab_size = len(idf)
    print(f"  [TF-IDF] Done. Vocab size: {vocab_size}")
    return {"tfidf": tfidf, "idf": idf, "similarities": sims,
            "vocab_size": vocab_size, "doc_count": N}


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  Collaborative Filtering — User-Item Matrix
# ═══════════════════════════════════════════════════════════════════════════════
def compute_interest_score(user, product_id):
    """Weighted interaction score for a user-product pair."""
    score = 0.0
    if product_id in user.get("viewed",   []):  score += WEIGHTS["view"]
    if product_id in user.get("cart",     []):  score += WEIGHTS["cart"]
    if product_id in user.get("purchases",[]): score += WEIGHTS["purchase"]
    # Search boost: if user searched something matching product category
    for q in user.get("searched", []):
        for tag in user.get("interests", []):
            if q.lower() in tag.lower():
                score += WEIGHTS["search"]
                break
    return score

def train_collaborative(users, products):
    """Build User-Item interaction matrix and user-user similarity."""
    print("  [CF] Building interaction matrix...")
    uids = [u["id"] for u in users]
    pids = [p["id"] for p in products]

    uid_idx = {uid: i for i, uid in enumerate(uids)}
    pid_idx = {pid: i for i, pid in enumerate(pids)}

    # Build matrix
    matrix = np.zeros((len(uids), len(pids)), dtype=np.float32)
    for u in users:
        ui = uid_idx[u["id"]]
        for pid in u.get("purchases", []):
            if pid in pid_idx: matrix[ui, pid_idx[pid]] += WEIGHTS["purchase"]
        for pid in u.get("cart",      []):
            if pid in pid_idx: matrix[ui, pid_idx[pid]] += WEIGHTS["cart"]
        for pid in u.get("viewed",    []):
            if pid in pid_idx: matrix[ui, pid_idx[pid]] += WEIGHTS["view"]

    print(f"  [CF] Matrix shape: {matrix.shape}")
    print(f"  [CF] Non-zero entries: {np.count_nonzero(matrix)}")

    # Normalize rows (L2)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    matrix_norm = matrix / norms

    # User-User cosine similarity
    user_sim = np.dot(matrix_norm, matrix_norm.T)
    np.fill_diagonal(user_sim, 0)   # no self-similarity

    sparsity = 1 - (np.count_nonzero(matrix) / matrix.size)
    print(f"  [CF] Sparsity: {sparsity:.2%}")
    print(f"  [CF] User-user similarity matrix: {user_sim.shape}")

    return {
        "matrix":       matrix,
        "matrix_norm":  matrix_norm,
        "user_sim":     user_sim,
        "uid_idx":      uid_idx,
        "pid_idx":      pid_idx,
        "uids":         uids,
        "pids":         pids,
        "sparsity":     float(sparsity),
        "nonzero":      int(np.count_nonzero(matrix)),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  Interest Score Model
# ═══════════════════════════════════════════════════════════════════════════════
def train_interest_model(users, products):
    """Calculate interest score per user per category."""
    print("  [Interest] Building category interest scores...")
    cat_products = defaultdict(list)
    for p in products:
        cat_products[p["category"]].append(p["id"])

    user_interest_scores = {}
    for u in users:
        cat_score = defaultdict(float)
        # From explicit category_views
        for cat, cnt in u.get("category_views", {}).items():
            cat_score[cat] += cnt * WEIGHTS["view"]
        # From viewed products
        for pid in u.get("viewed", []):
            p = next((x for x in products if x["id"] == pid), None)
            if p: cat_score[p["category"]] += WEIGHTS["view"]
        # From cart
        for pid in u.get("cart", []):
            p = next((x for x in products if x["id"] == pid), None)
            if p: cat_score[p["category"]] += WEIGHTS["cart"]
        # From purchases
        for pid in u.get("purchases", []):
            p = next((x for x in products if x["id"] == pid), None)
            if p: cat_score[p["category"]] += WEIGHTS["purchase"]
        # From explicit interests
        for cat in u.get("interests", []):
            cat_score[cat] += 2.0
        user_interest_scores[u["id"]] = dict(cat_score)

    print(f"  [Interest] Computed scores for {len(user_interest_scores)} users")
    return {"scores": user_interest_scores, "weights": WEIGHTS}


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TRAIN
# ═══════════════════════════════════════════════════════════════════════════════
def train_all(verbose=True):
    start = time.time()
    products = load_products()
    users    = load_users()

    if verbose:
        print(f"\n{'='*50}")
        print(f"  ShopDesi ML Trainer")
        print(f"  Products: {len(products)} | Users: {len(users)}")
        print(f"{'='*50}\n")

    if verbose: print("[1/3] Training TF-IDF Content-Based Model...")
    tfidf_model = train_tfidf(products)
    with open(MODEL_DIR + "tfidf_model.pkl", "wb") as f:
        pickle.dump(tfidf_model, f)
    if verbose: print(f"  Saved: {MODEL_DIR}tfidf_model.pkl\n")

    if verbose: print("[2/3] Training Collaborative Filtering Model...")
    cf_model = train_collaborative(users, products)
    with open(MODEL_DIR + "cf_model.pkl", "wb") as f:
        pickle.dump(cf_model, f)
    if verbose: print(f"  Saved: {MODEL_DIR}cf_model.pkl\n")

    if verbose: print("[3/3] Building Interest Score Model...")
    interest_model = train_interest_model(users, products)
    with open(MODEL_DIR + "interest_model.pkl", "wb") as f:
        pickle.dump(interest_model, f)
    if verbose: print(f"  Saved: {MODEL_DIR}interest_model.pkl\n")

    elapsed = time.time() - start
    stats = {
        "trained_at":    time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec":   round(elapsed, 2),
        "product_count": len(products),
        "user_count":    len(users),
        "vocab_size":    tfidf_model["vocab_size"],
        "cf_nonzero":    cf_model["nonzero"],
        "cf_sparsity":   cf_model["sparsity"],
        "models":        ["tfidf_model", "cf_model", "interest_model"],
        "weights":       WEIGHTS,
        "interest_threshold": INTEREST_THRESHOLD,
    }
    with open(MODEL_DIR + "training_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    if verbose:
        print(f"{'='*50}")
        print(f"  Training complete in {elapsed:.2f}s")
        print(f"  Vocab size:   {tfidf_model['vocab_size']}")
        print(f"  CF nonzero:   {cf_model['nonzero']}")
        print(f"  CF sparsity:  {cf_model['sparsity']:.2%}")
        print(f"{'='*50}\n")
    return stats

if __name__ == "__main__":
    train_all(verbose=True)
