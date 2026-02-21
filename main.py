from fastapi import FastAPI
from routers import master
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import Form
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

## GET STOCK AWALAN 

@app.get("/stock-awal", response_class=HTMLResponse)
def halaman_stock_awal(request: Request):

    kategori = supabase.table("kategori_kabel") \
        .select("*") \
        .order("nama_kategori") \
        .execute().data

    produk = supabase.table("produk_kabel") \
        .select("id, nama_kabel, kategori_id, kode_desain(kode_desain)") \
        .order("nama_kabel") \
        .execute().data

    return templates.TemplateResponse("stock_awal.html", {
        "request": request,
        "kategori": kategori,
        "produk": produk
    })

## SAVE STOCK AWAL SISTEM

@app.post("/save-stock-awal")
def save_stock_awal(
    tahun: int = Form(...),
    bulan: int = Form(...),
    data_json: str = Form(...)
):

    data_list = json.loads(data_json)

    insert_data = []

    for item in data_list:
        insert_data.append({
            "kode_desain_id": item["produk_id"],
            "tahun": tahun,
            "bulan": bulan,
            "jumlah_stock_awal": float(item["jumlah"])
        })

    supabase.table("stock_awal_bulanan") \
        .insert(insert_data) \
        .execute()

    return {"status": "success"}


##SAVE MINGGUAN

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


@app.post("/generate-stock-awal")
def generate_stock_awal(
    tahun: int = Form(...),
    bulan: int = Form(...),
    mode: str = Form("normal")  # normal | replace
):
    """
    mode:
    - normal  → tidak boleh generate kalau sudah ada
    - replace → hapus dulu lalu generate ulang
    """

    # Tentukan bulan sebelumnya
    if bulan == 1:
        prev_bulan = 12
        prev_tahun = tahun - 1
    else:
        prev_bulan = bulan - 1
        prev_tahun = tahun

    # 🔎 Cek apakah data bulan ini sudah ada
    existing = supabase.table("stock_awal_bulanan") \
        .select("id") \
        .eq("tahun", tahun) \
        .eq("bulan", bulan) \
        .execute().data

    if existing and mode == "normal":
        return {
            "error": f"Stock awal bulan {bulan}/{tahun} sudah ada!"
        }

    # 🔄 Jika mode replace → hapus dulu
    if existing and mode == "replace":
        supabase.table("stock_awal_bulanan") \
            .delete() \
            .eq("tahun", tahun) \
            .eq("bulan", bulan) \
            .execute()

    # 🔎 Ambil stock akhir bulan sebelumnya dari view
    result = supabase.table("view_laporan_bulanan") \
        .select("kode_desain_id, stock_akhir") \
        .eq("tahun", prev_tahun) \
        .eq("bulan", prev_bulan) \
        .execute().data

    if not result:
        return {
            "error": f"Tidak ada data bulan {prev_bulan}/{prev_tahun}"
        }

    insert_data = []

    for row in result:
        insert_data.append({
            "kode_desain_id": row["kode_desain_id"],
            "tahun": tahun,
            "bulan": bulan,
            "jumlah_stock_awal": row["stock_akhir"]
        })

    supabase.table("stock_awal_bulanan") \
        .insert(insert_data) \
        .execute()

    return {
        "status": f"Stock awal bulan {bulan}/{tahun} berhasil digenerate"
    }

#### DASHBOARD



@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, tahun: int = None, bulan: int = None):

    if not tahun:
        tahun = datetime.now().year
    if not bulan:
        bulan = datetime.now().month

    # Data bulan aktif
    data = supabase.table("view_laporan_bulanan") \
        .select("*") \
        .eq("tahun", tahun) \
        .eq("bulan", bulan) \
        .execute().data

    labels = []
    stock_akhir = []
    produksi_data = []
    pengiriman_data = []

    total_produksi = 0
    total_pengiriman = 0
    total_stock = 0

    warning_stock = []

    for row in data:
        labels.append(row["nama_kategori"])
        produksi_data.append(row["total_produksi"])
        pengiriman_data.append(row["total_pengiriman"])
        stock_akhir.append(row["stock_akhir"])

        total_produksi += row["total_produksi"]
        total_pengiriman += row["total_pengiriman"]
        total_stock += row["stock_akhir"]

        if row["stock_akhir"] < 0:
            warning_stock.append(row["nama_kategori"])

    # Trend 12 bulan
    trend = supabase.rpc("fn_trend_12_bulan", {"tahun_param": tahun}).execute().data

    trend_labels = [t["bulan"] for t in trend]
    trend_stock = [t["total_stock"] for t in trend]

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "labels": labels,
        "stock_akhir": stock_akhir,
        "produksi_data": produksi_data,
        "pengiriman_data": pengiriman_data,
        "total_produksi": total_produksi,
        "total_pengiriman": total_pengiriman,
        "total_stock": total_stock,
        "trend_labels": trend_labels,
        "trend_stock": trend_stock,
        "warning_stock": warning_stock,
        "tahun": tahun,
        "bulan": bulan
    })