# Fashionista v2 — Enhanced Fullstack Demo

What's new:
- Many more products and images (placeholder SVGs included). Each product has sizes, colors, brand, price, description.
- Working Search (instant) and Sort (price/name/brand).
- Favorites (Add to wishlist) stored in session.
- User signup/login (basic, for demo) with MySQL support; falls back to JSON when MySQL not configured.
- Admin panel to add/edit products (form-based). Admin auth is simple: create user with is_admin flag in DB.
- Animations & improved interactive styling (red/pink/orange theme).
- Updated requirements: mysql-connector-python==8.0.33

Run instructions:
1. Create & activate venv
2. pip install -r requirements.txt
3. (Optional) configure MySQL and run init_db.sql
4. python app.py
5. Open http://127.0.0.1:5000

Notes:
- This is a demo. Payments are simulated (no real gateway).
- If you want real images instead of SVG placeholders, you can replace files in static/images/ with your JPG/PNG images keeping filenames referenced in products.json or DB.
