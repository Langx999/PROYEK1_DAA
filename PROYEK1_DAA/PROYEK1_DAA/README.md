# Proyek 1 DAA — Paleogenomika: Sekuens DNA Kuno

**Nama:** M. Galang Setyawan  
**Algoritma:** KMP (Knuth-Morris-Pratt) + Merge Sort  
**Bahasa:** Python 3, tanpa library eksternal.

## Ringkasan
Program mencari fragmen DNA dalam untai referensi. Kecocokan diterima jika seluruh karakter sama, atau jika hanya karakter paling kanan fragmen yang berbeda. Program mencari seluruh posisi yang memenuhi aturan, memilih kecocokan terbaik (skor tertinggi, lalu indeks terkecil), dan mengurutkan laporan dengan Merge Sort.

**Catatan dataset:** folder `data/` berisi data simulasi untuk demonstrasi, bukan hasil ekstraksi DNA fosil. Ganti dengan dataset resmi kelas setelah mengunduhnya dari repositori dosen. Berkas referensi harus berisi urutan A/C/G/T saja; berkas pola berisi satu fragmen per baris.

## Struktur folder

```text
proyek_paleogenomika_galang/
├── main.py
├── README.md
├── data/
│   ├── reference_dna.txt
│   └── patterns.txt
└── diagram/
    ├── flowchart.png
    └── class_diagram.png
```

## Cara menjalankan di Windows CMD

1. Ekstrak folder proyek.
2. Buka CMD, lalu masuk ke folder proyek, contohnya:

```bat
cd %USERPROFILE%\Downloads\proyek_paleogenomika_galang
```

3. Jalankan program:

```bat
python main.py
```

4. Jalankan pengujian:

```bat
python main.py --tests
```

5. Jalankan simulasi skenario terbaik dan terburuk:

```bat
python main.py --benchmark
```

6. Menggunakan dataset lain:

```bat
python main.py --reference data\reference_dna.txt --patterns data\patterns.txt
```

7. Menjalankan versi rekursif untuk dataset kecil:

```bat
python main.py --algorithm recursive --sort recursive
```

Validasi rekursif dibatasi maksimal 700 karakter; pencarian rekursif dibatasi ketika gabungan panjang teks dan pola melebihi 700 karakter, untuk mengurangi risiko batas kedalaman rekursi Python. Untuk DNA referensi yang panjang, gunakan mode `iterative`.

## Arti hasil

- `Exact Match`: semua karakter fragmen sama.
- `End-Mutated`: seluruh karakter kecuali karakter terakhir sama; karakter terakhir berbeda.
- `Not Found`: tidak ada posisi yang memenuhi aturan.
- Indeks menggunakan **basis 0**, sehingga karakter pertama berada pada indeks 0.
- Jika terdapat beberapa kecocokan, program menampilkan semua indeks dan memilih kecocokan terbaik: skor terbesar, kemudian indeks terkecil.

## Algoritma

### KMP
KMP mencari prefix pola, yaitu seluruh karakter kecuali karakter paling kanan. Setelah prefix ditemukan, program memeriksa satu karakter di posisi akhir. Kompleksitas pencarian untuk satu pola adalah `O(n + m + z)`, disederhanakan menjadi `O(n + m)` karena `z <= n`, dengan `n` panjang DNA referensi, `m` panjang pola, dan `z` jumlah posisi yang cocok.

### Merge Sort
Mengurutkan `k` laporan berdasarkan skor kemiripan menurun dan indeks menaik. Kompleksitas waktu terbaik maupun terburuk adalah `O(k log k)` dan ruang tambahan `O(k)`.

## Batasan dan asumsi

1. Data input menggunakan huruf kapital A, C, G, dan T.
2. Toleransi mutasi hanya satu karakter dan hanya pada posisi paling kanan.
3. Tidak ada anotasi nama spesies atau nomor fosil pada dataset simulasi ini; karena itu program tidak mengarang informasi tersebut.
4. Data simulasi harus diganti dengan dataset resmi kelas untuk hasil final yang sesuai instruksi dosen.
