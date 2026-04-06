# Yapay Zeka ile Müşteri Yorum Analizi

Gemini API, FastAPI, PostgreSQL, Streamlit, Docker ve AWS EC2 kullanarak
uçtan uca bir duygu analizi uygulaması.

---

## Proje Akışı

```
Gemini API → PostgreSQL → FastAPI → Streamlit → Docker → Deploy
```

Her adım bir öncekinin üzerine inşa edilir. Adımları sırayla takip edin.

---

## Adım 1 — Gemini ile Yorum Analizi Geliştirme

**Ne yapacağız?**
Google'ın Gemini yapay zeka modeline bağlanıp müşteri yorumlarını
duygu analizine göre sınıflandıracağız: **pozitif / negatif / nötr**

**Dosya:** `backend/app/services/gemini_service.py`

**Ne öğreneceğiz?**
- `google-genai` SDK kurulumu ve virtual environment kullanımı
- `genai.Client` ile API bağlantısı kurma
- Prompt mühendisliği (modele ne söylemek gerekir?)
- JSON formatında yapılandırılmış yanıt alma
- Async Gemini çağrısı (`client.aio.models.generate_content`)

**Test:**
```bash
cd backend
python app/services/gemini_service.py "Ürün harika, çok memnun kaldım!"
```

---

## Adım 2 — PostgreSQL ile Analiz Sonuçlarını Kaydetme

**Ne yapacağız?**
Her analiz sonucunu veritabanına kaydedeceğiz. Böylece geçmiş
analizlere erişebilecek ve istatistik gösterebileceğiz.

**Neden FastAPI'den önce?**
Veritabanı modelini ve bağlantısını önce kurarsak FastAPI'yi
yazarken zaten hazır olan DB katmanını entegre edebiliriz.
Sonradan geri dönüp değiştirmek gerekmez.

**Dosyalar:**
- `backend/app/core/config.py` — ortam değişkenlerini oku (.env)
- `backend/app/db/database.py` — async engine, session, get_db
- `backend/app/models/analysis.py` — analyses tablosu ORM modeli

**Ne öğreneceğiz?**
- Pydantic Settings ile `.env` dosyasından config okuma
- SQLAlchemy async engine kurulumu (`asyncpg` sürücüsü)
- ORM model tanımlama (Python sınıfı → veritabanı tablosu)
- Async session yönetimi ve `get_db` dependency pattern'i

**Bağlantı string formatı:**
```
postgresql+asyncpg://kullanici:sifre@host:5432/veritabani
```

**Test:**
```bash
# Sadece PostgreSQL container'ını başlat
docker compose up db -d

# Bağlantı + tablo oluşturma + CRUD testini çalıştır
cd backend
python test_db.py
```

---

## Adım 3 — FastAPI ile Yorum Analizi API'si Geliştirme

**Ne yapacağız?**
Gemini (Adım 1) ve PostgreSQL (Adım 2) servislerini bir REST API'ye
bağlayacağız. İki endpoint yazacağız:
- `POST /api/v1/analysis/` → yorum gönder, analiz sonucu al ve kaydet
- `GET  /api/v1/analysis/history` → geçmiş analizleri listele

**Dosyalar:**
- `backend/main.py` — uygulama giriş noktası, CORS, lifespan
- `backend/app/schemas/schemas.py` — request/response modelleri (Pydantic)
- `backend/app/api/routes/analysis.py` — endpoint tanımları
- `backend/app/services/analysis_service.py` — Gemini + DB iş mantığı

**Ne öğreneceğiz?**
- FastAPI kurulumu ve async uygulama oluşturma
- Pydantic ile otomatik veri doğrulama
- CORS middleware (Streamlit'in API'ye erişebilmesi için)
- `lifespan` ile async tablo oluşturma
- Dependency Injection ile `get_db` kullanımı
- Swagger UI ile otomatik dokümantasyon (`/docs`)

**Test:**
```bash
cd backend
uvicorn main:app --reload
# Tarayıcıda: http://localhost:8000/docs
```

---

## Adım 4 — Streamlit ile Kullanıcı Arayüzü Geliştirme

**Ne yapacağız?**
Kullanıcıların yorum yazabileceği ve analiz sonuçlarını görebileceği
bir web arayüzü oluşturacağız.

**Dosyalar:**
- `frontend/app.py` — tek sayfa: ayarlar + dashboard + form + geçmiş
- `frontend/api_client.py` — FastAPI'ye HTTP istekleri atan client

**Ne öğreneceğiz?**
- Streamlit kurulumu ve `streamlit run` komutu
- `st.form` ile kullanıcı girişi alma
- `st.session_state` ile sayfa yenilenince veriyi koruma
- `st.columns` ve `st.metric` ile düzen oluşturma
- `st.container(border=True)` ile kart görünümü (saf Python, HTML yok)
- `requests` kütüphanesi ile FastAPI'ye istek atma

**Test:**
```bash
cd frontend
streamlit run app.py
# Tarayıcıda: http://localhost:8501
```

---

## Adım 5 — Docker

**Ne yapacağız?**
Tüm servisleri (PostgreSQL, FastAPI, Streamlit) Docker container'larına
alacağız. Tek komutla hepsini ayağa kaldıracağız.

**Dosyalar:**
- `backend/Dockerfile` — FastAPI image'ı
- `frontend/Dockerfile` — Streamlit image'ı
- `docker-compose.yml` — 3 servisi birlikte yönetir

**Ne öğreneceğiz?**
- `Dockerfile` yazımı (base image, WORKDIR, COPY, RUN, CMD)
- Docker layer cache mantığı (neden önce requirements.txt kopyalanır?)
- `docker-compose.yml` ile çok servisli yapı kurma
- Servisler arası iletişim (servis adı = hostname)
- `healthcheck` ve `depends_on` ile başlatma sırası belirleme
- Named volume ile veri kalıcılığı

**Komutlar:**
```bash
# Tüm servisleri başlat
docker compose up --build

# Arka planda çalıştır
docker compose up -d --build

# Durdur (veriyi koru)
docker compose down

# Durdur + veriyi sil
docker compose down -v
```

**Çalışan servisler:**

| Servis | URL |
|--------|-----|
| Streamlit | http://localhost:8501 |
| FastAPI Swagger | http://localhost:8000/docs |
| PostgreSQL | localhost:5433 |

---

## Adım 6 — Deploy (AWS EC2)

**Ne yapacağız?**
Uygulamayı AWS EC2 üzerinde gerçek bir sunucuya deploy edeceğiz.
İnternet üzerinden erişilebilir hale getireceğiz.

**Ne öğreneceğiz?**
- EC2 instance oluşturma (Ubuntu 22.04, t2.micro)
- Security Group ile port açma (22, 8000, 8501)
- SSH ile sunucuya bağlanma
- Sunucuya Docker kurma
- Uygulamayı production'da çalıştırma

**Adımlar:**

1. EC2 instance oluşturun:
   - AMI: Ubuntu 22.04 LTS
   - Tip: t2.micro (ücretsiz kullanım)
   - Security Group: 22 (SSH), 8000 (API), 8501 (Streamlit) portlarını açın

2. SSH ile bağlanın:
   ```bash
   ssh -i anahtar.pem ubuntu@<ec2-ip-adresi>
   ```

3. Docker kurun:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-plugin
   sudo usermod -aG docker ubuntu
   newgrp docker
   ```

4. Projeyi klonlayın:
   ```bash
   git clone <repo-url>
   cd yorum-analizi
   cp backend/.env.example backend/.env
   # .env dosyasına GEMINI_API_KEY'i yazın
   nano backend/.env
   ```

5. Başlatın:
   ```bash
   docker compose up -d --build
   ```

6. Erişin:
   ```
   http://<ec2-ip-adresi>:8501        → Streamlit
   http://<ec2-ip-adresi>:8000/docs   → FastAPI
   ```

---

## Proje Yapısı

```
yorum-analizi/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── analysis.py        # Adım 3: POST /analysis, GET /history
│   │   ├── core/
│   │   │   └── config.py          # Adım 2: .env okuma
│   │   ├── db/
│   │   │   └── database.py        # Adım 2: Async engine, get_db
│   │   ├── models/
│   │   │   └── analysis.py        # Adım 2: analyses tablosu
│   │   ├── schemas/
│   │   │   └── schemas.py         # Adım 3: Pydantic modeller
│   │   └── services/
│   │       ├── gemini_service.py  # Adım 1: Gemini API
│   │       └── analysis_service.py # Adım 3: Gemini + DB iş mantığı
│   ├── main.py                    # Adım 3: FastAPI giriş noktası
│   ├── requirements.txt
│   ├── Dockerfile                 # Adım 5: Backend image
│   └── .env.example
├── frontend/
│   ├── app.py                     # Adım 4: Streamlit tek sayfa
│   ├── api_client.py              # Adım 4: HTTP client
│   ├── requirements.txt
│   ├── Dockerfile                 # Adım 5: Frontend image
│   └── .env.example
└── docker-compose.yml             # Adım 5: Tüm servisler
```
