"""
ADIMLAR:
    1. Async SQLAlchemy engine'i oluştur  (veritabanı bağlantısı)
    2. Async session factory'yi tanımla   (her istek için ayrı oturum)
    3. Base class'ı oluştur               (ORM modelleri bu sınıftan türer)
    4. get_db dependency'sini yaz         (FastAPI bunu her endpoint'e enjekte eder)

KURULUM:
    1 Virtual environment'ı aktif edin:
           - Windows : venv\Scripts\activate
           - Mac/Linux: source venv/bin/activate
    2. requirements.txt dosyasına şunları ekleyin:
           sqlalchemy[asyncio]
           asyncpg
    3. Bağımlılıkları yükleyin:
           pip install -r requirements.txt
    4. backend/.env dosyasına bağlantı string'ini yazın:
           DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/yorum_analizi

NOT:
    Neden asyncpg?
        psycopg2 sync (blocking) bir sürücüdür.
        asyncpg ise async/await destekli PostgreSQL sürücüsüdür.
        FastAPI async çalıştığı için asyncpg kullanmak gerekir,
        aksi takdirde DB sorgusu tüm event loop'u bloklar.

    Neden postgresql+asyncpg:// ?
        SQLAlchemy hangi sürücüyü kullanacağını URL'den anlar:
            postgresql://          →  psycopg2  (sync)
            postgresql+asyncpg://  →  asyncpg   (async)
"""

# =========================================================
# 1. Async SQLAlchemy engine'i oluştur
# =========================================================
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Async engine: bağlantı havuzunu async olarak yönetir
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,      # Havuzda sürekli açık tutulan bağlantı sayısı
    max_overflow=10,  # Havuz dolunca açılabilecek ekstra bağlantı sayısı
    echo=False,       # True yapılırsa çalışan SQL sorguları terminale yazdırılır
)


# =========================================================
# 2. Async session factory'yi tanımla
# =========================================================
# async_sessionmaker: her çağrıda yeni bir AsyncSession üretir
# expire_on_commit=False: commit sonrası nesne alanlarına erişmeye devam edebiliriz
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


# =========================================================
# 3. Base class'ı oluştur
# =========================================================
# Tüm ORM modelleri (örn: Analysis) bu sınıftan miras alır
Base = declarative_base()


# =========================================================
# 4. get_db dependency'sini yaz
# =========================================================
async def get_db():
    """
    Amaç:
        FastAPI endpoint'lerine async veritabanı session'ı sağlamak.

    Nasıl çalışır?
        async with: session açılır, endpoint'e verilir, blok bitince
        otomatik kapatılır — hata olsa bile. try/finally gerekmez.

    Kullanım (routes/analysis.py içinde):
        async def analyze(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session
