# 🛒 ShopDesi — E-Commerce Recommendation System
### Govt. Polytechnic Bighapur, Unnao | CSE 6th Semester Major Project

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open in browser
http://localhost:5000

# Admin Panel
http://localhost:5000/admin   →  admin / admin
```

---

## 👤 Auth System

### Login (existing users)
| Username | Password | Interests |
|---|---|---|
| rahul_tech | rahul123 | Electronics, Books |
| priya_fashion | priya123 | Fashion, Beauty |
| amit_fitness | amit123 | Sports & Fitness, Electronics |
| sneha_home | sneha123 | Home & Kitchen, Beauty |
| vikram_gamer | vikram123 | Electronics, Sports |
| ananya_books | ananya123 | Books, Fashion |
| rohit_budget | rohit123 | Electronics, Fashion, Books |
| Navya_beauty | navya123 | Beauty, Fashion |

### Signup (new users)
- Full Name, Username, Email (optional), Password
- **Select minimum 2 interests** from 6 categories
- Recommendations start immediately based on selected interests
- Interests evolve as you browse (auto-detect after 3 views in a category)

---

## 🤖 ML Algorithms

### 1. TF-IDF Content-Based Filtering
- Builds weighted TF-IDF vectors (name×4, brand×3, subcategory×3, category×2, tags×2)
- Precomputes top-20 cosine similarities per product at training time
- Used for: Similar Products, Because You Viewed, Complete Your Cart

### 2. Collaborative Filtering (User-Item Matrix)
- Builds interaction matrix: view×1, cart×2, purchase×3 weights
- L2-normalized, cosine user-user similarity
- Finds similar users → recommends what they liked

### 3. Interest Score Model
- Category score = views×1 + cart_adds×3 + purchases×5 + explicit_interests×2
- Auto-adds category to interests after 3 views (configurable in admin)
- Used for: For You, Interest-Based strip

### 4. Hybrid Recommendation
```
For You = 40% CF + 30% Content-Based + 30% Interest-Based
```

---

## 📁 Project Structure

```
ecommerce/
├── app.py              ← Flask backend + all API routes
├── recommender.py      ← ML engine (uses trained models)
├── ml_trainer.py       ← Model training pipeline
├── requirements.txt
├── data/
│   ├── products.json   ← 180 Indian products, 6 categories
│   └── users.json      ← Users (demo + new signups)
├── models/
│   ├── tfidf_model.pkl     ← Trained TF-IDF + similarities
│   ├── cf_model.pkl        ← Collaborative filtering matrix
│   ├── interest_model.pkl  ← Interest score model
│   └── training_stats.json ← Last training metadata
├── templates/
│   ├── auth.html       ← Login + Signup (unified)
│   ├── base.html       ← Navbar, footer layout
│   ├── home.html       ← Home with 5 rec strips + product grid
│   ├── product.html    ← Product detail page
│   ├── cart.html       ← Shopping cart
│   ├── search.html     ← Search results
│   ├── profile.html    ← User profile + interest manager
│   └── admin.html      ← Admin panel
└── static/
    ├── css/style.css   ← Main stylesheet (responsive)
    ├── css/auth.css    ← Auth page styles
    ├── css/admin.css   ← Admin panel styles
    ├── js/app.js       ← Main frontend JS
    └── js/admin.js     ← Admin frontend JS
```

---

## 🎯 Features

| Feature | Details |
|---|---|
| Auth | Login + Signup with interest selection, validation, live username check |
| Products | 180 Indian products, 6 categories, 18 subcategories |
| Recommendations | 5 strips: For You, Because You Viewed, Cart-Based, Interest-Based, Trending |
| Dynamic Interests | Auto-detects after 3 category views; manual add/remove in profile |
| Filters | Sort by popularity/rating/price/discount; filter by price range, rating, category |
| Search | TF-IDF relevance + interest boost |
| Cart | AJAX add/remove, real-time badge, checkout |
| Profile | Interest manager, category activity bars, interest score bars, clear buttons |
| ℹ️ Info | Every rec strip has explanation of which algorithm and why |
| Admin | Dashboard charts, user management, ML retrain, threshold control |
| Responsive | Mobile, tablet, desktop — fully responsive |

---

## 👨‍💻 Team
- Varun Singh (E23272135500064)
- Pravendra Kumar (E23272135500042)
- Vishesh Dhiman (E23273135500009)
- Anika Katiyar (E23273135500060)
