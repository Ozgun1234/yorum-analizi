"""
ADIMLAR:
    1. Sayfa yüklenince geçmiş analizleri veritabanından çek
    2. Dashboard istatistik kartlarını göster (toplam/pozitif/negatif/nötr)
    3. Yorum giriş formunu oluştur
    4. Form gönderilince Gemini analizi yap ve sayfayı yenile
    5. Geçmiş analiz listesini feed olarak göster

NOT:
    st.session_state: Streamlit'te sayfa yenilenince veriler sıfırlanır.
    session_state bu veriyi tarayıcı oturumu boyunca bellekte tutar.

    st.rerun(): Formu gönderdikten sonra sayfayı sıfırdan çizer.
    Böylece yeni analiz anında listenin en üstünde görünür.
"""

# =========================================================
# 1. Sayfa yüklenince geçmiş analizleri veritabanından çek
# =========================================================
import requests
import streamlit as st
from api_client import analyze_comment, get_history


def _load_from_db():
    """
    Amaç:
        FastAPI üzerinden veritabanındaki tüm analizleri çekip
        session_state'e kaydetmek. Hata olursa boş liste kullan.
    """
    try:
        data = get_history(limit=100)
        st.session_state.analyses = [
            {
                "comment":     a["comment_text"],
                "sentiment":   a["sentiment"],
                "confidence":  a["confidence"],
                "explanation": a.get("explanation", ""),
            }
            for a in data.get("analyses", [])
        ]
    except Exception:
        st.session_state.analyses = []


# Yardımcı fonksiyonlar — badge CSS sınıfı ve etiket metni
def _badge_class(sentiment: str) -> str:
    s = sentiment.lower()
    if s == "pozitif": return "pos"
    if s == "negatif": return "neg"
    return "notr"


def _badge_label(sentiment: str) -> str:
    s = sentiment.lower()
    if s == "pozitif": return "😊 Pozitif"
    if s == "negatif": return "😠 Negatif"
    return "😐 Nötr"


def show():
    # İlk açılışta session_state'te veri yoksa veritabanından yükle
    if "analyses" not in st.session_state:
        _load_from_db()

    analyses = st.session_state.analyses
    total    = len(analyses)
    pozitif  = sum(1 for a in analyses if a["sentiment"].lower() == "pozitif")
    negatif  = sum(1 for a in analyses if a["sentiment"].lower() == "negatif")
    notr     = total - pozitif - negatif

    # Sayfayı iki sütuna böl: sol = dashboard, sağ = analiz formu
    left, right = st.columns([2, 3])

    # =========================================================
    # 2. Dashboard istatistik kartlarını göster
    # =========================================================
    with left:
        st.markdown("## 📊 Dashboard")

        st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card total">
    <div class="stat-value">{total}</div>
    <div class="stat-label">Toplam</div>
  </div>
  <div class="stat-card pos">
    <div class="stat-value">{pozitif}</div>
    <div class="stat-label">Pozitif</div>
  </div>
  <div class="stat-card neg">
    <div class="stat-value">{negatif}</div>
    <div class="stat-label">Negatif</div>
  </div>
  <div class="stat-card notr">
    <div class="stat-value">{notr}</div>
    <div class="stat-label">Nötr</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # =========================================================
        # 5. Geçmiş analiz listesini feed olarak göster
        # =========================================================
        st.markdown('<div class="section-title">Son Analizler</div>', unsafe_allow_html=True)

        if not analyses:
            st.markdown("""
<div style="text-align:center;padding:40px 0;color:#334155;font-size:13px;line-height:1.8">
  Henüz analiz yok.<br>Sağ taraftan bir yorum gönderin.
</div>
""", unsafe_allow_html=True)
        else:
            for a in analyses:
                cls   = _badge_class(a["sentiment"])
                label = _badge_label(a["sentiment"])
                conf  = int(a["confidence"] * 100)
                # Uzun yorumları kısalt
                short = a["comment"][:120] + "..." if len(a["comment"]) > 120 else a["comment"]
                exp   = f'<div class="card-explanation">{a["explanation"]}</div>' if a.get("explanation") else ""

                st.markdown(f"""
<div class="feed-card">
  <div class="card-row">
    <span class="badge {cls}">{label}</span>
    <span class="conf">%{conf} güven</span>
  </div>
  <div class="card-comment">{short}</div>
  {exp}
</div>
""", unsafe_allow_html=True)

    # =========================================================
    # 3. Yorum giriş formunu oluştur
    # =========================================================
    with right:
        st.markdown("""
<div class="product-header">
  <div class="product-icon">🤖</div>
  <div>
    <div class="product-name">Yapay Zeka ile Müşteri Yorum Analizi</div>
    <div class="product-meta">
      Verimlilik &nbsp;·&nbsp; Üretkenlik &nbsp;·&nbsp; 2.4K değerlendirme &nbsp;·&nbsp;
      <span class="product-rating">★★★★★</span>
      <span style="color:#475569">&nbsp;4.8 / 5.0</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">💬 Uygulama Değerlendirmesi Yaz</div>', unsafe_allow_html=True)

        # st.form: tüm inputlar tek seferde gönderilir, her tuş basışında rerun olmaz
        with st.form("comment_form", clear_on_submit=True):
            comment = st.text_area(
                label="yorum",
                placeholder="Uygulamayı kullandınız mı? Deneyiminizi paylaşın...",
                height=120,
            )
            submitted = st.form_submit_button(
                "🚀 Gönder & Analiz Et",
                use_container_width=True,
            )

        # =========================================================
        # 4. Form gönderilince Gemini analizi yap ve sayfayı yenile
        # =========================================================
        if submitted:
            if not comment.strip():
                st.warning("Lütfen bir yorum girin.")
            else:
                with st.spinner("Gemini analiz ediyor..."):
                    try:
                        analyze_comment(comment.strip())  # POST /analysis/
                        _load_from_db()                   # Güncel listeyi çek
                        st.toast("Analiz tamamlandı!", icon="✅")
                        st.rerun()                        # Sayfayı yeniden çiz
                    except requests.HTTPError:
                        st.error("Analiz sırasında hata oluştu.")
                    except Exception:
                        st.error("API bağlantı hatası.")

        if analyses:
            st.markdown('<div class="section-title">📝 Kullanıcı Değerlendirmeleri</div>', unsafe_allow_html=True)

            for i, a in enumerate(analyses):
                cls   = _badge_class(a["sentiment"])
                label = _badge_label(a["sentiment"])

                st.markdown(f"""
<div class="review-card">
  <div class="card-row">
    <span class="review-user">Kullanıcı #{total - i}</span>
    <span class="badge {cls}">{label}</span>
  </div>
  <div class="review-text">{a["comment"]}</div>
</div>
""", unsafe_allow_html=True)
