INSERT INTO produk_kabel (
    nama_produk,
    kategori_id,
    kode_desain_id
)
SELECT
    t.nama_kabel,
    k.id,
    d.id
FROM temp_produk t
JOIN kategori_kabel k
    ON TRIM(LOWER(k.nama_kategori)) = TRIM(LOWER(t.nama_kategori))
JOIN kode_desain d
    ON TRIM(LOWER(d.kode)) = TRIM(LOWER(t.kode_desain));
