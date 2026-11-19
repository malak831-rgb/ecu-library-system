import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- 1. إعداد الصفحة والتصميم العام ---
st.set_page_config(
    page_title="ECU Smart Library System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحسين المظهر البصري بـ CSS مخصص
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.1rem;
    }
    .main-header p {
        color: #e0e8f5;
        margin: 5px 0 0 0;
        font-size: 0.95rem;
    }
    .member-card {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
        padding: 18px;
        border-radius: 12px;
        border-left: 6px solid #00d2ff;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. إعداد قاعدة البيانات (SQLite) ---
conn = sqlite3.connect("library_pro.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS books (
                    copy_id TEXT PRIMARY KEY,
                    isbn TEXT,
                    title TEXT,
                    author TEXT,
                    category TEXT,
                    shelf_location TEXT,
                    status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS members (
                    member_id TEXT PRIMARY KEY,
                    full_name TEXT,
                    national_id TEXT UNIQUE,
                    phone TEXT,
                    email TEXT,
                    join_date TEXT,
                    status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT,
                    copy_id TEXT,
                    borrow_date TEXT,
                    due_date TEXT,
                    return_date TEXT,
                    fine_amount REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
                    res_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    copy_id TEXT,
                    patron_name TEXT,
                    patron_contact TEXT,
                    res_date TEXT)''')
    conn.commit()

    c.execute("SELECT COUNT(*) FROM books")
    if c.fetchone()[0] == 0:
        sample_books = [
            ("B001", "978-0132350884", "Clean Code", "Robert C. Martin", "Software Engineering", "Shelf A-1", "Available"),
            ("B002", "978-1118057629", "Systems Analysis and Design", "Alan Dennis", "Information Systems", "Shelf B-2", "Available"),
            ("B003", "978-0262033848", "Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", "Shelf C-1", "Borrowed"),
            ("B004", "978-0131103627", "The C Programming Language", "Brian Kernighan", "Programming", "Shelf A-3", "Available"),
            ("B005", "978-0134685991", "Effective C++", "Scott Meyers", "Programming", "Shelf A-4", "Available"),
            ("B006", "978-0201633610", "Design Patterns", "Erich Gamma", "Software Engineering", "Shelf B-1", "Borrowed"),
        ]
        c.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)", sample_books)

        sample_members = [
            ("M101", "Malak Abodef Omar", "3060901001", "01001660931", "malak@ecu.edu.eg", "2026-10-01", "Active"),
            ("M102", "Asmaa Mohamed", "3060501002", "01000000002", "asmaa@ecu.edu.eg", "2026-10-05", "Active"),
            ("M103", "Habiba Ahmed", "3060701003", "01000000003", "habiba@ecu.edu.eg", "2026-10-12", "Active"),
        ]
        c.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?, ?, ?)", sample_members)

        # معاملات تجريبية (واحدة متأخرة 4 أيام وواحدة متأخرة يومين)
        past_borrow_1 = (datetime.now() - timedelta(days=18)).strftime("%Y-%m-%d")
        past_due_1 = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
        past_borrow_2 = (datetime.now() - timedelta(days=16)).strftime("%Y-%m-%d")
        past_due_2 = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

        c.execute("INSERT INTO transactions (member_id, copy_id, borrow_date, due_date) VALUES (?, ?, ?, ?)",
                  ("M102", "B003", past_borrow_1, past_due_1))
        c.execute("INSERT INTO transactions (member_id, copy_id, borrow_date, due_date) VALUES (?, ?, ?, ?)",
                  ("M103", "B006", past_borrow_2, past_due_2))
        conn.commit()

init_db()

# --- 3. إدارة الجلسة (Session State) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.staff_role = ""
    st.session_state.staff_name = ""

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("## 🏛️ Public Library Portal")
    st.caption("INF 2101 • System Analysis & Design")
    st.divider()

    if not st.session_state.logged_in:
        st.subheader("🔐 Staff Authentication")
        username = st.text_input("Username", placeholder="librarian or admin")
        password = st.text_input("Password", type="password", placeholder="1234")
        if st.button("Sign In", type="primary", use_container_width=True):
            if username == "librarian" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.staff_role = "Desk Librarian"
                st.session_state.staff_name = "Staff #01"
                st.rerun()
            elif username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.staff_role = "Administrative Coordinator"
                st.session_state.staff_name = "Admin #01"
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        st.info("💡 **Demo Accounts:**\n- `librarian` / `1234`\n- `admin` / `1234`")
    else:
        st.success(f"🟢 **Active Session**\n\n**Role:** {st.session_state.staff_role}")
        st.divider()
        # محاكاة System Clock للكتب المتأخرة
        today_str = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) FROM transactions WHERE return_date IS NULL AND due_date < ?", (today_str,))
        overdue_count = c.fetchone()[0]
        if overdue_count > 0:
            st.error(f"⏰ **System Clock Alert:**\n{overdue_count} book(s) are currently OVERDUE!")
        else:
            st.info("✅ **System Clock:** All active loans are on schedule.")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.staff_role = ""
            st.rerun()

# --- 5. الهيدر الرئيسي وشريط المؤشرات (KPIs) ---
st.markdown("""
<div class="main-header">
    <h1>🏛️ Smart Library Management System</h1>
    <p>Integrated Circulation, Catalog Search & Automated Fine Tracking Prototype</p>
</div>
""", unsafe_allow_html=True)

# حساب المؤشرات الحية من قاعدة البيانات
c.execute("SELECT COUNT(*) FROM books")
total_books = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM books WHERE status = 'Available'")
avail_books = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM books WHERE status = 'Borrowed'")
borrowed_books = c.fetchone()[0]
c.execute("SELECT COALESCE(SUM(fine_amount), 0) FROM transactions")
total_fines = c.fetchone()[0]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("📚 Total Catalog Copies", total_books)
kpi2.metric("✅ Available Now", avail_books)
kpi3.metric("📖 Currently Borrowed", borrowed_books)
kpi4.metric("💰 Collected Fines", f"${total_fines:.2f}")

st.divider()

# --- 6. التبويبات الرئيسية ---
if not st.session_state.logged_in:
    tabs = st.tabs(["🔍 Online Book Search & Reserve (FR-01)"])
else:
    tabs = st.tabs([
        "🔍 Catalog Search (FR-01)",
        "👤 Member Registration (FR-02)",
        "🔄 Borrow & Return (FR-03 & FR-04)",
        "📊 Analytics & Database Reports"
    ])

# === TAB 1: البحث في الفهرس وحجز الكتب المستعارة ===
with tabs[0]:
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input("🔎 Search by Title, Author, or ISBN:", placeholder="e.g., Clean Code, Alan Dennis, 978-...")
    with col_s2:
        status_filter = st.selectbox("Filter by Status:", ["All", "Available", "Borrowed"])

    query = "SELECT copy_id, isbn, title, author, category, shelf_location, status FROM books WHERE 1=1"
    params = []
    if search_query:
        query += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
        q = f"%{search_query}%"
        params.extend([q, q, q])
    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    c.execute(query, params)
    books_data = c.fetchall()

    if books_data:
        df_books = pd.DataFrame(books_data, columns=["Copy ID", "ISBN", "Title", "Author", "Category", "Shelf", "Status"])
        st.dataframe(df_books, use_container_width=True, hide_index=True)
    else:
        st.warning("No matching books found in the catalog.")

    # ميزة حجز كتاب مستعار (Extend Use Case)
    with st.expander("📌 Reserve a Borrowed Book (Hold Request)"):
        c.execute("SELECT copy_id, title FROM books WHERE status = 'Borrowed'")
        borrowed_list = c.fetchall()
        if not borrowed_list:
            st.info("All books are currently available for immediate borrowing!")
        else:
            r_col1, r_col2, r_col3 = st.columns(3)
            with r_col1:
                selected_book = st.selectbox("Select Borrowed Book:", [f"{b[0]} - {b[1]}" for b in borrowed_list])
            with r_col2:
                patron_name = st.text_input("Your Full Name")
            with r_col3:
                patron_contact = st.text_input("Phone or Email")
            if st.button("Place Reservation"):
                if patron_name and patron_contact:
                    b_id = selected_book.split(" - ")[0]
                    c.execute("INSERT INTO reservations (copy_id, patron_name, patron_contact, res_date) VALUES (?, ?, ?, ?)",
                              (b_id, patron_name, patron_contact, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    st.success(f"✅ Hold placed on **{selected_book}**. We will notify you once returned!")
                else:
                    st.error("Please enter your name and contact details.")

# === باقي التبويبات للموظفين فقط ===
if st.session_state.logged_in:

    # === TAB 2: تسجيل عضو جديد ===
    with tabs[1]:
        col_form, col_card = st.columns([1.4, 1])
        with col_form:
            st.subheader("Register New Library Member")
            with st.form("register_member_form", clear_on_submit=True):
                full_name = st.text_input("Full Name *")
                national_id = st.text_input("National / University ID *")
                phone = st.text_input("Phone Number *")
                email = st.text_input("Email Address *")
                submitted = st.form_submit_button("✅ Generate Membership", type="primary")

                if submitted:
                    if not (full_name and national_id and phone and email):
                        st.error("All fields marked with * are required.")
                    else:
                        c.execute("SELECT * FROM members WHERE national_id = ?", (national_id,))
                        if c.fetchone():
                            st.error("⚠️ A member with this National/University ID already exists!")
                        else:
                            c.execute("SELECT COUNT(*) FROM members")
                            new_id = f"M{101 + c.fetchone()[0]}"
                            join_dt = datetime.now().strftime("%Y-%m-%d")
                            c.execute("INSERT INTO members VALUES (?, ?, ?, ?, ?, ?, ?)",
                                      (new_id, full_name, national_id, phone, email, join_dt, "Active"))
                            conn.commit()
                            st.session_state.last_member = (new_id, full_name, national_id, join_dt)
                            st.success(f"Member registered successfully! ID: **{new_id}**")

        with col_card:
            st.subheader("Digital Library Card Preview")
            card_data = st.session_state.get("last_member", ("M101", "Malak Abodef Omar", "3060901001", "2026-10-01"))
            st.markdown(f"""
            <div class="member-card">
                <h4 style="margin:0; color:#00d2ff;">🏛️ PUBLIC LIBRARY MEMBER PASS</h4>
                <hr style="border-color: rgba(255,255,255,0.2);">
                <p style="margin:4px 0;"><b>Member ID:</b> {card_data[0]}</p>
                <p style="margin:4px 0;"><b>Name:</b> {card_data[1]}</p>
                <p style="margin:4px 0;"><b>National ID:</b> {card_data[2]}</p>
                <p style="margin:4px 0;"><b>Issued Date:</b> {card_data[3]} • <b>Status:</b> ACTIVE</p>
            </div>
            """, unsafe_allow_html=True)

    # === TAB 3: الاستعارة والإرجاع وحساب الغرامات ===
    with tabs[2]:
        col_b, col_r = st.columns(2)

        with col_b:
            st.subheader("📤 Issue Book (Borrowing)")
            c.execute("SELECT member_id, full_name FROM members WHERE status = 'Active'")
            active_members = c.fetchall()
            c.execute("SELECT copy_id, title FROM books WHERE status = 'Available'")
            avail_list = c.fetchall()

            if not avail_list:
                st.warning("No available books to borrow right now.")
            else:
                sel_member = st.selectbox("Select Active Member:", [f"{m[0]} - {m[1]}" for m in active_members])
                sel_copy = st.selectbox("Select Available Book:", [f"{b[0]} - {b[1]}" for b in avail_list])
                loan_days = st.slider("Loan Duration (Days):", min_value=7, max_value=21, value=14)

                if st.button("Confirm Checkout", type="primary", use_container_width=True):
                    m_id = sel_member.split(" - ")[0]
                    b_id = sel_copy.split(" - ")[0]
                    c.execute("SELECT COUNT(*) FROM transactions WHERE member_id = ? AND return_date IS NULL", (m_id,))
                    if c.fetchone()[0] >= 3:
                        st.error("❌ Borrowing Limit Reached: Member already has 3 active books.")
                    else:
                        today = datetime.now().strftime("%Y-%m-%d")
                        due = (datetime.now() + timedelta(days=loan_days)).strftime("%Y-%m-%d")
                        c.execute("INSERT INTO transactions (member_id, copy_id, borrow_date, due_date) VALUES (?, ?, ?, ?)",
                                  (m_id, b_id, today, due))
                        c.execute("UPDATE books SET status = 'Borrowed' WHERE copy_id = ?", (b_id,))
                        conn.commit()
                        st.success(f"✅ Checkout Complete! Due Date: **{due}**")
                        st.rerun()

        with col_r:
            st.subheader("📥 Return Book & Fine Calculator")
            c.execute("""SELECT t.copy_id, b.title, t.member_id, t.due_date 
                         FROM transactions t JOIN books b ON t.copy_id = b.copy_id 
                         WHERE t.return_date IS NULL""")
            active_loans = c.fetchall()

            if not active_loans:
                st.info("No active borrowed books pending return.")
            else:
                loan_options = [f"{l[0]} - {l[1]} (Member: {l[2]} | Due: {l[3]})" for l in active_loans]
                sel_return = st.selectbox("Select Active Loan to Return:", loan_options)
                daily_rate = st.number_input("Daily Overdue Fine Rate ($):", min_value=1.0, max_value=20.0, value=5.0, step=1.0)

                if st.button("Process Return & Calculate Fine", type="primary", use_container_width=True):
                    r_copy_id = sel_return.split(" - ")[0]
                    c.execute("SELECT trans_id, due_date FROM transactions WHERE copy_id = ? AND return_date IS NULL", (r_copy_id,))
                    trans_id, due_str = c.fetchone()

                    due_date = datetime.strptime(due_str, "%Y-%m-%d")
                    today_date = datetime.now()
                    late_days = (today_date - due_date).days
                    fine = max(0.0, late_days * daily_rate)

                    c.execute("UPDATE transactions SET return_date = ?, fine_amount = ? WHERE trans_id = ?",
                              (today_date.strftime("%Y-%m-%d"), fine, trans_id))
                    c.execute("UPDATE books SET status = 'Available' WHERE copy_id = ?", (r_copy_id,))
                    conn.commit()

                    if fine > 0:
                        st.warning(f"⚠️ Returned **{late_days} day(s) late**! Collect Fine: **${fine:.2f}**")
                    else:
                        st.success("✅ Returned on time! No fine required ($0.00).")
                    st.rerun()

    # === TAB 4: التحليلات والتقارير ===
    with tabs[3]:
        st.subheader("📈 Library Circulation Analytics")
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("**Books by Category**")
            c.execute("SELECT category, COUNT(*) as count FROM books GROUP BY category")
            cat_df = pd.DataFrame(c.fetchall(), columns=["Category", "Count"]).set_index("Category")
            st.bar_chart(cat_df)
        with ch2:
            st.markdown("**Inventory Availability Status**")
            c.execute("SELECT status, COUNT(*) as count FROM books GROUP BY status")
            stat_df = pd.DataFrame(c.fetchall(), columns=["Status", "Count"]).set_index("Status")
            st.bar_chart(stat_df)

        st.divider()
        st.subheader("🗂️ Complete Database Records & CSV Export")

        c.execute("SELECT * FROM transactions")
        trans_df = pd.DataFrame(c.fetchall(), columns=["Trans ID", "Member ID", "Copy ID", "Borrow Date", "Due Date", "Return Date", "Fine ($)"])
        st.dataframe(trans_df, use_container_width=True, hide_index=True)

        csv_data = trans_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Transactions Report (CSV / Excel)",
            data=csv_data,
            file_name="library_transactions_report.csv",
            mime="text/csv"
        )