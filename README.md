# PROYEK 1 - DESAIN DAN ANALISIS ALGORITMA

## Pemetaan Fragmen DNA Kuno (Paleogenomika)

Nama: M. Galang Setyawan
Program Studi: Teknik Informatika
Mata Kuliah: Desain dan Analisis Algoritma

## Deskripsi Proyek

Proyek ini merupakan implementasi algoritma untuk
mencari fragmen DNA kuno di dalam DNA referensi.

Program menggunakan toleransi satu perbedaan
karakter pada bagian ujung kanan fragmen.

## Algoritma

1. KMP (Knuth-Morris-Pratt)
   Untuk mencari fragmen DNA.

2. Merge Sort
   Untuk mengurutkan hasil berdasarkan skor
   kemiripan tertinggi dan indeks terkecil.

3. Object Oriented Programming
   Untuk menyusun struktur program Python.

## Struktur Folder

- main.py
- data/reference_dna.txt
- data/patterns.txt
- docs/
- results/

## Cara Menjalankan

Jalankan program:

python main.py

Pengujian:

python main.py --tests

Benchmark:

python main.py --benchmark

## Hasil Pengujian

10 dari 10 pengujian berhasil pada
dataset simulasi yang digunakan.

## Catatan Dataset

Dataset yang digunakan pada demonstrasi awal
merupakan dataset simulasi 120 karakter.
Dataset ini dapat diganti dengan dataset resmi
kelas apabila diperlukan.
