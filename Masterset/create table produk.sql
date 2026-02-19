CREATE TABLE "produk_kabel" (
	"id"	INTEGER,
	"nama_produk"	TEXT NOT NULL,
	"kategori_id"	INTEGER NOT NULL,
	"kode_desain_id"	INTEGER NOT NULL,
	"satuan"	TEXT DEFAULT 'KM',
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("kategori_id") REFERENCES "kategori_kabel"("id"),
	FOREIGN KEY("kode_desain_id") REFERENCES "kode_desain"("id")
);