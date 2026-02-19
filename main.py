from fastapi import FastAPI
from routers import master
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from supabase import create_client, Client
from dotenv import load_dotenv
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
def halaman_input(request: Request, kategori_id: int | None = None):

    # Ambil semua kategori
    kategori = supabase.table("kategori_kabel") \
        .select("*") \
        .order("nama_kategori") \
        .execute().data

    # Jika kategori dipilih → filter produk
    if kategori_id:
        produk = supabase.table("produk_kabel") \
            .select("id, nama_kabel") \
            .eq("kategori_id", kategori_id) \
            .order("nama_kabel") \
            .execute().data
    else:
        produk = []

    return templates.TemplateResponse("input_stock.html", {
        "request": request,
        "kategori": kategori,
        "produk": produk,
        "kategori_selected": kategori_id
    })
