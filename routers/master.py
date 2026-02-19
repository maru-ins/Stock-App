from fastapi import APIRouter
from database import supabase
from models import ProdukCreate, KategoriCreate, KodeDesainCreate

router = APIRouter(prefix="/master", tags=["Master Data"])


# ======================
# KATEGORI
# ======================

@router.get("/kategori")
def get_kategori():
    response = supabase.table("kategori_kabel").select("*").order("nama_kategori").execute()
    return response.data


@router.post("/kategori")
def tambah_kategori(data: KategoriCreate):
    response = supabase.table("kategori_kabel").insert(data.dict()).execute()
    return response.data


# ======================
# KODE DESAIN
# ======================

@router.get("/kode-desain")
def get_kode_desain():
    response = supabase.table("kode_desain").select("*").order("kode_desain").execute()
    return response.data


@router.post("/kode-desain")
def tambah_kode_desain(data: KodeDesainCreate):
    response = supabase.table("kode_desain").insert(data.dict()).execute()
    return response.data


# ======================
# PRODUK
# ======================

@router.get("/produk")
def get_produk():
    response = supabase.table("produk_kabel") \
        .select("""
            id,
            nama_kabel,
            satuan,
            kategori_kabel ( nama_kategori ),
            kode_desain ( kode_desain )
        """) \
        .execute()

    return response.data

@router.get("/produk-by-kategori/{kategori_id}")
def get_produk_by_kategori(kategori_id: int):
    response = supabase.table("produk_kabel") \
        .select("id, nama_kabel") \
        .eq("kategori_id", kategori_id) \
        .order("nama_kabel") \
        .execute()

    return response.data


@router.post("/produk")
def tambah_produk(data: ProdukCreate):
    response = supabase.table("produk_kabel").insert(data.dict()).execute()
    return response.data




# from fastapi import APIRouter
# from database import supabase

# router = APIRouter(prefix="/master", tags=["Master Data"])

# # Ambil semua produk
# @router.get("/produk")
# def get_produk():
#     response = supabase.table("produk_kabel").select("*").execute()
#     return response.data

# # Tambah produk
# @router.post("/produk")
# def tambah_produk(data: dict):
#     response = supabase.table("produk_kabel").insert(data).execute()
#     return response.data
