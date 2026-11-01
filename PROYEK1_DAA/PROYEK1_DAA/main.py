"""Proyek 1 DAA: Pemetaan Fragmen DNA Kuno dengan KMP dan Merge Sort.

Program ini menggunakan KMP untuk mencari prefix pattern (semua karakter
kecuali karakter terakhir), lalu memeriksa karakter paling kanan untuk
menerima exact match atau maksimal satu mutasi di ujung kanan.

Tidak memakai str.find(), str.index(), re, sorted(), atau list.sort().
Dataset bawaan adalah data simulasi untuk demonstrasi, bukan DNA fosil asli.
"""

from __future__ import annotations

import argparse
import time
import tracemalloc
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class OperationCounter:
    """Menghitung perbandingan karakter pada proses validasi dan pencarian."""

    character_comparisons: int = 0
    ordering_comparisons: int = 0


@dataclass
class Match:
    index: int
    similarity: float
    status: str


@dataclass
class SearchResult:
    pattern: str
    matches: List[Match]

    @property
    def best_match(self) -> Optional[Match]:
        if len(self.matches) == 0:
            return None
        best = self.matches[0]
        for candidate in self.matches[1:]:
            if candidate.similarity > best.similarity:
                best = candidate
            elif candidate.similarity == best.similarity and candidate.index < best.index:
                best = candidate
        return best

    @property
    def best_score(self) -> float:
        best = self.best_match
        return best.similarity if best is not None else 0.0

    @property
    def best_index(self) -> Optional[int]:
        best = self.best_match
        return best.index if best is not None else None

    @property
    def best_status(self) -> str:
        best = self.best_match
        return best.status if best is not None else "Not Found"


class DNAValidator:
    """Memvalidasi alfabet DNA A, C, G, dan T."""

    ALPHABET = "ACGT"

    @classmethod
    def validate_iterative(cls, sequence: str, label: str, counter: OperationCounter) -> None:
        if sequence == "":
            raise ValueError(f"{label} tidak boleh kosong.")
        for position, character in enumerate(sequence):
            counter.character_comparisons += 1
            if character not in cls.ALPHABET:
                raise ValueError(
                    f"{label} tidak valid: karakter '{character}' pada posisi {position}. "
                    "Gunakan hanya A, C, G, dan T."
                )

    @classmethod
    def validate_recursive(cls, sequence: str, label: str, counter: OperationCounter) -> None:
        if sequence == "":
            raise ValueError(f"{label} tidak boleh kosong.")
        if len(sequence) > 700:
            raise ValueError(
                "Validasi rekursif dibatasi untuk input maksimal 700 karakter agar aman "
                "dari batas stack Python. Gunakan mode iterative untuk data panjang."
            )

        def check(position: int) -> None:
            if position >= len(sequence):
                return
            counter.character_comparisons += 1
            if sequence[position] not in cls.ALPHABET:
                raise ValueError(
                    f"{label} tidak valid: karakter '{sequence[position]}' "
                    f"pada posisi {position}. Gunakan hanya A, C, G, dan T."
                )
            check(position + 1)

        check(0)


class KMPMatcher:
    """KMP untuk prefix pattern, dilanjutkan pemeriksaan karakter terakhir."""

    @staticmethod
    def build_lps_iterative(pattern: str, counter: OperationCounter) -> List[int]:
        lps = [0] * len(pattern)
        length = 0
        position = 1

        while position < len(pattern):
            counter.character_comparisons += 1
            if pattern[position] == pattern[length]:
                length += 1
                lps[position] = length
                position += 1
            elif length != 0:
                length = lps[length - 1]
            else:
                lps[position] = 0
                position += 1
        return lps

    @staticmethod
    def build_lps_recursive(pattern: str, counter: OperationCounter) -> List[int]:
        lps = [0] * len(pattern)

        def fill(position: int, length: int) -> None:
            if position >= len(pattern):
                return
            if length > 0:
                counter.character_comparisons += 1
                if pattern[position] != pattern[length]:
                    fill(position, lps[length - 1])
                    return
                length += 1
            else:
                counter.character_comparisons += 1
                if pattern[position] == pattern[0]:
                    length = 1
            lps[position] = length
            fill(position + 1, length)

        if len(pattern) > 700:
            raise ValueError("Pembuatan LPS rekursif dibatasi untuk pola maksimal 700 karakter.")
        if len(pattern) > 1:
            fill(1, 0)
        return lps

    @staticmethod
    def _make_match(text: str, pattern: str, start: int, counter: OperationCounter) -> Match:
        final_position = start + len(pattern) - 1
        counter.character_comparisons += 1
        if text[final_position] == pattern[-1]:
            return Match(start, 100.0, "Exact Match")
        score = ((len(pattern) - 1) / len(pattern)) * 100.0
        return Match(start, score, "End-Mutated")

    def search_iterative(
        self, text: str, pattern: str, counter: OperationCounter
    ) -> List[Match]:
        """Mencari seluruh posisi yang cocok, termasuk overlap."""
        matches: List[Match] = []
        if len(pattern) == 1:
            for position in range(len(text)):
                counter.character_comparisons += 1
                if text[position] == pattern[0]:
                    matches.append(Match(position, 100.0, "Exact Match"))
                else:
                    matches.append(Match(position, 0.0, "End-Mutated"))
            return matches

        prefix = pattern[:-1]
        lps = self.build_lps_iterative(prefix, counter)
        matched = 0

        for position in range(len(text)):
            while matched > 0:
                counter.character_comparisons += 1
                if text[position] == prefix[matched]:
                    matched += 1
                    break
                matched = lps[matched - 1]
            else:
                # Dijalankan jika matched sejak awal 0 atau fallback mencapai 0.
                counter.character_comparisons += 1
                if text[position] == prefix[0]:
                    matched = 1

            if matched == len(prefix):
                start = position - len(prefix) + 1
                final_position = start + len(pattern) - 1
                if final_position < len(text):
                    matches.append(self._make_match(text, pattern, start, counter))
                matched = lps[matched - 1]
        return matches

    def search_recursive(
        self, text: str, pattern: str, counter: OperationCounter
    ) -> List[Match]:
        """Versi rekursif untuk demonstrasi pada data kecil saja."""
        if len(text) + len(pattern) > 700:
            raise ValueError(
                "Pencarian rekursif dibatasi untuk gabungan panjang teks dan pola maksimal "
                "700 karakter. Gunakan mode iterative untuk dataset panjang."
            )

        matches: List[Match] = []
        if len(pattern) == 1:
            def scan_single(position: int) -> None:
                if position >= len(text):
                    return
                counter.character_comparisons += 1
                if text[position] == pattern[0]:
                    matches.append(Match(position, 100.0, "Exact Match"))
                else:
                    matches.append(Match(position, 0.0, "End-Mutated"))
                scan_single(position + 1)

            scan_single(0)
            return matches

        prefix = pattern[:-1]
        lps = self.build_lps_recursive(prefix, counter)

        def scan(position: int, matched: int) -> None:
            if position >= len(text):
                return
            if matched > 0:
                counter.character_comparisons += 1
                if text[position] != prefix[matched]:
                    scan(position, lps[matched - 1])
                    return
                matched += 1
            else:
                counter.character_comparisons += 1
                if text[position] == prefix[0]:
                    matched = 1

            if matched == len(prefix):
                start = position - len(prefix) + 1
                final_position = start + len(pattern) - 1
                if final_position < len(text):
                    matches.append(self._make_match(text, pattern, start, counter))
                matched = lps[matched - 1]
            scan(position + 1, matched)

        scan(0, 0)
        return matches


class MergeSorter:
    """Merge Sort rekursif dan iteratif tanpa sorted() atau list.sort()."""

    @staticmethod
    def comes_before(left: SearchResult, right: SearchResult, counter: OperationCounter) -> bool:
        counter.ordering_comparisons += 1
        if left.best_score != right.best_score:
            return left.best_score > right.best_score
        left_index = left.best_index
        right_index = right.best_index
        if left_index is None and right_index is not None:
            return False
        if left_index is not None and right_index is None:
            return True
        if left_index is not None and right_index is not None and left_index != right_index:
            return left_index < right_index
        return False  # stabil: urutan awal dipertahankan jika seluruh kunci sama

    def sort_recursive(self, items: List[SearchResult], counter: OperationCounter) -> List[SearchResult]:
        if len(items) <= 1:
            return items[:]
        middle = len(items) // 2
        left = self.sort_recursive(items[:middle], counter)
        right = self.sort_recursive(items[middle:], counter)
        return self._merge(left, right, counter)

    def sort_iterative(self, items: List[SearchResult], counter: OperationCounter) -> List[SearchResult]:
        result = items[:]
        width = 1
        size = len(result)
        while width < size:
            merged: List[SearchResult] = []
            start = 0
            while start < size:
                middle = min(start + width, size)
                end = min(start + 2 * width, size)
                left = result[start:middle]
                right = result[middle:end]
                merged.extend(self._merge(left, right, counter))
                start += 2 * width
            result = merged
            width *= 2
        return result

    def _merge(
        self, left: List[SearchResult], right: List[SearchResult], counter: OperationCounter
    ) -> List[SearchResult]:
        merged: List[SearchResult] = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            if self.comes_before(left[i], right[j], counter):
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        while i < len(left):
            merged.append(left[i])
            i += 1
        while j < len(right):
            merged.append(right[j])
            j += 1
        return merged


class DNAProject:
    """Orkestrasi validasi, pencarian fragmen, dan pengurutan laporan."""

    def __init__(self) -> None:
        self.validator = DNAValidator()
        self.matcher = KMPMatcher()
        self.sorter = MergeSorter()

    def run(
        self,
        reference: str,
        patterns: List[str],
        algorithm: str = "iterative",
        sort_method: str = "iterative",
    ) -> tuple[List[SearchResult], OperationCounter]:
        counter = OperationCounter()
        if algorithm == "recursive":
            self.validator.validate_recursive(reference, "DNA referensi", counter)
        else:
            self.validator.validate_iterative(reference, "DNA referensi", counter)
        if len(patterns) == 0:
            raise ValueError("Daftar pola DNA tidak boleh kosong.")

        results: List[SearchResult] = []
        for number, pattern in enumerate(patterns, start=1):
            if algorithm == "recursive":
                self.validator.validate_recursive(pattern, f"Pola ke-{number}", counter)
                found = self.matcher.search_recursive(reference, pattern, counter)
            else:
                self.validator.validate_iterative(pattern, f"Pola ke-{number}", counter)
                found = self.matcher.search_iterative(reference, pattern, counter)
            results.append(SearchResult(pattern, found))

        if sort_method == "recursive":
            results = self.sorter.sort_recursive(results, counter)
        else:
            results = self.sorter.sort_iterative(results, counter)
        return results, counter


def read_reference(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File DNA referensi tidak ditemukan: {path}")
    pieces: List[str] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            pieces.append(line.strip())
    return "".join(pieces)


def read_patterns(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"File pola DNA tidak ditemukan: {path}")
    patterns: List[str] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            pattern = line.strip()
            if pattern != "":
                patterns.append(pattern)
    return patterns


def print_report(results: List[SearchResult], counter: OperationCounter) -> None:
    print("\n=== HASIL PEMETAAN FRAGMEN DNA KUNO ===")
    for number, result in enumerate(results, start=1):
        print(f"\n{number}. Pola: {result.pattern}")
        if result.best_match is None:
            print("   Indeks terbaik (0-based): -")
            print("   Semua indeks: []")
            print("   Jumlah kemunculan: 0")
            print("   Skor kemiripan: 0.0% (0/{})".format(len(result.pattern)))
            print("   Status: Not Found")
        else:
            best = result.best_match
            indices = [hit.index for hit in result.matches]
            print(f"   Indeks terbaik (0-based): {best.index}")
            print(f"   Semua indeks: {indices}")
            print(f"   Jumlah kemunculan: {len(result.matches)}")
            same_count = int(round(best.similarity / 100.0 * len(result.pattern)))
            print(f"   Skor kemiripan: {best.similarity:.1f}% ({same_count}/{len(result.pattern)})")
            print(f"   Status: {best.status}")
    print("\nMetrik Eksekusi:")
    print(f"- Perbandingan karakter: {counter.character_comparisons}")
    print(f"- Perbandingan pengurutan: {counter.ordering_comparisons}")


def run_tests() -> bool:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProjectTests)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    return outcome.wasSuccessful()


def _measure_kmp(label: str, algorithm: str, text: str, pattern: str) -> None:
    """Ukur waktu, memori, dan operasi KMP untuk satu skenario."""
    matcher = KMPMatcher()
    counter = OperationCounter()
    tracemalloc.start()
    start_time = time.perf_counter()
    if algorithm == "recursive":
        matches = matcher.search_recursive(text, pattern, counter)
    else:
        matches = matcher.search_iterative(text, pattern, counter)
    elapsed = time.perf_counter() - start_time
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  Metode             : {algorithm}")
    print(f"  Panjang teks       : {len(text)} karakter")
    print(f"  Panjang pola       : {len(pattern)} karakter")
    print(f"  Jumlah kecocokan   : {len(matches)}")
    print(f"  Perbandingan       : {counter.character_comparisons}")
    print(f"  Waktu              : {elapsed:.6f} detik")
    print(f"  Memori puncak      : {peak_bytes / 1024:.2f} KiB")
    print(f"  Memori saat akhir  : {current_bytes / 1024:.2f} KiB")


def _make_sort_items(size: int, reverse_input: bool) -> List[SearchResult]:
    """Buat data uji urut/terbalik untuk mengukur Merge Sort."""
    items: List[SearchResult] = []
    for position in range(size):
        if reverse_input:
            score = 100.0 * (position + 1) / size
        else:
            score = 100.0 * (size - position) / size
        items.append(
            SearchResult(
                pattern=f"PATTERN_{position:04d}",
                matches=[Match(position, score, "Exact Match")],
            )
        )
    return items


def _measure_merge_sort(label: str, method: str, items: List[SearchResult]) -> None:
    """Ukur waktu, memori, dan jumlah perbandingan Merge Sort."""
    sorter = MergeSorter()
    counter = OperationCounter()
    tracemalloc.start()
    start_time = time.perf_counter()
    if method == "recursive":
        ordered = sorter.sort_recursive(items, counter)
    else:
        ordered = sorter.sort_iterative(items, counter)
    elapsed = time.perf_counter() - start_time
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    check_counter = OperationCounter()
    order_is_correct = True
    for position in range(1, len(ordered)):
        if sorter.comes_before(ordered[position], ordered[position - 1], check_counter):
            order_is_correct = False
            break

    print(f"  Metode             : {method}")
    print(f"  Jumlah data        : {len(items)}")
    print(f"  Perbandingan       : {counter.ordering_comparisons}")
    print(f"  Waktu              : {elapsed:.6f} detik")
    print(f"  Memori puncak      : {peak_bytes / 1024:.2f} KiB")
    print(f"  Urutan benar       : {'Ya' if order_is_correct else 'Tidak'}")


def run_benchmarks() -> None:
    """Bandingkan iteratif dan rekursif pada ukuran aman, lalu uji skala besar."""
    print("\n=== BENCHMARK KMP: ITERATIF VS REKURSIF ===")
    print("Perbandingan yang adil menggunakan teks dan pola berukuran sama.")

    for size in (100, 300, 600):
        small_cases = [
            ("Terbaik (tidak ada prefix yang cocok)", "C" * size, "A" * 15 + "G"),
            ("Terburuk (banyak prefix cocok/kandidat)", "A" * size, "A" * 15 + "G"),
        ]
        for label, text, pattern in small_cases:
            print(f"\n{label} — panjang teks {size}, pola 16 karakter")
            _measure_kmp(label, "iterative", text, pattern)
            _measure_kmp(label, "recursive", text, pattern)

    print("\n=== BENCHMARK MERGE SORT: ITERATIF VS REKURSIF ===")
    print("Merge Sort diuji pada data terurut dan terbalik; keduanya tetap O(n log n).")
    for size in (100, 300, 600):
        for label, reverse_input in (("Terbaik (data sudah terurut)", False), ("Data terbalik", True)):
            print(f"\n{label} — jumlah data {size}")
            items = _make_sort_items(size, reverse_input)
            _measure_merge_sort(label, "iterative", items)
            _measure_merge_sort(label, "recursive", items)

    print("\n=== UJI SKALABILITAS KMP ITERATIF ===")
    print("Input besar hanya diuji dengan iteratif karena rekursi dibatasi untuk keamanan stack Python.")
    large_cases = [
        ("Terbaik (tidak ada prefix yang cocok)", "C" * 20000, "A" * 15 + "G"),
        ("Terburuk (banyak prefix cocok/kandidat)", "A" * 20000, "A" * 15 + "G"),
    ]
    for label, text, pattern in large_cases:
        print(f"\n{label}")
        _measure_kmp(label, "iterative", text, pattern)


class ProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.matcher = KMPMatcher()
        self.project = DNAProject()

    def test_exact_match(self) -> None:
        counter = OperationCounter()
        hits = self.matcher.search_iterative("GGGACGTAAA", "ACGT", counter)
        self.assertEqual([hit.index for hit in hits], [3])
        self.assertEqual(hits[0].status, "Exact Match")
        self.assertEqual(hits[0].similarity, 100.0)

    def test_one_mutation_at_right_end(self) -> None:
        counter = OperationCounter()
        hits = self.matcher.search_iterative("GGGACGAAAA", "ACGT", counter)
        self.assertEqual([hit.index for hit in hits], [3])
        self.assertEqual(hits[0].status, "End-Mutated")
        self.assertAlmostEqual(hits[0].similarity, 75.0)

    def test_not_found(self) -> None:
        counter = OperationCounter()
        hits = self.matcher.search_iterative("ACGTACGT", "TTTT", counter)
        self.assertEqual(hits, [])

    def test_overlapping_occurrences(self) -> None:
        counter = OperationCounter()
        hits = self.matcher.search_iterative("AAAAAA", "AAA", counter)
        self.assertEqual([hit.index for hit in hits], [0, 1, 2, 3])

    def test_recursive_equals_iterative(self) -> None:
        text = "GGGACGTACGAAAACTTACGT"
        pattern = "ACGT"
        iterative = self.matcher.search_iterative(text, pattern, OperationCounter())
        recursive = self.matcher.search_recursive(text, pattern, OperationCounter())
        self.assertEqual(
            [(m.index, m.status, m.similarity) for m in iterative],
            [(m.index, m.status, m.similarity) for m in recursive],
        )

    def test_sorting_score_then_index(self) -> None:
        data = [
            SearchResult("p1", [Match(10, 93.75, "End-Mutated")]),
            SearchResult("p2", [Match(2, 100.0, "Exact Match")]),
            SearchResult("p3", []),
            SearchResult("p4", [Match(5, 100.0, "Exact Match")]),
        ]
        sorter = MergeSorter()
        ordered = sorter.sort_iterative(data, OperationCounter())
        self.assertEqual([item.pattern for item in ordered], ["p2", "p4", "p1", "p3"])

    def test_invalid_alphabet(self) -> None:
        with self.assertRaises(ValueError):
            self.project.run("ACGTNX", ["ACGT"])

    def test_recursive_validator(self) -> None:
        counter = OperationCounter()
        DNAValidator.validate_recursive("ACGTAC", "uji", counter)
        self.assertEqual(counter.character_comparisons, 6)
        with self.assertRaises(ValueError):
            DNAValidator.validate_recursive("ACNT", "uji", OperationCounter())

    def test_recursive_sort_matches_iterative(self) -> None:
        data = [
            SearchResult("p1", [Match(10, 93.75, "End-Mutated")]),
            SearchResult("p2", [Match(2, 100.0, "Exact Match")]),
            SearchResult("p3", []),
            SearchResult("p4", [Match(5, 100.0, "Exact Match")]),
        ]
        sorter = MergeSorter()
        iterative = sorter.sort_iterative(data, OperationCounter())
        recursive = sorter.sort_recursive(data, OperationCounter())
        self.assertEqual([item.pattern for item in iterative], [item.pattern for item in recursive])

    def test_recursive_pipeline(self) -> None:
        reference = "GGGCTTCGGGCAACTTAACCCCCTGGCACAAACCGTTAAA"
        patterns = ["CTTCGGGCAACTTAAC", "CTGGCACAAACCGTTG", "TTTTTTTTTTTTTTTT"]
        results, _ = self.project.run(reference, patterns, "recursive", "recursive")
        self.assertEqual([item.pattern for item in results], patterns)
        self.assertEqual(results[0].best_status, "Exact Match")
        self.assertEqual(results[1].best_status, "End-Mutated")
        self.assertEqual(results[2].best_status, "Not Found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pemetaan fragmen DNA kuno menggunakan KMP dan Merge Sort.")
    parser.add_argument("--reference", default=None, help="File teks DNA referensi (A/C/G/T saja).")
    parser.add_argument("--patterns", default=None, help="File teks: satu pola DNA per baris.")
    parser.add_argument("--algorithm", choices=["iterative", "recursive"], default="iterative")
    parser.add_argument("--sort", choices=["iterative", "recursive"], default="iterative")
    parser.add_argument("--tests", action="store_true", help="Jalankan unit test.")
    parser.add_argument("--benchmark", action="store_true", help="Jalankan simulasi skenario terbaik dan terburuk.")
    args = parser.parse_args()

    if args.tests:
        success = run_tests()
        if not success:
            raise SystemExit(1)
        return
    if args.benchmark:
        run_benchmarks()
        return

    base_directory = Path(__file__).resolve().parent
    reference_path = Path(args.reference) if args.reference else base_directory / "data" / "reference_dna.txt"
    patterns_path = Path(args.patterns) if args.patterns else base_directory / "data" / "patterns.txt"
    reference = read_reference(reference_path)
    patterns = read_patterns(patterns_path)
    project = DNAProject()
    results, counter = project.run(reference, patterns, args.algorithm, args.sort)
    print(f"DNA referensi: {len(reference)} karakter")
    print(f"Jumlah pola  : {len(patterns)}")
    print(f"Mode pencarian: {args.algorithm}; mode pengurutan: {args.sort}")
    print_report(results, counter)


if __name__ == "__main__":
    main()
