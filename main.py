from fastapi import FastAPI
from routers import master
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from supabase import create_client, Client
from dotenv import load_dotenvfrom fastapi import Form
import json
from datetime import datetime
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app = FastAPI(title="Stock Report API")

app.include_router(master.router)

@app.get("/")
def root():
    return {"message": "Stock App Running"}


templates = Jinja2Templates(directory="templates")

@app.get("/input", response_class=HTMLResponse)
def halaman_input(request: Request):

    # Ambil semua kategori
    kategori = supabase.table("kategori_kabel") \
        .select("*") \
        .order("nama_kategori") \
        .execute().data

    # Ambil semua produk + join kode_desain
    produk = supabase.table("produk_kabel") \
        .select("id, nama_kabel, kategori_id, kode_desain(kode_desain)") \
        .order("nama_kabel") \
        .execute().data

    return templates.TemplateResponse("input_stock.html", {
        "request": request,
        "kategori": kategori,
        "produk": produk
    })

# @app.get("/input", response_class=HTMLResponse)
# def halaman_input(request: Request, kategori_id: int | None = None):

   
#     kategori = supabase.table("kategori_kabel") \
#         .select("*") \
#         .order("nama_kategori") \
#         .execute().data

   
#     if kategori_id:
#         produk = supabase.table("produk_kabel") \
#             .select("id, nama_kabel") \
#             .eq("kategori_id", kategori_id) \
#             .order("nama_kabel") \
#             .execute().data
#     else:
#         produk = []

#     return templates.TemplateResponse("input_stock.html", {
#         "request": request,
#         "kategori": kategori,
#         "produk": produk,
#         "kategori_selected": kategori_id
#     })


@app.post("/save-stok")
def save_stok(
    bulan: int = Form(...),
    minggu: int = Form(...),
    jenis_transaksi: str = Form(...),
    data_json: str = Form(...)
):

    tahun = datetime.now().year
    data_list = json.loads(data_json)

    insert_data = []

    for item in data_list:
        insert_data.append({
            "kode_desain_id": item["produk_id"],
            "tahun": tahun,
            "bulan": bulan,
            "minggu_ke": minggu,
            "jenis_transaksi": jenis_transaksi,
            "jumlah_km": float(item["jumlah"])
        })

    supabase.table("table_transaksi_mingguan") \
        .insert(insert_data) \
        .execute()

    return {"status": "success"}