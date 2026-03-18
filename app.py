from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import json, time, os

from recommender import (
    PRODUCTS, PRODUCT_MAP, CATEGORIES,
    hybrid_recommend, viewed_based_recommend, cart_based_recommend,
    interest_based_recommend, search_products, similar_products,
    category_products, popular_products, trending_products,
    filter_and_sort, load_users, save_users,
    update_category_views, get_user_interest_scores,
    reload_models, INTEREST_THRESHOLD
)

app = Flask(__name__)
app.secret_key = "shopdesi_gp_bighapur_cse_2025"

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_user():
    uid = session.get("user_id")
    if not uid: return None
    return next((u for u in load_users() if u["id"] == uid), None)

def pub_user(u):
    d = dict(u); d.pop("password", None); return d

def track(uid, field, value):
    users = load_users()
    for u in users:
        if u["id"] != uid: continue
        lst = u.get(field, [])
        if isinstance(value, int):
            if value in lst: lst.remove(value)
            lst.append(value); u[field] = lst[-40:]
        elif isinstance(value, str):
            if value in lst: lst.remove(value)
            lst.append(value); u[field] = lst[-20:]
        break
    save_users(users)

# ── Page routes ───────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET","POST"])
def login():
    if session.get("user_id"): return redirect("/")
    if request.method == "POST":
        uname = request.form.get("username","").strip().lower()
        pwd   = request.form.get("password","").strip()
        user  = next((u for u in load_users() if u["username"]==uname and u["password"]==pwd), None)
        if user:
            session["user_id"] = user["id"]
            return redirect("/")
        return render_template("auth.html", mode="login", error="Invalid username or password.")
    return render_template("auth.html", mode="login")

@app.route("/signup", methods=["GET"])
def signup():
    if session.get("user_id"): return redirect("/")
    return render_template("auth.html", mode="signup")

@app.route("/logout")
def logout():
    session.clear(); return redirect("/login")

@app.route("/")
def home():
    if not session.get("user_id"): return redirect("/login")
    return render_template("home.html")

@app.route("/product/<int:pid>")
def product_page(pid):
    if not session.get("user_id"): return redirect("/login")
    if pid not in PRODUCT_MAP: return redirect("/")
    return render_template("product.html")

@app.route("/cart")
def cart_page():
    if not session.get("user_id"): return redirect("/login")
    return render_template("cart.html")

@app.route("/search")
def search_page():
    if not session.get("user_id"): return redirect("/login")
    return render_template("search.html")

@app.route("/profile")
def profile_page():
    if not session.get("user_id"): return redirect("/login")
    return render_template("profile.html")

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form.get("username")=="admin" and request.form.get("password")=="admin":
            session["admin"] = True; return redirect("/admin")
        return render_template("admin_login.html", error="Wrong credentials.")
    if not session.get("admin"):
        return render_template("admin_login.html")
    return render_template("admin.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None); return redirect("/admin")



# ── Login API (JSON) ──────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def api_login():
    data  = request.json or {}
    uname = data.get("username","").strip().lower()
    pwd   = data.get("password","").strip()
    user  = next((u for u in load_users() if u["username"]==uname and u["password"]==pwd), None)
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401
    session["user_id"] = user["id"]
    return jsonify({"ok": True, "user": pub_user(user)})

@app.route("/api/check-username")
def api_check_username():
    u     = request.args.get("u","").strip().lower()
    users = load_users()
    taken = any(usr["username"] == u for usr in users)
    return jsonify({"available": not taken, "username": u})

# ── Signup API ────────────────────────────────────────────────────────────────
@app.route("/api/signup", methods=["POST"])
def api_signup():
    data      = request.json or {}
    name      = data.get("name","").strip()
    username  = data.get("username","").strip().lower()
    email     = data.get("email","").strip().lower()
    password  = data.get("password","").strip()
    interests = data.get("interests", [])

    # Validations
    if not name or len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters."}), 400
    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if not username.isalnum() and not all(c.isalnum() or c=='_' for c in username):
        return jsonify({"error": "Username can only contain letters, numbers, underscore."}), 400
    if not password or len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters."}), 400
    if len(interests) < 2:
        return jsonify({"error": "Please select at least 2 interests."}), 400

    users = load_users()
    # Check duplicate username / email
    if any(u["username"] == username for u in users):
        return jsonify({"error": "Username already taken. Try another."}), 400
    if email and any(u.get("email","") == email for u in users):
        return jsonify({"error": "Email already registered."}), 400

    # Create user
    import time as _t
    new_id  = "u" + str(int(_t.time() * 1000))[-6:]
    avatar  = "".join(w[0].upper() for w in name.split()[:2])
    new_user = {
        "id":             new_id,
        "username":       username,
        "password":       password,
        "name":           name,
        "email":          email,
        "avatar":         avatar,
        "interests":      interests,
        "viewed":         [],
        "cart":           [],
        "searched":       [],
        "purchases":      [],
        "category_views": {},
        "joined":         _t.strftime("%Y-%m-%d"),
    }
    users.append(new_user)
    save_users(users)
    session["user_id"] = new_id
    return jsonify({"ok": True, "user": pub_user(new_user)})

# ═══════════════════════════════════════════════════════════════════════════════
# USER API
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/api/me")
def api_me():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    return jsonify(pub_user(u))

@app.route("/api/products")
def api_products():
    category    = request.args.get("category","")
    subcategory = request.args.get("subcategory","")
    sort_by     = request.args.get("sort","popularity")
    min_price   = request.args.get("min_price", type=int)
    max_price   = request.args.get("max_price", type=int)
    min_rating  = request.args.get("min_rating", type=float)
    page        = max(1, request.args.get("page",1,type=int))
    per_page    = 20
    filtered    = filter_and_sort(
        category=category or None, subcategory=subcategory or None,
        min_price=min_price, max_price=max_price,
        min_rating=min_rating, sort_by=sort_by)
    total = len(filtered)
    tp    = max(1,(total+per_page-1)//per_page)
    page  = min(page, tp)
    u     = get_user()
    return jsonify({
        "products":    filtered[(page-1)*per_page:page*per_page],
        "total":       total, "page": page, "total_pages": tp,
        "cart_ids":    u.get("cart",[]) if u else [],
        "categories":  CATEGORIES,
    })

@app.route("/api/product/<int:pid>")
def api_product(pid):
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    p = PRODUCT_MAP.get(pid)
    if not p: return jsonify({"error":"Not found"}), 404
    track(u["id"], "viewed", pid)
    update_category_views(u["id"], p["category"])
    u = get_user()
    return jsonify({
        "product":  p,
        "similar":  similar_products(pid, n=10),
        "cat_rec":  category_products(p["category"], exclude_ids=[pid], n=8),
        "in_cart":  pid in u.get("cart",[]),
        "cart_ids": u.get("cart",[]),
        "user":     pub_user(u),
    })

@app.route("/api/recommendations")
def api_recommendations():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    uid = u["id"]
    int_scores = get_user_interest_scores(u)
    return jsonify({
        "for_you":        hybrid_recommend(uid, n=12),
        "viewed_based":   viewed_based_recommend(uid, n=8),
        "cart_based":     cart_based_recommend(uid, n=8),
        "interest_based": interest_based_recommend(uid, n=10),
        "trending":       trending_products(n=8),
        "cart_ids":       u.get("cart",[]),
        "user":           pub_user(u),
        "interest_scores": int_scores,
    })

@app.route("/api/search")
def api_search():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    q = request.args.get("q","").strip()
    if not q: return jsonify({"results":[],"query":""})
    track(u["id"], "searched", q)
    u = get_user()
    return jsonify({
        "results":  search_products(q, user_id=u["id"], n=40),
        "query":    q,
        "cart_ids": u.get("cart",[]),
        "user":     pub_user(u),
    })

@app.route("/api/cart/toggle", methods=["POST"])
def api_cart_toggle():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    pid = request.json.get("product_id")
    if not pid or pid not in PRODUCT_MAP:
        return jsonify({"error":"Invalid product"}), 400
    users = load_users()
    for usr in users:
        if usr["id"] != u["id"]: continue
        cart = usr.get("cart",[])
        if pid in cart: cart.remove(pid); action="removed"
        else:           cart.append(pid); action="added"
        usr["cart"] = cart
        save_users(users)
        return jsonify({"action":action,"cart_count":len(cart),"pid":pid,"cart_ids":cart})
    return jsonify({"error":"User not found"}), 404

@app.route("/api/cart/remove", methods=["POST"])
def api_cart_remove():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    pid = request.json.get("product_id")
    users = load_users()
    for usr in users:
        if usr["id"] != u["id"]: continue
        cart = usr.get("cart",[])
        if pid in cart: cart.remove(pid)
        usr["cart"] = cart
        save_users(users)
        return jsonify({"cart_count":len(cart),"cart_ids":cart})
    return jsonify({}), 404

@app.route("/api/cart/items")
def api_cart_items():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    cart_ids = u.get("cart",[])
    return jsonify({"items":[PRODUCT_MAP[pid] for pid in cart_ids if pid in PRODUCT_MAP],"cart_ids":cart_ids})

@app.route("/api/cart/checkout", methods=["POST"])
def api_checkout():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    users = load_users()
    for usr in users:
        if usr["id"] != u["id"]: continue
        cart = usr.get("cart",[])
        purchases = usr.get("purchases",[])
        for pid in cart:
            if pid not in purchases: purchases.append(pid)
        usr["purchases"] = purchases[-50:]
        usr["cart"] = []
        save_users(users)
        return jsonify({"ok":True,"order_id":f"SD{int(time.time())}"})
    return jsonify({"error":"User not found"}), 404

@app.route("/api/products/bulk", methods=["POST"])
def api_products_bulk():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    ids = request.json.get("ids",[])
    return jsonify({"products":[PRODUCT_MAP[pid] for pid in ids if pid in PRODUCT_MAP],"cart_ids":u.get("cart",[])})

@app.route("/api/user/clear", methods=["POST"])
def api_user_clear():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    field = request.json.get("field")
    users = load_users()
    for usr in users:
        if usr["id"] != u["id"]: continue
        if   field=="all":           usr["viewed"]=[]; usr["cart"]=[]; usr["searched"]=[]; usr["interests"]=[]; usr["category_views"]={}
        elif field=="viewed":        usr["viewed"]=[]
        elif field=="cart":          usr["cart"]=[]
        elif field=="searched":      usr["searched"]=[]
        elif field=="interests":     usr["interests"]=[]
        elif field=="category_views":usr["category_views"]={}
        elif field=="purchases":     usr["purchases"]=[]
        save_users(users)
        return jsonify({"ok":True,"user":pub_user(usr)})
    return jsonify({"error":"User not found"}), 404

@app.route("/api/user/interests", methods=["POST"])
def api_user_interests():
    u = get_user()
    if not u: return jsonify({"error":"Not logged in"}), 401
    action   = request.json.get("action")
    interest = request.json.get("interest")
    if interest not in CATEGORIES: return jsonify({"error":"Invalid"}), 400
    users = load_users()
    for usr in users:
        if usr["id"] != u["id"]: continue
        ints = usr.get("interests",[])
        if action=="add" and interest not in ints:    ints.append(interest)
        elif action=="remove" and interest in ints:   ints.remove(interest)
        usr["interests"] = ints
        save_users(users)
        return jsonify({"ok":True,"interests":ints})
    return jsonify({"error":"User not found"}), 404

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN API
# ═══════════════════════════════════════════════════════════════════════════════
def req_admin():
    if not session.get("admin"): abort(403)

@app.route("/api/admin/stats")
def api_admin_stats():
    req_admin()
    users = load_users()
    # Category distribution
    cat_counts = {}
    for p in PRODUCTS:
        cat_counts[p["category"]] = cat_counts.get(p["category"],0) + 1
    # Top viewed products
    all_viewed = []
    for u in users: all_viewed += u.get("viewed",[])
    from collections import Counter
    top_viewed = [{"product": PRODUCT_MAP[pid], "count": cnt}
                  for pid, cnt in Counter(all_viewed).most_common(10) if pid in PRODUCT_MAP]
    # Category view distribution across all users
    cat_view_totals = {}
    for u in users:
        for cat, cnt in u.get("category_views",{}).items():
            cat_view_totals[cat] = cat_view_totals.get(cat,0) + cnt
    # Interest distribution
    all_interests = []
    for u in users: all_interests += u.get("interests",[])
    interest_counts = dict(Counter(all_interests))
    # Training stats
    train_stats = {}
    if os.path.exists("models/training_stats.json"):
        with open("models/training_stats.json") as f:
            train_stats = json.load(f)
    return jsonify({
        "total_products":   len(PRODUCTS),
        "total_users":      len(users),
        "total_views":      sum(len(u.get("viewed",[])) for u in users),
        "total_cart":       sum(len(u.get("cart",[])) for u in users),
        "total_purchases":  sum(len(u.get("purchases",[])) for u in users),
        "total_searches":   sum(len(u.get("searched",[])) for u in users),
        "categories":       list(CATEGORIES.keys()),
        "category_counts":  cat_counts,
        "cat_view_totals":  cat_view_totals,
        "top_viewed":       top_viewed,
        "interest_counts":  interest_counts,
        "training_stats":   train_stats,
        "interest_threshold": INTEREST_THRESHOLD,
    })

@app.route("/api/admin/users")
def api_admin_users():
    req_admin()
    users = load_users()
    return jsonify([{
        "id":u["id"],"name":u["name"],"username":u["username"],
        "interests":u.get("interests",[]),
        "viewed_count":len(u.get("viewed",[])),
        "cart_count":len(u.get("cart",[])),
        "purchase_count":len(u.get("purchases",[])),
        "search_count":len(u.get("searched",[])),
        "category_views":u.get("category_views",{}),
        "interest_scores": get_user_interest_scores(u),
    } for u in users])

@app.route("/api/admin/users/<uid>", methods=["PATCH"])
def api_admin_patch_user(uid):
    req_admin()
    data  = request.json
    users = load_users()
    for u in users:
        if u["id"] != uid: continue
        if "interests"       in data: u["interests"] = data["interests"]
        if "reset_viewed"    in data: u["viewed"] = []
        if "reset_cart"      in data: u["cart"] = []
        if "reset_purchases" in data: u["purchases"] = []
        if "reset_history"   in data: u["viewed"]=[]; u["searched"]=[]; u["category_views"]={}
        if "reset_all"       in data:
            u["viewed"]=[]; u["cart"]=[]; u["searched"]=[]
            u["purchases"]=[]; u["category_views"]={}
            # Only reset interests if not explicitly provided in same request
            if "interests" not in data: u["interests"]=[]
        save_users(users)
        return jsonify({"ok":True,"user":pub_user(u)})
    return jsonify({"error":"User not found"}), 404

@app.route("/api/admin/users/<uid>", methods=["DELETE"])
def api_admin_delete_user(uid):
    req_admin()
    users = load_users()
    orig  = len(users)
    users = [u for u in users if u["id"] != uid]
    if len(users) == orig:
        return jsonify({"error":"User not found"}), 404
    save_users(users)
    return jsonify({"ok": True})


@app.route("/api/admin/products")
def api_admin_products():
    req_admin()
    cat = request.args.get("category","")
    pool = [p for p in PRODUCTS if not cat or p["category"]==cat]
    return jsonify(pool)

@app.route("/api/admin/retrain", methods=["POST"])
def api_admin_retrain():
    req_admin()
    from ml_trainer import train_all
    stats = train_all(verbose=False)
    reload_models()
    return jsonify({"ok":True,"stats":stats})

@app.route("/api/admin/settings", methods=["GET","POST"])
def api_admin_settings():
    req_admin()
    if request.method == "POST":
        import recommender as rec
        data = request.json
        if "interest_threshold" in data:
            rec.INTEREST_THRESHOLD = max(1, int(data["interest_threshold"]))
            import ml_trainer as mt
            mt.INTEREST_THRESHOLD = rec.INTEREST_THRESHOLD
        return jsonify({"ok":True,"interest_threshold": rec.INTEREST_THRESHOLD})
    import recommender as rec
    return jsonify({"interest_threshold": rec.INTEREST_THRESHOLD})

@app.route("/api/admin/user_chart_data")
def api_admin_user_chart_data():
    req_admin()
    users = load_users()
    # Per-user interest scores for chart
    chart_data = []
    for u in users:
        scores = get_user_interest_scores(u)
        chart_data.append({
            "name": u["name"].split()[0],
            "username": u["username"],
            "scores": scores,
            "total_interactions": (
                len(u.get("viewed",[]))*1 +
                len(u.get("cart",[]))*3 +
                len(u.get("purchases",[]))*5
            )
        })
    return jsonify(chart_data)

# if __name__ == "__main__":
#     app.run(debug=True, port=5000, use_reloader=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
