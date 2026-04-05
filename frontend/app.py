"""
ADIMLAR:
    1. Streamlit sayfa ayarlarını yap  (başlık, ikon, layout)
    2. Uygulama genelinde geçerli CSS stillerini uygula
    3. Ana sayfayı çağır

KURULUM:
    1. Virtual environment'ı aktif edin:
           - Windows : venv\Scripts\activate
           - Mac/Linux: source venv/bin/activate
    2. requirements.txt dosyasına şunları ekleyin:
           streamlit
           requests
           python-dotenv
    3. Bağımlılıkları yükleyin:
           pip install -r requirements.txt
    4. Uygulamayı başlatmak için:
           streamlit run app.py
    5. Tarayıcıda otomatik açılır:
           http://localhost:8501

NOT:
    Bu dosya Streamlit uygulamasının giriş noktasıdır (entry point).
    FastAPI'deki main.py ile aynı rolü oynar.
    Sayfa yönlendirmesi (routing) ve global stiller burada tanımlanır.
"""

# =========================================================
# 1. Streamlit sayfa ayarlarını yap
# =========================================================
import streamlit as st
from pages import main_page

# set_page_config: her uygulamada ilk çağrılması gereken Streamlit fonksiyonu
st.set_page_config(
    page_title="Yorum Analizi",
    page_icon="🎓",
    layout="wide",   # Tam genişlik kullan
)


# =========================================================
# 2. Uygulama genelinde geçerli CSS stillerini uygula
# =========================================================
# unsafe_allow_html=True: Ham HTML/CSS yazabilmemizi sağlar.
# Streamlit'in varsayılan açık temasını koyu temaya çeviriyoruz.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Temel ── */
*, html, body { font-family: 'Inter', 'Segoe UI', sans-serif !important; }
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] { background-color: #080E1C !important; }

[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Tüm default metinler */
p, span, div, label { color: #CBD5E1; }
h1, h2, h3, h4, h5 { color: #F1F5F9 !important; font-weight: 700 !important; }

/* ── Kolon ayırıcı ── */
[data-testid="stColumns"] {
    gap: 0 !important;
    align-items: stretch;
}
[data-testid="stColumn"]:first-child {
    background: #0C1525;
    border-right: 1px solid rgba(255,255,255,0.06);
    padding: 2rem 1.8rem !important;
    min-height: 100vh;
}
[data-testid="stColumn"]:last-child {
    background: #080E1C;
    padding: 2rem 2rem !important;
    min-height: 100vh;
}

/* ── Stat kartları ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 0;
}
.stat-card {
    background: #111D30;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px 14px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}
.stat-card.total::before  { background: #3B82F6; }
.stat-card.pos::before    { background: #10B981; }
.stat-card.neg::before    { background: #EF4444; }
.stat-card.notr::before   { background: #F59E0B; }
.stat-value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 5px;
}
.stat-card.total .stat-value { color: #60A5FA; }
.stat-card.pos   .stat-value { color: #34D399; }
.stat-card.neg   .stat-value { color: #F87171; }
.stat-card.notr  .stat-value { color: #FBBF24; }
.stat-label {
    font-size: 10px;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* ── Feed & Review kartları ── */
.section-title {
    font-size: 11px;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 20px 0 10px;
}
.feed-card {
    background: #111D30;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.feed-card:hover { border-color: rgba(59,130,246,0.3); }
.card-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.badge {
    font-size: 10px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.badge.pos { background:rgba(16,185,129,0.12); color:#34D399; border:1px solid rgba(16,185,129,0.25); }
.badge.neg { background:rgba(239,68,68,0.12);  color:#F87171; border:1px solid rgba(239,68,68,0.25); }
.badge.notr{ background:rgba(245,158,11,0.12); color:#FBBF24; border:1px solid rgba(245,158,11,0.25); }
.conf { font-size: 11px; color: #334155; font-weight: 600; }
.card-comment {
    font-size: 13px;
    color: #94A3B8;
    line-height: 1.55;
    margin-bottom: 4px;
}
.card-explanation {
    font-size: 11px;
    color: #3B5A8A;
    font-style: italic;
    line-height: 1.4;
}

/* ── Ürün başlığı ── */
.product-header {
    background: #111D30;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.product-icon { font-size: 36px; line-height: 1; }
.product-name { font-size: 16px; font-weight: 700; color: #F1F5F9; margin-bottom: 3px; }
.product-meta { font-size: 12px; color: #475569; }
.product-rating { color: #FBBF24; }

/* ── Review kartları ── */
.review-card {
    background: #111D30;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.review-user { font-size: 12px; font-weight: 600; color: #475569; }
.review-text { font-size: 13px; color: #94A3B8; line-height: 1.55; margin-top: 6px; }

/* ── Form alanları ── */
textarea {
    background-color: #111D30 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #E2E8F0 !important;
    font-size: 14px !important;
    padding: 14px !important;
    resize: none !important;
    transition: border-color 0.2s !important;
}
textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
textarea::placeholder { color: #334155 !important; }
.stTextArea label { display: none !important; }

/* ── Gönder butonu ── */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #1D4ED8 0%, #3B82F6 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 0 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.3) !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stFormSubmitButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── Boşluk ve divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.2rem 0 !important; }
[data-testid="stAlert"] {
    border-radius: 10px !important;
    background: #111D30 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 4px; }

/* ── Sidebar ve Streamlit chrome'u gizle ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebar"] { display: none !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] p { color: #64748B !important; }

/* ── Toast ── */
[data-testid="toastContainer"] { font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. Ana sayfayı çağır
# =========================================================
main_page.show()
