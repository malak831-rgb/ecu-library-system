import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- 1. إعداد الصفحة ---
st.set_page_config(
    page_title="ECU Smart Library System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. قاموس اللغات (عربي / إنجليزي) ---
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
if "day_offset" not in st.session_state:
    st.session_state.day_offset = 0

TEXT = {
    "EN": {
        "dir": "ltr",
        "align": "left",
        "title": "🏛️ Smart Library Management System",
        "subtitle": "Integrated Circulation, Catalog Search & Automated Fine Tracking Prototype",
        "portal": "🏛️ Public Library Portal",
        "course": "INF 2101 • System Analysis & Design",
        "lang_label": "🌐 Language / اللغة",
        "login_hdr": "🔐 Staff Authentication",
        "user": "Username",
        "pass": "Password",
        "signin": "Sign In",
        "logout": "🚪 Logout",
        "active_sess": "🟢 Active Session",
        "role": "Role",
        "clock_title": "⏰ System Clock Simulator",
        "clock_btn": "⏩ Advance +10 Days (Demo)",
        "clock_reset": "🔄 Reset Date",
        "overdue_alert": "book(s) are currently OVERDUE!",
        "ontime_alert": "✅ System Clock: All active loans are on schedule.",
        "kpi1": "📚 Total Catalog Copies",
        "kpi2": "✅ Available Now",
        "kpi3": "📖 Currently Borrowed",
        "kpi4": "💰 Collected Fines",
        "tab_search": "🔍 Online Book Search (FR-01)",
        "tab_reg": "👤 Member Registration (FR-02)",
        "tab_circ": "🔄 Borrow, Renew & Return (FR-03/04)",
        "tab_rep": "📊 Analytics & Reports",
        "tab_admin": "⚙️ Admin: Catalog & Borrowers",
        "search_lbl": "🔎 Search by Title, Author, or ISBN:",
        "filter_lbl": "Filter by Status:",
        "res_exp": "📌 Reserve a Borrowed Book (Hold Request)",
        "res_btn": "Place Reservation",
        "reg_hdr": "Register New Library Member",
        "card_hdr": "Digital Library Card & QR Pass",
        "issue_hdr": "📤 Issue Book (Borrowing)",
        "return_hdr": "📥 Return / Renew Book",
        "checkout_btn": "Confirm Checkout",
        "return_btn": "Process Return & Calculate Fine",
        "renew_btn": "🔄 Renew Loan (+7 Days)",
        "csv_btn": "⬇️ Download Transactions Report (CSV)",
        "add_book_hdr": "➕ Add New Book to Catalog",
        "del_book_hdr": "🗑️ Remove Damaged / Lost Copy",
        "borrowers_hdr": "🔒 Confidential: Active & Past Borrowers Log (Admin Only)"
    },
    "AR": {
        "dir": "rtl",
        "align": "right",
        "title": "🏛️ نظام إدارة المكتبة الذكي",
        "subtitle": "نموذج متكامل للبحث في الفهرس، الإعارة، وحساب الغرامات تلقائياً",
        "portal": "🏛️ بوابة المكتبة العامة",
        "course": "INF 2101 • تحليل وتصميم النظم",
        "lang_label": "🌐 اللغة / Language",
        "login_hdr": "🔐 تسجيل دخول الموظفين",
        "user": "اسم المستخدم",
        "pass": "كلمة المرور",
        "signin": "تسجيل الدخول",
        "logout": "🚪 تسجيل الخروج",
        "active_sess": "🟢 جلسة نشطة",
        "role": "الصلاحية",
        "clock_title": "⏰ محاكي ساعة النظام (للمناقشة)",
        "clock_btn": "⏩ تقديم التاريخ +10 أيام",
        "clock_reset": "🔄 إعادة ضبط التاريخ",
        "overdue_alert": "كتاب/كتب متأخرة عن موعد التسليم!",
        "ontime_alert": "✅ ساعة النظام: جميع الاستعارات في موعدها.",
        "kpi1": "📚 إجمالي نسخ الكتب",
        "kpi2": "✅ الكتب المتاحة حالياً",
        "kpi3": "📖 الكتب المستعارة",
        "kpi4": "💰 إجمالي الغرامات",
        "tab_search": "🔍 البحث في الفهرس (FR-01)",
        "tab_reg": "👤 تسجيل الأعضاء (FR-02)",
        "tab_circ": "🔄 الإعارة والتجديد والإرجاع (FR-03/04)",
        "tab_rep": "📊 التحليلات والتقارير",
        "tab_admin": "⚙️ الإدارة: الفهرس وبيانات المستعيرين",
        "search_lbl": "🔎 ابحث بعنوان الكتاب، المؤلف، أو الرقم الدولي (ISBN):",
        "filter_lbl": "تصفية حسب الحالة:",
        "res_exp": "📌 حجز كتاب مستعار (قائمة الانتظار)",
        "res_btn": "تأكيد الحجز",
        "reg_hdr": "تسجيل عضو جديد بالمكتبة",
        "card_hdr": "بطاقة العضوية الرقمية ورمز QR",
        "issue_hdr": "📤 إعارة كتاب لعضو",
        "return_hdr": "📥 إرجاع أو تجديد استعارة كتاب",
        "checkout_btn": "تأكيد عملية الإعارة",
        "return_btn": "إتمام الإرجاع وحساب الغرامة",
        "renew_btn": "🔄 تجديد الاستعارة (+7 أيام)",
        "csv_btn": "⬇️ تحميل تقرير المعاملات (Excel / CSV)",
        "add_book_hdr": "➕ إضافة كتاب جديد للفهرس",
        "del_book_hdr": "🗑️ حذف نسخة تالفة أو مفقودة",
        "borrowers_hdr": "🔒 سجل بيانات الأعضاء المستعيرين (خاص بالمنسق الإداري فقط)"
    }
}

T = TEXT[st.session_state.lang]

def get_now():
    return datetime.now() + timedelta(days=st.session_state.day_offset)

# تنسيق CSS يدعم الاتجاهين (RTL / LTR)
st.markdown(f"""
<style>
    .main .block-container {{
        direction: {T['dir']};
        text-align: {T['align']};
    }}
    .main-header {{
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        direction: {T['dir']};
        text-align: {T['align']};
    }}
    .main-header h1 {{
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }}
    .main-header p {{
        color: #e0e8f5;
        margin: 5px 0 0 0;
        font-size: 0.95rem;
    }}
    .member-card {{
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
        padding: 18px;
        border-radius: 12px;
        border-left: 6px solid #00d2ff;
        margin-top: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. إعداد قاعدة البيانات الجديدة بأسماء أجنبية وهمية ---
conn = sqlite3.connect("library_v3.db", check_same_thread=False)
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

        # أسماء وهمية أجنبية بالكامل
        sample_members = [
            ("M101", "Liam Carter", "ID-8840192", "+1-202-555-0143", "liam.carter@example.com", "2026-10-01", "Active"),
            ("M102", "Emma Watson", "ID-8840193", "+1-202-555-0188", "emma.watson@example.com", "2026-10-05", "Active"),
            ("M103", "Noah Bennett", "ID-8840194", "+1-202-555-0192", "noah.bennett@example.com", "2026-10-12", "Active"),
            ("M104", "Sophia Reed", "ID-8840195", "+1-202-555-0117", "sophia.reed@example.com", "2026-10-15", "Active"),
        ]
        c.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?, ?, ?)", sample_members)

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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.staff_role = ""

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    lang_choice = st.radio(T["lang_label"], ["English", "العربية"], horizontal=True, index=0 if st.session_state.lang == "EN" else 1)
    new_lang = "EN" if lang_choice == "English" else "AR"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.divider()
    st.markdown(f"## {T['portal']}")
    st.caption(T["course"])
    st.divider()

    if not st.session_state.logged_in:
        st.subheader(T["login_hdr"])
        username = st.text_input(T["user"], placeholder="librarian or admin")
        password = st.text_input(T["pass"], type="password", placeholder="1234")
        if st.button(T["signin"], type="primary", use_container_width=True):
            if username == "librarian" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.staff_role = "Desk Librarian"
                st.rerun()
            elif username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.staff_role = "Administrative Coordinator"
                st.rerun()
            else:
                st.error("❌ Invalid credentials / بيانات غير صحيحة")
        st.info("💡 **Demo Accounts:**\n- `librarian` / `1234`\n- `admin` / `1234`")
    else:
        st.success(f"**{T['active_sess']}**\n\n**{T['role']}:** {st.session_state.staff_role}")
        st.divider()

        st.markdown(f"**{T['clock_title']}**")
        st.caption(f"📅 Simulated Date: **{get_now().strftime('%Y-%m-%d')}**")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button(T["clock_btn"], use_container_width=True):
                st.session_state.day_offset += 10
                st.rerun()
        with col_c2:
            if st.button(T["clock_reset"], use_container_width=True):
                st.session_state.day_offset = 0
                st.rerun()

        today_str = get_now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) FROM transactions WHERE return_date IS NULL AND due_date < ?", (today_str,))
        overdue_count = c.fetchone()[0]
        if overdue_count > 0:
            st.error(f"🚨 **{overdue_count}** {T['overdue_alert']}")
        else:
            st.info(T["ontime_alert"])

        st.divider()
        if st.button(T["logout"], use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.staff_role = ""
            st.rerun()

# --- 5. الهيدر ومؤشرات الأداء (KPIs) ---
st.markdown(f"""
<div class="main-header">
    <h1>{T['title']}</h1>
    <p>{T['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

c.execute("SELECT COUNT(*) FROM books")
total_books = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM books WHERE status = 'Available'")
avail_books = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM books WHERE status = 'Borrowed'")
borrowed_books = c.fetchone()[0]
c.execute("SELECT COALESCE(SUM(fine_amount), 0) FROM transactions")
total_fines = c.fetchone()[0]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(T["kpi1"], total_books)
kpi2.metric(T["kpi2"], avail_books)
kpi3.metric(T["kpi3"], borrowed_books)
kpi4.metric(T["kpi4"], f"${total_fines:.2f}")

st.divider()

# --- 6. التبويبات حسب الصلاحيات ---
if not st.session_state.logged_in:
    tabs = st.tabs([T["tab_search"]])
elif st.session_state.staff_role == "Administrative Coordinator":
    tabs = st.tabs([T["tab_search"], T["tab_reg"], T["tab_circ"], T["tab_rep"], T["tab_admin"]])
else:
    tabs = st.tabs([T["tab_search"], T["tab_reg"], T["tab_circ"], T["tab_rep"]])

# === TAB 1: البحث والحجز ===
with tabs[0]:
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input(T["search_lbl"], placeholder="Clean Code, Alan Dennis, 978-...")
    with col_s2:
        status_filter = st.selectbox(T["filter_lbl"], ["All", "Available", "Borrowed"])

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
        st.warning("No matching books found / لا توجد نتائج مطابقة")

    with st.expander(T["res_exp"]):
        c.execute("SELECT copy_id, title FROM books WHERE status = 'Borrowed'")
        borrowed_list = c.fetchall()
        if not borrowed_list:
            st.info("All books are currently available / جميع الكتب متاحة حالياً")
        else:
            r_col1, r_col2, r_col3 = st.columns(3)
            with r_col1:
                selected_book = st.selectbox("Book / الكتاب:", [f"{b[0]} - {b[1]}" for b in borrowed_list])
            with r_col2:
                patron_name = st.text_input("Name / الاسم")
            with r_col3:
                patron_contact = st.text_input("Phone or Email / الهاتف أو البريد")
            if st.button(T["res_btn"]):
                if patron_name and patron_contact:
                    b_id = selected_book.split(" - ")[0]
                    c.execute("INSERT INTO reservations (copy_id, patron_name, patron_contact, res_date) VALUES (?, ?, ?, ?)",
                              (b_id, patron_name, patron_contact, get_now().strftime("%Y-%m-%d")))
                    conn.commit()
                    st.success(f"✅ Hold placed on **{selected_book}**!")
                else:
                    st.error("Please fill all fields / يرجى إدخال جميع البيانات")

# === التبويبات الداخلية للموظفين ===
if st.session_state.logged_in:

    # === TAB 2: تسجيل عضو + QR Code ===
    with tabs[1]:
        col_form, col_card = st.columns([1.4, 1])
        with col_form:
            st.subheader(T["reg_hdr"])
            with st.form("register_member_form", clear_on_submit=True):
                full_name = st.text_input("Full Name / الاسم الكامل *")
                national_id = st.text_input("National / University ID / الرقم القومي أو الجامعي *")
                phone = st.text_input("Phone / رقم الهاتف *")
                email = st.text_input("Email / البريد الإلكتروني *")
                submitted = st.form_submit_button("✅ Generate Membership / إصدار العضوية", type="primary")

                if submitted:
                    if not (full_name and national_id and phone and email):
                        st.error("All fields are required / جميع الحقول مطلوبة")
                    else:
                        c.execute("SELECT * FROM members WHERE national_id = ?", (national_id,))
                        if c.fetchone():
                            st.error("⚠️ Member already exists / هذا الرقم مسجل بالفعل")
                        else:
                            c.execute("SELECT COUNT(*) FROM members")
                            new_id = f"M{101 + c.fetchone()[0]}"
                            join_dt = get_now().strftime("%Y-%m-%d")
                            c.execute("INSERT INTO members VALUES (?, ?, ?, ?, ?, ?, ?)",
                                      (new_id, full_name, national_id, phone, email, join_dt, "Active"))
                            conn.commit()
                            st.session_state.last_member = (new_id, full_name, national_id, join_dt)
                            st.success(f"✅ Member Registered! ID: **{new_id}**")

        with col_card:
            st.subheader(T["card_hdr"])
            card_data = st.session_state.get("last_member", ("M101", "Liam Carter", "ID-8840192", "2026-10-01"))
            c_left, c_right = st.columns([2, 1])
            with c_left:
                st.markdown(f"""
                <div class="member-card">
                    <h4 style="margin:0; color:#00d2ff;">🏛️ LIBRARY MEMBER PASS</h4>
                    <hr style="border-color: rgba(255,255,255,0.2);">
                    <p style="margin:4px 0;"><b>ID:</b> {card_data[0]}</p>
                    <p style="margin:4px 0;"><b>Name:</b> {card_data[1]}</p>
                    <p style="margin:4px 0;"><b>Issued:</b> {card_data[3]}</p>
                </div>
                """, unsafe_allow_html=True)
            with c_right:
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=130x130&data={card_data[0]}-{card_data[1]}"
                st.image(qr_url, caption=card_data[0])

    # === TAB 3: الإعارة والتجديد والإرجاع ===
    with tabs[2]:
        col_b, col_r = st.columns(2)

        with col_b:
            st.subheader(T["issue_hdr"])
            c.execute("SELECT member_id, full_name FROM members WHERE status = 'Active'")
            active_members = c.fetchall()
            c.execute("SELECT copy_id, title FROM books WHERE status = 'Available'")
            avail_list = c.fetchall()

            if not avail_list:
                st.warning("No available books / لا توجد كتب متاحة حالياً")
            else:
                sel_member = st.selectbox("Member / العضو:", [f"{m[0]} - {m[1]}" for m in active_members])
                sel_copy = st.selectbox("Book / الكتاب:", [f"{b[0]} - {b[1]}" for b in avail_list])
                loan_days = st.slider("Duration (Days) / مدة الاستعارة:", 7, 21, 14)

                if st.button(T["checkout_btn"], type="primary", use_container_width=True):
                    m_id = sel_member.split(" - ")[0]
                    b_id = sel_copy.split(" - ")[0]
                    c.execute("SELECT COUNT(*) FROM transactions WHERE member_id = ? AND return_date IS NULL", (m_id,))
                    if c.fetchone()[0] >= 3:
                        st.error("❌ Limit Reached (Max 3 books) / العضو وصل للحد الأقصى (3 كتب)")
                    else:
                        today = get_now().strftime("%Y-%m-%d")
                        due = (get_now() + timedelta(days=loan_days)).strftime("%Y-%m-%d")
                        c.execute("INSERT INTO transactions (member_id, copy_id, borrow_date, due_date) VALUES (?, ?, ?, ?)",
                                  (m_id, b_id, today, due))
                        c.execute("UPDATE books SET status = 'Borrowed' WHERE copy_id = ?", (b_id,))
                        conn.commit()
                        st.success(f"✅ Done! Due Date: **{due}**")
                        st.rerun()

        with col_r:
            st.subheader(T["return_hdr"])
            c.execute("""SELECT t.copy_id, b.title, t.member_id, t.due_date 
                         FROM transactions t JOIN books b ON t.copy_id = b.copy_id 
                         WHERE t.return_date IS NULL""")
            active_loans = c.fetchall()

            if not active_loans:
                st.info("No active loans / لا توجد استعارات نشطة حالياً")
            else:
                loan_options = [f"{l[0]} - {l[1]} (Member: {l[2]} | Due: {l[3]})" for l in active_loans]
                sel_return = st.selectbox("Active Loan / الاستعارة النشطة:", loan_options)
                daily_rate = st.number_input("Daily Fine ($) / غرامة التأخير اليومية:", 1.0, 20.0, 5.0, 1.0)

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button(T["return_btn"], type="primary", use_container_width=True):
                        r_copy_id = sel_return.split(" - ")[0]
                        c.execute("SELECT trans_id, due_date FROM transactions WHERE copy_id = ? AND return_date IS NULL", (r_copy_id,))
                        trans_id, due_str = c.fetchone()

                        due_date = datetime.strptime(due_str, "%Y-%m-%d")
                        today_date = get_now()
                        late_days = (today_date - due_date).days
                        fine = max(0.0, late_days * daily_rate)

                        c.execute("UPDATE transactions SET return_date = ?, fine_amount = ? WHERE trans_id = ?",
                                  (today_date.strftime("%Y-%m-%d"), fine, trans_id))
                        c.execute("UPDATE books SET status = 'Available' WHERE copy_id = ?", (r_copy_id,))
                        conn.commit()
                        st.rerun()
                with b_col2:
                    if st.button(T["renew_btn"], use_container_width=True):
                        r_copy_id = sel_return.split(" - ")[0]
                        c.execute("SELECT COUNT(*) FROM reservations WHERE copy_id = ?", (r_copy_id,))
                        if c.fetchone()[0] > 0:
                            st.error("❌ Cannot renew: Book is reserved by another patron!")
                        else:
                            c.execute("SELECT trans_id, due_date FROM transactions WHERE copy_id = ? AND return_date IS NULL", (r_copy_id,))
                            trans_id, due_str = c.fetchone()
                            new_due = (datetime.strptime(due_str, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
                            c.execute("UPDATE transactions SET due_date = ? WHERE trans_id = ?", (new_due, trans_id))
                            conn.commit()
                            st.success(f"✅ Renewed until **{new_due}**!")
                            st.rerun()

    # === TAB 4: التحليلات والتقارير (إخفاء بيانات المستعيرين عن الموظف العادي) ===
    with tabs[3]:
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("**Books by Category / الكتب حسب التخصص**")
            c.execute("SELECT category, COUNT(*) as count FROM books GROUP BY category")
            st.bar_chart(pd.DataFrame(c.fetchall(), columns=["Category", "Count"]).set_index("Category"))
        with ch2:
            st.markdown("**Inventory Status / حالة المخزون**")
            c.execute("SELECT status, COUNT(*) as count FROM books GROUP BY status")
            st.bar_chart(pd.DataFrame(c.fetchall(), columns=["Status", "Count"]).set_index("Status"))

        st.divider()
        if st.session_state.staff_role == "Administrative Coordinator":
            c.execute("SELECT * FROM transactions")
            trans_df = pd.DataFrame(c.fetchall(), columns=["Trans ID", "Member ID", "Copy ID", "Borrow Date", "Due Date", "Return Date", "Fine ($)"])
            st.dataframe(trans_df, use_container_width=True, hide_index=True)

            csv_data = trans_df.to_csv(index=False).encode("utf-8")
            st.download_button(T["csv_btn"], csv_data, "library_transactions_report.csv", "text/csv")
        else:
            st.info("🔒 Detailed borrower records and transaction logs are restricted to the **Administrative Coordinator (`admin`)** role.")

    # === TAB 5: إدارة الفهرس + سجل بيانات المستعيرين (خاص بالـ admin فقط) ===
    if st.session_state.staff_role == "Administrative Coordinator":
        with tabs[4]:
            st.subheader(T["borrowers_hdr"])
            c.execute("""SELECT m.member_id, m.full_name, m.national_id, m.phone, m.email,
                                b.copy_id, b.title, t.borrow_date, t.due_date,
                                COALESCE(t.return_date, 'Currently Borrowed') as status, t.fine_amount
                         FROM transactions t
                         JOIN members m ON t.member_id = m.member_id
                         JOIN books b ON t.copy_id = b.copy_id
                         ORDER BY t.trans_id DESC""")
            borrowers_rows = c.fetchall()
            if borrowers_rows:
                df_borrowers = pd.DataFrame(borrowers_rows, columns=[
                    "Member ID", "Borrower Name", "National/Uni ID", "Phone", "Email",
                    "Copy ID", "Book Title", "Borrow Date", "Due Date", "Return Status", "Fine ($)"
                ])
                st.dataframe(df_borrowers, use_container_width=True, hide_index=True)

            st.divider()
            adm1, adm2 = st.columns(2)
            with adm1:
                st.subheader(T["add_book_hdr"])
                with st.form("add_book_form", clear_on_submit=True):
                    new_copy_id = st.text_input("Copy ID (e.g., B007)")
                    new_isbn = st.text_input("ISBN")
                    new_title = st.text_input("Book Title / عنوان الكتاب")
                    new_author = st.text_input("Author / المؤلف")
                    new_cat = st.selectbox("Category / التخصص", ["Software Engineering", "Information Systems", "Computer Science", "Programming"])
                    new_shelf = st.text_input("Shelf Location (e.g., Shelf D-1)")
                    if st.form_submit_button("➕ Add Book / إضافة الكتاب", type="primary"):
                        if new_copy_id and new_title and new_author:
                            try:
                                c.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, 'Available')",
                                          (new_copy_id, new_isbn, new_title, new_author, new_cat, new_shelf))
                                conn.commit()
                                st.success(f"✅ Added **{new_title}**!")
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("⚠️ Copy ID already exists!")
                        else:
                            st.error("Please fill required fields.")

            with adm2:
                st.subheader(T["del_book_hdr"])
                c.execute("SELECT copy_id, title FROM books WHERE status = 'Available'")
                rem_books = c.fetchall()
                if rem_books:
                    del_choice = st.selectbox("Select Available Copy:", [f"{b[0]} - {b[1]}" for b in rem_books])
                    if st.button("🗑️ Delete Copy / حذف النسخة"):
                        del_id = del_choice.split(" - ")[0]
                        c.execute("DELETE FROM books WHERE copy_id = ?", (del_id,))
                        conn.commit()
                        st.warning(f"Deleted copy {del_id}.")
                        st.rerun()
