"""
ShopDesi Recommender — uses pre-trained ML models
Loads from models/ directory. If models missing, auto-trains.
"""
import json, pickle, math, re, os, time
from collections import defaultdict

DATA_DIR  = "data/"
MODEL_DIR = "models/"
INTEREST_THRESHOLD = 3

# ── Data loaders ──────────────────────────────────────────────────────────────
def load_products():
    with open(DATA_DIR + "products.json", encoding="utf-8") as f:
        return json.load(f)

def load_users():
    with open(DATA_DIR + "users.json", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_DIR + "users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# ── Load models ───────────────────────────────────────────────────────────────
def _load_models():
    """Load trained models; auto-train if missing."""
    needed = ["tfidf_model.pkl", "cf_model.pkl", "interest_model.pkl"]
    if not all(os.path.exists(MODEL_DIR + f) for f in needed):
        print("[Recommender] Models missing — running trainer...")
        from ml_trainer import train_all
        train_all(verbose=False)
    with open(MODEL_DIR + "tfidf_model.pkl", "rb") as f:
        tfidf  = pickle.load(f)
    with open(MODEL_DIR + "cf_model.pkl", "rb") as f:
        cf     = pickle.load(f)
    with open(MODEL_DIR + "interest_model.pkl", "rb") as f:
        imodel = pickle.load(f)
    return tfidf, cf, imodel

# Load static models at module level (products never change)
PRODUCTS    = load_products()
PRODUCT_MAP = {p["id"]: p for p in PRODUCTS}
_TFIDF, _CF, _IMODEL = _load_models()

def reload_models():
    """Call after retraining."""
    global _TFIDF, _CF, _IMODEL
    _TFIDF, _CF, _IMODEL = _load_models()

# ── TF-IDF helpers ────────────────────────────────────────────────────────────
def _tokenize(text):
    return re.findall(r'\w+', str(text).lower())

def _cosine_dict(a, b):
    common = set(a) & set(b)
    if not common: return 0.0
    dot   = sum(a[k]*b[k] for k in common)
    mag_a = math.sqrt(sum(v*v for v in a.values()))
    mag_b = math.sqrt(sum(v*v for v in b.values()))
    d = mag_a * mag_b
    return dot/d if d > 0 else 0.0

# ── Content-Based (uses precomputed similarities) ─────────────────────────────
def content_based(seed_ids, n=10, exclude_ids=None):
    """Use pre-trained TF-IDF similarity table."""
    exclude = set(exclude_ids or []) | set(seed_ids)
    sims    = _TFIDF.get("similarities", {})
    scores  = defaultdict(float)
    for sid in seed_ids:
        for sim_score, other_pid in sims.get(sid, []):
            if other_pid not in exclude:
                scores[other_pid] = max(scores[other_pid], sim_score)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [PRODUCT_MAP[pid] for pid, _ in ranked[:n] if pid in PRODUCT_MAP]

def search_tfidf(query):
    """Search using trained TF-IDF vectors."""
    tokens  = _tokenize(query)
    if not tokens: return {}
    qv      = {t: 1.0 for t in tokens}
    idf     = _TFIDF.get("idf", {})
    tfidf   = _TFIDF.get("tfidf", {})
    scores  = {}
    for p in PRODUCTS:
        pv   = tfidf.get(p["id"], {})
        # Apply IDF to query vector
        qv_w = {t: idf.get(t, 0.5) for t in tokens}
        scores[p["id"]] = _cosine_dict(qv_w, pv)
    return scores

# ── Interest score (from trained model, with live update) ─────────────────────
def get_user_interest_scores(user):
    """Combine trained interest model + live session behavior + signup interests."""
    trained_scores = _IMODEL.get("scores", {}).get(user["id"], {})
    w              = _IMODEL.get("weights", {"view":1,"cart":3,"purchase":5})

    # Live incremental scores on top of trained
    live = defaultdict(float, trained_scores)

    # Seed scores from signup/explicit interests (even for new users)
    for cat in user.get("interests", []):
        live[cat] += 2.0

    # Behavioral signals
    for pid in user.get("viewed", []):
        p = PRODUCT_MAP.get(pid)
        if p: live[p["category"]] += w.get("view", 1)
    for pid in user.get("cart", []):
        p = PRODUCT_MAP.get(pid)
        if p: live[p["category"]] += w.get("cart", 3)
    for pid in user.get("purchases", []):
        p = PRODUCT_MAP.get(pid)
        if p: live[p["category"]] += w.get("purchase", 5)
    for cat, cnt in user.get("category_views", {}).items():
        live[cat] += cnt * w.get("view", 1)
    return dict(live)

# ── Auto-detect interests from live score ─────────────────────────────────────
def update_category_views(user_id, category):
    users = load_users()
    for u in users:
        if u["id"] != user_id: continue
        cv = u.get("category_views", {})
        cv[category] = cv.get(category, 0) + 1
        u["category_views"] = cv
        interests = u.get("interests", [])
        if cv[category] >= INTEREST_THRESHOLD and category not in interests:
            interests.append(category)
            u["interests"] = interests
        break
    save_users(users)

# ── Collaborative Filtering (from trained matrix) ─────────────────────────────
def collaborative(user_id, n=10):
    """Use pre-trained user-user similarity matrix."""
    uid_idx  = _CF.get("uid_idx", {})
    user_sim = _CF.get("user_sim")
    matrix   = _CF.get("matrix")
    pids     = _CF.get("pids", [])

    if user_id not in uid_idx or user_sim is None:
        return []

    # Also use LIVE user data for seen items
    users    = load_users()
    user     = next((u for u in users if u["id"] == user_id), None)
    if not user: return []
    seen     = set(user.get("viewed",[]) + user.get("cart",[]) + user.get("purchases",[]))

    ui       = uid_idx[user_id]
    sim_row  = user_sim[ui]  # similarity to all other users

    # Weighted product scores from similar users
    import numpy as np
    weighted_scores = np.zeros(len(pids))
    for other_ui, sim in enumerate(sim_row):
        if sim > 0.01:
            weighted_scores += sim * matrix[other_ui]

    # Exclude already seen
    for pid in seen:
        if pid in _CF.get("pid_idx", {}):
            weighted_scores[_CF["pid_idx"][pid]] = 0

    top_idx = np.argsort(weighted_scores)[::-1][:n]
    result  = [PRODUCT_MAP[pids[i]] for i in top_idx
               if weighted_scores[i] > 0 and pids[i] in PRODUCT_MAP]
    return result

# ── Hybrid Recommend ──────────────────────────────────────────────────────────
def hybrid_recommend(user_id, n=12):
    """
    Hybrid = CF (40%) + Content-Based (30%) + Interest-Based (30%)
    Falls back to popularity for cold-start users.
    """
    users  = load_users()
    user   = next((u for u in users if u["id"] == user_id), None)
    if not user: return popular_products(n)

    seen   = set(user.get("viewed",[]) + user.get("cart",[]) + user.get("purchases",[]))
    seeds  = user.get("cart",[])[-5:] + user.get("viewed",[])[-6:]

    cf_n  = max(1, int(n * 0.4))
    cb_n  = max(1, int(n * 0.3))
    int_n = max(1, int(n * 0.3))

    cf_recs   = collaborative(user_id, n=cf_n)
    cb_recs   = content_based(seeds, n=cb_n, exclude_ids=list(seen)) if seeds else []
    int_recs  = interest_based_recommend(user_id, n=int_n)

    seen_ids = set(); result = []
    for p in cf_recs + cb_recs + int_recs:
        if p["id"] not in seen_ids and p["id"] not in seen and len(result) < n:
            result.append(p); seen_ids.add(p["id"])

    # Fill with popular
    for p in popular_products(n*3):
        if p["id"] not in seen_ids and p["id"] not in seen and len(result) < n:
            result.append(p); seen_ids.add(p["id"])
    return result

def viewed_based_recommend(user_id, n=8):
    users  = load_users()
    user   = next((u for u in users if u["id"] == user_id), None)
    if not user or not user.get("viewed"): return []
    seen   = set(user.get("viewed",[]) + user.get("cart",[]) + user.get("purchases",[]))
    return content_based(user["viewed"][-6:], n=n, exclude_ids=list(seen))

def cart_based_recommend(user_id, n=8):
    users = load_users()
    user  = next((u for u in users if u["id"] == user_id), None)
    if not user or not user.get("cart"): return []
    seen  = set(user.get("viewed",[]) + user.get("cart",[]) + user.get("purchases",[]))
    return content_based(user["cart"], n=n, exclude_ids=list(seen))

def interest_based_recommend(user_id, n=10):
    """Use interest scores to pick top categories + recommend from them."""
    users  = load_users()
    user   = next((u for u in users if u["id"] == user_id), None)
    if not user: return popular_products(n)

    seen   = set(user.get("viewed",[]) + user.get("cart",[]) + user.get("purchases",[]))
    scores = get_user_interest_scores(user)

    if not scores:
        return popular_products(n)

    # Sort categories by score
    top_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:4]
    result   = []
    seen_ids = set()
    per_cat  = max(2, n // len(top_cats))

    for cat, score in top_cats:
        pool = [p for p in PRODUCTS
                if p["category"] == cat
                and p["id"] not in seen
                and p["id"] not in seen_ids]
        pool.sort(key=lambda x: x["rating"] * math.log(x["popularity"]+1), reverse=True)
        for p in pool[:per_cat]:
            result.append(p); seen_ids.add(p["id"])

    return result[:n]

def trending_products(n=12):
    """Popularity + rating combined score."""
    scored = [(p, p["rating"] * math.log(p["popularity"]+1)) for p in PRODUCTS]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p,_ in scored[:n]]

def popular_products(n=12, category=None):
    pool = [p for p in PRODUCTS if not category or p["category"]==category]
    return sorted(pool, key=lambda x: x["popularity"], reverse=True)[:n]

def similar_products(pid, n=8):
    return content_based([pid], n=n, exclude_ids=[pid])

def category_products(category, exclude_ids=None, n=12):
    excl = set(exclude_ids or [])
    pool = [p for p in PRODUCTS if p["category"]==category and p["id"] not in excl]
    return sorted(pool, key=lambda x: x["popularity"], reverse=True)[:n]

def search_products(query, user_id=None, n=40):
    scores = search_tfidf(query)
    if user_id:
        users = load_users()
        user  = next((u for u in users if u["id"] == user_id), None)
        if user:
            int_scores = get_user_interest_scores(user)
            for p in PRODUCTS:
                boost = int_scores.get(p["category"], 0) * 0.01
                scores[p["id"]] = scores.get(p["id"], 0) + min(boost, 0.1)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [PRODUCT_MAP[pid] for pid,s in ranked[:n] if s > 0.01 and pid in PRODUCT_MAP]

def filter_and_sort(products=None, category=None, subcategory=None,
                    min_price=None, max_price=None, min_rating=None, sort_by="popularity"):
    result = list(products or PRODUCTS)
    if category:    result = [p for p in result if p["category"]==category]
    if subcategory: result = [p for p in result if p["subcategory"]==subcategory]
    if min_price is not None: result = [p for p in result if p["price"]>=min_price]
    if max_price is not None: result = [p for p in result if p["price"]<=max_price]
    if min_rating is not None: result = [p for p in result if p["rating"]>=float(min_rating)]
    sort_map = {
        "popularity": lambda x: -x["popularity"],
        "rating":     lambda x: (-x["rating"], -x["popularity"]),
        "price_low":  lambda x:  x["price"],
        "price_high": lambda x: -x["price"],
        "discount":   lambda x: -x["discount"],
        "newest":     lambda x: -x["id"],
    }
    result.sort(key=sort_map.get(sort_by, sort_map["popularity"]))
    return result

def get_categories():
    cats = {}
    for p in PRODUCTS:
        cats.setdefault(p["category"], set()).add(p["subcategory"])
    return {k: sorted(v) for k,v in sorted(cats.items())}

CATEGORIES = get_categories()
