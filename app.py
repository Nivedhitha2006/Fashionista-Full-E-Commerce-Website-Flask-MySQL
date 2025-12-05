from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import os, json
app = Flask(__name__)
app.secret_key = os.environ.get('FASHIONISTA_SECRET','dev-secret-key-v2')

DB_CONFIG = {
    'use_mysql': True,
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'fashionista'
}

def load_products_from_json():
    here = os.path.dirname(__file__)
    with open(os.path.join(here,'products.json'),'r',encoding='utf8') as f:
        return json.load(f)

def load_products_from_mysql():
    import mysql.connector
    conn = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'],
                                   password=DB_CONFIG['password'], database=DB_CONFIG['database'])
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def get_products():
    if DB_CONFIG.get('use_mysql', True):
        try:
            return load_products_from_mysql()
        except Exception as e:
            print('MySQL error:', e)
            return load_products_from_json()
    else:
        return load_products_from_json()

def get_product(pid):
    prods = get_products()
    for p in prods:
        if int(p['id'])==int(pid):
            return p
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products')
def api_products():
    q = request.args.get('q','').lower()
    brand = request.args.get('brand','').lower()
    sort = request.args.get('sort','')
    prods = get_products()
    if q:
        prods = [p for p in prods if q in p['name'].lower() or q in (p.get('description') or '').lower() or q in (p.get('brand') or '').lower()]
    if brand:
        prods = [p for p in prods if brand == (p.get('brand') or '').lower()]
    if sort=='price_asc':
        prods = sorted(prods, key=lambda x: float(x.get('price') or 0))
    elif sort=='price_desc':
        prods = sorted(prods, key=lambda x: float(x.get('price') or 0), reverse=True)
    elif sort=='name_asc':
        prods = sorted(prods, key=lambda x: x.get('name','').lower())
    elif sort=='name_desc':
        prods = sorted(prods, key=lambda x: x.get('name','').lower(), reverse=True)
    return jsonify(prods)

@app.route('/product/<int:pid>')
def product_page(pid):
    prod = get_product(pid)
    if not prod:
        return "Not found", 404
    return render_template('product.html', product=prod)

@app.route('/api/product/<int:pid>')
def api_product(pid):
    prod = get_product(pid)
    if not prod:
        return jsonify({'error':'not found'}), 404
    return jsonify(prod)

@app.route('/api/cart/add', methods=['POST'])
def api_cart_add():
    data = request.json
    pid = int(data.get('id'))
    qty = int(data.get('qty',1))
    prod = get_product(pid)
    if not prod:
        return jsonify({'error':'not found'}),404
    cart = session.get('cart',{})
    item = cart.get(str(pid), {'id':pid,'qty':0,'name':prod['name'],'price':prod['price'],'image':prod.get('image')})
    item['qty'] += qty
    cart[str(pid)] = item
    session['cart'] = cart; session.modified=True
    return jsonify({'ok':True,'cart':cart})

@app.route('/api/cart')
def api_cart():
    return jsonify(session.get('cart',{}))

@app.route('/api/cart/update', methods=['POST'])
def api_cart_update():
    data = request.json
    pid = str(data.get('id'))
    qty = int(data.get('qty',0))
    cart = session.get('cart',{})
    if pid in cart:
        if qty<=0:
            cart.pop(pid,None)
        else:
            cart[pid]['qty']=qty
    session['cart']=cart; session.modified=True
    return jsonify({'ok':True,'cart':cart})

@app.route('/api/fav/toggle', methods=['POST'])
def api_fav_toggle():
    pid = str(request.json.get('id'))
    fav_list = set(session.get('fav',[]))
    if pid in fav_list:
        fav_list.remove(pid)
    else:
        fav_list.add(pid)
    session['fav'] = list(fav_list); session.modified=True
    return jsonify({'ok':True,'fav':session['fav']})

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET','POST'])
def checkout():
    if request.method=='POST':
        session.pop('cart', None)
        return render_template('checkout.html', success=True)
    return render_template('checkout.html', success=False)

def load_users_json():
    here = os.path.dirname(__file__)
    path = os.path.join(here,'users.json')
    if os.path.exists(path):
        with open(path,'r',encoding='utf8') as f:
            return json.load(f)
    return []

def authenticate(email, password):
    if DB_CONFIG.get('use_mysql', True):
        try:
            import mysql.connector
            conn = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'],
                                           password=DB_CONFIG['password'], database=DB_CONFIG['database'])
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
            user = cur.fetchone()
            cur.close(); conn.close()
            return user
        except Exception as e:
            print('MySQL user load failed', e)
    users = load_users_json()
    for u in users:
        if u['email']==email and u['password']==password:
            return u
    return None

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email'); pwd = request.form.get('password')
        user = authenticate(email,pwd)
        if user:
            session['user'] = {'id': user.get('id'), 'email': user.get('email'), 'name': user.get('name'), 'is_admin': user.get('is_admin',0)}
            flash('Logged in')
            return redirect(url_for('index'))
        flash('Invalid creds')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name = request.form.get('name'); email=request.form.get('email'); pwd=request.form.get('password')
        if DB_CONFIG.get('use_mysql', True):
            try:
                import mysql.connector
                conn = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'],
                                               password=DB_CONFIG['password'], database=DB_CONFIG['database'])
                cur = conn.cursor()
                cur.execute("INSERT INTO users (email,password,name) VALUES (%s,%s,%s)", (email,pwd,name))
                conn.commit()
                cur.close(); conn.close()
                flash('Account created; please login')
                return redirect(url_for('login'))
            except Exception as e:
                print('MySQL insert failed', e)
        users = load_users_json()
        if any(u['email']==email for u in users):
            flash('Email exists')
            return redirect(url_for('signup'))
        users.append({'id': len(users)+1, 'email':email, 'password':pwd, 'name':name, 'is_admin':0})
        with open(os.path.join(os.path.dirname(__file__),'users.json'),'w',encoding='utf8') as f:
            json.dump(users,f,indent=2)
        flash('Account created; please login')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/admin')
def admin_index():
    user = session.get('user')
    if not user or not user.get('is_admin'):
        flash('Admin only')
        return redirect(url_for('login'))
    return render_template('admin/index.html')

@app.route('/admin/products')
def admin_products():
    user = session.get('user')
    if not user or not user.get('is_admin'):
        flash('Admin only'); return redirect(url_for('login'))
    prods = get_products()
    return render_template('admin/products.html', products=prods)

@app.route('/admin/products/new', methods=['GET','POST'])
def admin_new_product():
    user = session.get('user')
    if not user or not user.get('is_admin'):
        flash('Admin only'); return redirect(url_for('login'))
    if request.method=='POST':
        name = request.form.get('name'); brand = request.form.get('brand'); price = request.form.get('price') or 0
        image = request.form.get('image'); desc = request.form.get('description'); sizes = request.form.get('sizes'); colors = request.form.get('colors')
        if DB_CONFIG.get('use_mysql', True):
            try:
                import mysql.connector
                conn = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'],
                                               password=DB_CONFIG['password'], database=DB_CONFIG['database'])
                cur = conn.cursor()
                cur.execute("INSERT INTO products (name,brand,price,image,description,sizes,colors) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                            (name,brand,price,image,desc,sizes,colors))
                conn.commit()
                cur.close(); conn.close()
                flash('Product added')
                return redirect(url_for('admin_products'))
            except Exception as e:
                print('MySQL insert failed', e)
        prods = load_products_from_json()
        new_id = max([p['id'] for p in prods])+1
        prods.append({'id':new_id,'name':name,'brand':brand,'price':float(price),'image':image,'description':desc,'sizes':sizes,'colors':colors})
        with open(os.path.join(os.path.dirname(__file__),'products.json'),'w',encoding='utf8') as f:
            json.dump(prods,f,indent=2)
        flash('Product added')
        return redirect(url_for('admin_products'))
    return render_template('admin/new_product.html')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

if __name__=='__main__':
    app.run(debug=True)
