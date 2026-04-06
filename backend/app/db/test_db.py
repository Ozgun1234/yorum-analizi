"""
ADIMLAR:
    1. Sadece PostgreSQL container'ını başlat
    2. Test için doğrudan DB bağlantısı kur
    3. Tabloları oluştur
    4. Test kaydı ekle
    5. Kaydı sorgula ve ekrana yazdır
    6. Test kaydını temizle

KURULUM:
    1. Sadece PostgreSQL'i başlatın (FastAPI ve Streamlit olmadan):
           docker compose up db -d
    2. Çalıştığını doğrulayın:
           docker compose ps
    3. Bu test dosyasını çalıştırın:
           python test_db.py

NOT:
    Bu dosya FastAPI olmadan, doğrudan SQLAlchemy üzerinden
    veritabanı bağlantısını ve ORM modelini test eder.

    Neden localhost:5433?
        docker-compose.yml'de PostgreSQL portu 5433 olarak dışa açıldı:
            ports: "5433:5432"
        Container içinde 5432, dışarıdan 5433 ile erişilir.
        FastAPI container içindeyken "db:5432" kullanır,
        biz burada dışarıdan bağlandığımız için "localhost:5433" kullanıyoruz.
"""

# =========================================================
# 1. Gerekli kütüphaneleri import et
# =========================================================
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, text

from app.models.analysis import Analysis
from app.db.database import Base


# =========================================================
# 2. Test için doğrudan DB bağlantısı kur
# =========================================================
# Dışarıdan bağlandığımız için localhost:5433 kullanıyoruz
# (docker-compose.yml'de 5433:5432 olarak map edildi)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/yorum_analizi"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
# echo=True: çalışan SQL sorgularını terminale yazdırır — öğrenmek için faydalı

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


# =========================================================
# 3. Tabloları oluştur
# =========================================================
async def create_tables():
    """
    Amaç:
        Base.metadata.create_all ile tüm ORM modellerindeki tabloları
        PostgreSQL'de oluşturmak.
        Tablo zaten varsa bu işlem hiçbir şey yapmaz (güvenli).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablolar oluşturuldu (veya zaten vardı)")


# =========================================================
# 4. Test kaydı ekle
# =========================================================
async def insert_test_record() -> int:
    """
    Amaç:
        analyses tablosuna sahte bir analiz kaydı ekleyip
        veritabanına yazma işlemini test etmek.

    Returns:
        Eklenen kaydın id'si
    """
    async with AsyncSessionLocal() as db:
        analysis = Analysis(
            comment_text="Bu bir test yorumudur.",
            sentiment="pozitif",
            confidence=0.99,
            explanation="Bu kayıt test_db.py tarafından oluşturuldu.",
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

    print(f"✅ Test kaydı eklendi  →  id={analysis.id}")
    return analysis.id


# =========================================================
# 5. Kaydı sorgula ve ekrana yazdır
# =========================================================
async def query_record(record_id: int):
    """
    Amaç:
        Az önce eklediğimiz kaydı id ile sorgulayıp
        veritabanından okuma işlemini test etmek.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Analysis).where(Analysis.id == record_id)
        )
        analysis = result.scalar_one_or_none()

    if analysis:
        print("\n📋 Sorgulanan kayıt:")
        print(f"   id           : {analysis.id}")
        print(f"   comment_text : {analysis.comment_text}")
        print(f"   sentiment    : {analysis.sentiment}")
        print(f"   confidence   : {analysis.confidence}")
        print(f"   explanation  : {analysis.explanation}")
        print(f"   created_at   : {analysis.created_at}")
    else:
        print("❌ Kayıt bulunamadı!")


# =========================================================
# 6. Test kaydını temizle
# =========================================================
async def delete_test_record(record_id: int):
    """
    Amaç:
        Test verisini veritabanından silip temizlemek.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Analysis).where(Analysis.id == record_id)
        )
        analysis = result.scalar_one_or_none()
        if analysis:
            await db.delete(analysis)
            await db.commit()

    print(f"\n🗑️  Test kaydı silindi  →  id={record_id}")


# =========================================================
# Tüm adımları sırayla çalıştır
# =========================================================
async def main():
    print("=" * 50)
    print("  Veritabanı Bağlantı Testi")
    print("=" * 50)

    await create_tables()

    record_id = await insert_test_record()
    await query_record(record_id)
    await delete_test_record(record_id)

    print("\n✅ Tüm testler başarılı! Veritabanı bağlantısı çalışıyor.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
