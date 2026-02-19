from pydantic import BaseModel

class ProdukCreate(BaseModel):
    nama_kabel: str
    kategori_id: int
    kode_desain_id: int
    satuan: str
    
class KategoriCreate(BaseModel):
    nama_kategori: str

class KodeDesainCreate(BaseModel):
    kode_desain: str
    deskripsi: str | None = None
