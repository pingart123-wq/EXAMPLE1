import streamlit as st
import pandas as pd
import json
import os
import datetime
import time

# ================= 1. PAGE SETUP & CSS INJECTION =================
st.set_page_config(
    page_title="GourmetOS PH | Enterprise",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load FontAwesome & Custom CSS
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* --- GLOBAL THEME --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #1f2937;
        }
        
        /* Remove Streamlit Default Padding */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        
        /* --- CARDS & CONTAINERS --- */
        .stContainer, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #f3f4f6;
            padding: 15px;
        }
        
        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {
            .stContainer, div[data-testid="stMetric"] {
                background-color: #1e293b;
                border-color: #334155;
                color: white;
            }
        }

        /* --- METRICS --- */
        div[data-testid="stMetricLabel"] { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #6b7280; }
        div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #111827; }
        
        /* --- POS MENU CARDS --- */
        .menu-card-header {
            text-align: center;
            padding-bottom: 10px;
        }
        .menu-img {
            font-size: 40px; 
            margin-bottom: 10px;
            display: block;
        }
        .menu-title { font-weight: 700; font-size: 14px; margin-bottom: 5px; }
        .menu-price { color: #2563eb; font-weight: 700; font-size: 16px; }

        /* --- BUTTONS --- */
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: all 0.2s;
        }
        /* Primary Button (Blue) */
        div.stButton > button[kind="primary"] {
            background-color: #2563eb;
            color: white;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #1d4ed8;
        }
        
        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: #0f172a; /* Dark Sidebar */
        }
        [data-testid="stSidebar"] * {
            color: #e2e8f0 !important;
        }
        
        /* --- LOGIN PAGE --- */
        .login-container {
            background: rgba(255, 255, 255, 0.9);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ================= 2. DATA ENGINE =================
DB_FILE = "restaurant.json"

DEFAULT_DATA = {
    "menu": [
        {"id": 1, "name": "Truffle Burger", "cat": "Burger", "price": 295.00, "icon": "🍔"},
        {"id": 2, "name": "Ribeye Steak", "cat": "Main", "price": 1250.00, "icon": "🥩"},
        {"id": 3, "name": "Classic Sisig", "cat": "Main", "price": 250.00, "icon": "🍳"},
        {"id": 4, "name": "Crispy Pata", "cat": "Main", "price": 680.00, "icon": "🍖"},
        {"id": 5, "name": "Carbonara", "cat": "Main", "price": 320.00, "icon": "🍝"},
        {"id": 6, "name": "Halo-Halo", "cat": "Dessert", "price": 150.00, "icon": "🍧"},
        {"id": 7, "name": "San Miguel", "cat": "Drink", "price": 95.00, "icon": "🍺"},
        {"id": 8, "name": "Iced Tea", "cat": "Drink", "price": 85.00, "icon": "🍹"},
        {"id": 9, "name": "Garlic Rice", "cat": "Sides", "price": 45.00, "icon": "🍚"},
    ],
    "staff": [{"id": 1, "name": "Juan Cruz", "role": "Manager"}, {"id": 2, "name": "Maria Clara", "role": "Chef"}],
    "sales": [],
    "orders": [], # Active kitchen orders
    "reservations": [],
    "tables": [{"id": i+1, "status": "Free"} for i in range(8)]
}

def load_db():
    if not os.path.exists(DB_FILE):
        return DEFAULT_DATA
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return DEFAULT_DATA

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Init Session State
if 'db' not in st.session_state:
    st.session_state.db = load_db()
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'user' not in st.session_state:
    st.session_state.user = None

# Helper
def peso(val): return f"₱{val:,.2f}"

# ================= 3. AUTHENTICATION =================
def login():
    # Background Image using CSS
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-4.0.3&auto=format&fit=crop&w=2340&q=80");
            background-size: cover;
            background-position: center;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("") # Spacer
        st.write("")
        st.write("")
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown("<h1 style='color:#111827;'>Gourmet<span style='color:#2563eb'>OS</span></h1>", unsafe_allow_html=True)
            st.markdown("<p style='color:#6b7280; margin-bottom: 20px;'>Enterprise Management System</p>", unsafe_allow_html=True)
            
            u = st.text_input("Username", placeholder="admin")
            p = st.text_input("Password", type="password", placeholder="admin123")
            
            if st.button("Sign In Securely", type="primary"):
                if u == "admin" and p == "admin123":
                    st.session_state.user = "admin"
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
            
            st.markdown('</div>', unsafe_allow_html=True)

# ================= 4. APPLICATION MODULES =================

# --- DASHBOARD ---
def render_dashboard():
    st.title("📊 Dashboard")
    
    db = st.session_state.db
    
    # Calculate Stats
    total_sales = sum(s['total'] for s in db['sales'])
    today_orders = len(db['sales'])
    active_tables = len([t for t in db['tables'] if t['status'] == 'Occupied'])
    menu_count = len(db['menu'])
    
    # 4 Cards Layout
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", peso(total_sales), "All Time")
    c2.metric("Total Orders", today_orders, "Today")
    c3.metric("Live Tables", active_tables, f"of {len(db['tables'])}")
    c4.metric("Menu Items", menu_count)
    
    st.write("") # Spacer
    
    # Charts & Table
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Recent Sales Trend")
        if db['sales']:
            df = pd.DataFrame(db['sales'])
            df['time'] = pd.to_datetime(df['time'])
            chart_data = df.groupby(df['time'].dt.hour)['total'].sum()
            st.bar_chart(chart_data, color="#2563eb")
        else:
            st.info("No sales data available yet.")
            
    with col_right:
        st.subheader("Top Categories")
        if db['sales']:
            # Flatten all items sold
            all_sold = []
            for s in db['sales']:
                all_sold.extend(s['items'])
            cat_df = pd.DataFrame(all_sold)
            if not cat_df.empty:
                st.dataframe(cat_df['cat'].value_counts(), use_container_width=True)
            else:
                st.caption("No item details.")
        else:
            st.caption("No data.")

# --- POS SYSTEM (SPLIT SCREEN) ---
def render_pos():
    # Header
    c_head1, c_head2 = st.columns([3, 1])
    c_head1.title("🏪 Point of Sale")
    
    # Filters
    cats = ["All"] + sorted(list(set(i['cat'] for i in st.session_state.db['menu'])))
    selected_cat = c_head2.selectbox("Filter Category", cats)

    # Main Layout
    # On Laptop: Menu (2/3) | Cart (1/3)
    # On Mobile: Menu (Full) -> Cart (Full)
    col_menu, col_cart = st.columns([0.65, 0.35], gap="large")
    
    # --- MENU GRID ---
    with col_menu:
        items = st.session_state.db['menu']
        if selected_cat != "All":
            items = [i for i in items if i['cat'] == selected_cat]
        
        # Responsive Grid: 3 items per row
        row_size = 3
        chunks = [items[i:i + row_size] for i in range(0, len(items), row_size)]
        
        for chunk in chunks:
            cols = st.columns(row_size)
            for idx, item in enumerate(chunk):
                with cols[idx]:
                    with st.container():
                        # HTML for Card Look
                        st.markdown(f"""
                        <div class="menu-card-header">
                            <span class="menu-img">{item['icon']}</span>
                            <div class="menu-title">{item['name']}</div>
                            <div class="menu-price">{peso(item['price'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add Button
                        if st.button("Add to Cart", key=f"add_{item['id']}", type="secondary"):
                            sid = str(item['id'])
                            if sid in st.session_state.cart:
                                st.session_state.cart[sid] += 1
                            else:
                                st.session_state.cart[sid] = 1
                            st.toast(f"Added {item['name']}", icon="🛒")

    # --- CART SECTION ---
    with col_cart:
        st.markdown("### 🛒 Current Order")
        
        if not st.session_state.cart:
            st.info("Cart is empty.")
        else:
            cart_total = 0
            order_items = []
            
            # Display Items
            for sid, qty in list(st.session_state.cart.items()):
                item = next((i for i in st.session_state.db['menu'] if str(i['id']) == sid), None)
                if item:
                    line_total = item['price'] * qty
                    cart_total += line_total
                    order_items.append({**item, "qty": qty})
                    
                    with st.container():
                        c1, c2, c3 = st.columns([2, 1, 0.5])
                        c1.markdown(f"**{item['name']}**")
                        c1.caption(f"{qty} x {peso(item['price'])}")
                        c2.markdown(f"**{peso(line_total)}**")
                        if c3.button("🗑️", key=f"del_{sid}"):
                            del st.session_state.cart[sid]
                            st.rerun()
            
            st.divider()
            
            # Summary
            tax = cart_total * 0.12
            total = cart_total
            
            c_sub1, c_sub2 = st.columns(2)
            c_sub1.text("Subtotal")
            c_sub2.text(peso(total - tax))
            
            c_vat1, c_vat2 = st.columns(2)
            c_vat1.text("VAT (12%)")
            c_vat2.text(peso(tax))
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin-top:10px; font-weight:bold; font-size:1.2rem;">
                <span>Total</span>
                <span style="color:#2563eb;">{peso(total)}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            
            if st.button("✨ Checkout & Print", type="primary", use_container_width=True):
                process_checkout(order_items, total)

# --- CHECKOUT RECEIPT MODAL ---
@st.dialog("🧾 Official Receipt")
def receipt_modal(order):
    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
    st.markdown("### GourmetOS PH")
    st.caption("Enterprise System • Philippines")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown(f"**Order ID:** #{order['id']}")
    st.markdown(f"**Date:** {order['time']}")
    
    st.divider()
    
    for item in order['items']:
        c1, c2 = st.columns([3, 1])
        c1.write(f"{item['qty']}x {item['name']}")
        c2.write(f"{peso(item['price'] * item['qty'])}")
        
    st.divider()
    
    st.markdown(f"<h3 style='text-align:right'>{peso(order['total'])}</h3>", unsafe_allow_html=True)
    
    st.divider()
    st.success("Payment Successful!")
    if st.button("Close Receipt"):
        st.rerun()

def process_checkout(items, total):
    new_order = {
        "id": int(time.time()),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "items": items,
        "total": total,
        "status": "Cooking"
    }
    
    st.session_state.db['sales'].append(new_order)
    st.session_state.db['orders'].append(new_order) # Active kitchen
    save_db(st.session_state.db)
    st.session_state.cart = {} # Clear cart
    
    receipt_modal(new_order)

# --- KITCHEN DISPLAY ---
def render_kitchen():
    st.title("👨‍🍳 Kitchen Display System")
    
    orders = st.session_state.db['orders']
    
    if not orders:
        st.container().success("Kitchen is clear! No pending orders.")
        return

    # Responsive Grid for Orders
    cols = st.columns(3) # 3 Cards per row
    
    for idx, order in enumerate(orders):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"#### Order #{str(order['id'])[-4:]}")
                st.caption(f"🕒 {order['time']}")
                st.divider()
                
                for item in order['items']:
                    st.markdown(f"- **{item['qty']}x** {item['name']}")
                
                st.write("")
                if st.button("✅ Mark Ready", key=f"k_{order['id']}", type="primary"):
                    st.session_state.db['orders'] = [o for o in st.session_state.db['orders'] if o['id'] != order['id']]
                    save_db(st.session_state.db)
                    st.rerun()

# --- RESERVATIONS ---
def render_reservations():
    st.title("📅 Reservations")
    
    col_form, col_list = st.columns([1, 2])
    
    with col_form:
        st.subheader("New Booking")
        with st.container():
            with st.form("res_form"):
                name = st.text_input("Name")
                date = st.date_input("Date")
                time_val = st.time_input("Time")
                pax = st.number_input("Guests", 1, 20, 2)
                
                if st.form_submit_button("Book Table", type="primary"):
                    new_res = {
                        "id": int(time.time()),
                        "name": name,
                        "time": f"{date} {time_val}",
                        "pax": pax
                    }
                    st.session_state.db['reservations'].append(new_res)
                    save_db(st.session_state.db)
                    st.success("Booked!")
                    st.rerun()

    with col_list:
        st.subheader("Upcoming List")
        if st.session_state.db['reservations']:
            df = pd.DataFrame(st.session_state.db['reservations'])
            st.dataframe(df, use_container_width=True)
            
            # Simple Cancel
            to_cancel = st.selectbox("Select to Cancel", [r['name'] for r in st.session_state.db['reservations']])
            if st.button("Cancel Reservation"):
                st.session_state.db['reservations'] = [r for r in st.session_state.db['reservations'] if r['name'] != to_cancel]
                save_db(st.session_state.db)
                st.rerun()
        else:
            st.info("No reservations.")

# --- MANAGEMENT ---
def render_management():
    st.title("⚙️ Management")
    
    tabs = st.tabs(["🍔 Menu", "👥 Staff", "🪑 Tables"])
    
    # Menu Tab
    with tabs[0]:
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.form("add_menu"):
                st.subheader("Add Item")
                name = st.text_input("Name")
                cat = st.selectbox("Category", ["Main", "Burger", "Drink", "Dessert", "Sides"])
                price = st.number_input("Price", 1.0)
                icon = st.text_input("Icon (Emoji)", "🍽️")
                if st.form_submit_button("Save"):
                    new_item = {"id": int(time.time()), "name": name, "cat": cat, "price": price, "icon": icon}
                    st.session_state.db['menu'].append(new_item)
                    save_db(st.session_state.db)
                    st.rerun()
        
        with c2:
            st.dataframe(pd.DataFrame(st.session_state.db['menu']), use_container_width=True)

    # Staff Tab
    with tabs[1]:
        st.dataframe(pd.DataFrame(st.session_state.db['staff']), use_container_width=True)
        
    # Tables Tab
    with tabs[2]:
        tables = st.session_state.db['tables']
        cols = st.columns(4)
        for idx, t in enumerate(tables):
            with cols[idx % 4]:
                with st.container():
                    status_color = "#22c55e" if t['status'] == 'Free' else "#ef4444"
                    st.markdown(f"<h3 style='text-align:center; color:{status_color}'>Table {t['id']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center'><b>{t['status']}</b></div>", unsafe_allow_html=True)
                    if st.button("Toggle", key=f"tbl_{t['id']}"):
                        t['status'] = "Occupied" if t['status'] == "Free" else "Free"
                        save_db(st.session_state.db)
                        st.rerun()

# ================= 5. MAIN ROUTER =================
if not st.session_state.user:
    login()
else:
    # Sidebar Navigation
    with st.sidebar:
        st.title("GourmetOS")
        st.markdown(f"Hello, **{st.session_state.user}**")
        
        nav = st.radio(
            "Navigate", 
            ["Dashboard", "Point of Sale", "Kitchen", "Reservations", "Management"],
            label_visibility="collapsed"
        )
        
        st.write("---")
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()

    # Route
    if nav == "Dashboard": render_dashboard()
    elif nav == "Point of Sale": render_pos()
    elif nav == "Kitchen": render_kitchen()
    elif nav == "Reservations": render_reservations()
    elif nav == "Management": render_management()