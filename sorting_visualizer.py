"""
Sorting Visualizer — Python + Tkinter
Algorithms: Bubble Sort · Merge Sort · Quick Sort · Heap Sort · Insertion Sort
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import time

# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────
WIDTH        = 1000
HEIGHT       = 520
BAR_AREA_H   = 400
BAR_AREA_Y   = 80
PANEL_W      = 220
CANVAS_W     = WIDTH - PANEL_W

DEFAULT_SIZE = 60
MIN_SIZE     = 10
MAX_SIZE     = 120

# Colour palette — dark terminal aesthetic (matches pathfinder)
BG        = "#0d1117"
PANEL_BG  = "#161b22"
BORDER    = "#30363d"
BAR_CLR   = "#1f6feb"        # default bar
CMP_CLR   = "#f85149"        # comparing (red)
SWAP_CLR  = "#3fb950"        # swapping (green)
SORTED_CLR= "#58a6ff"        # sorted / done
PIVOT_CLR = "#d29922"        # pivot (quicksort)
MERGE_CLR = "#a371f7"        # merge active
TEXT_CLR  = "#e6edf3"
MUTED     = "#8b949e"
ACCENT    = "#58a6ff"
BTN_BG    = "#21262d"
BTN_HOV   = "#30363d"
BTN_ACT   = "#388bfd"

ALGO_INFO = {
    "Bubble":    ("Bubble Sort",    "O(n²) time · O(1) space\nRepeatedly swaps adjacent elements.\nSimple but slow on large arrays."),
    "Insertion": ("Insertion Sort", "O(n²) time · O(1) space\nBuilds sorted portion one element\nat a time. Fast on nearly-sorted data."),
    "Quick":     ("Quick Sort",     "O(n log n) avg · O(n²) worst\nDivide & conquer with a pivot.\nFastest in practice on average."),
    "Merge":     ("Merge Sort",     "O(n log n) always · O(n) space\nDivide, sort halves, merge.\nGuaranteed performance, stable sort."),
    "Heap":      ("Heap Sort",      "O(n log n) always · O(1) space\nBuilds a max-heap, extracts max\nrepeatedly. In-place & consistent."),
}


# ──────────────────────────────────────────────
# SORTING GENERATORS  — yield (array_state, highlights, phase_label)
# highlights = list of (index, color)
# ──────────────────────────────────────────────

def bubble_sort(arr):
    a = arr[:]
    n = len(a)
    for i in range(n):
        for j in range(n - i - 1):
            yield a[:], [(j, CMP_CLR), (j+1, CMP_CLR)], f"Comparing [{j}] and [{j+1}]"
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                yield a[:], [(j, SWAP_CLR), (j+1, SWAP_CLR)], f"Swapping [{j}] ↔ [{j+1}]"
        yield a[:], [(n-i-1, SORTED_CLR)], f"Pass {i+1} complete"
    yield a[:], [(k, SORTED_CLR) for k in range(n)], "Sorted!"


def insertion_sort(arr):
    a = arr[:]
    n = len(a)
    yield a[:], [(0, SORTED_CLR)], "Starting — first element is trivially sorted"
    for i in range(1, n):
        key = a[i]
        j = i - 1
        yield a[:], [(i, PIVOT_CLR)], f"Inserting element at index {i} (value={key})"
        while j >= 0 and a[j] > key:
            yield a[:], [(j, CMP_CLR), (j+1, CMP_CLR)], f"Shifting [{j}] right"
            a[j+1] = a[j]
            j -= 1
            yield a[:], [(j+1, SWAP_CLR)], f"Moved to position {j+1}"
        a[j+1] = key
        yield a[:], [(k, SORTED_CLR) for k in range(i+1)], f"Inserted at position {j+1}"
    yield a[:], [(k, SORTED_CLR) for k in range(n)], "Sorted!"


def quick_sort(arr):
    a = arr[:]

    def _qs(lo, hi):
        if lo >= hi:
            return
        pivot = a[hi]
        yield a[:], [(hi, PIVOT_CLR)], f"Pivot = {pivot} at index {hi}"
        i = lo
        for j in range(lo, hi):
            yield a[:], [(j, CMP_CLR), (hi, PIVOT_CLR)], f"Comparing [{j}]={a[j]} with pivot={pivot}"
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                yield a[:], [(i, SWAP_CLR), (j, SWAP_CLR), (hi, PIVOT_CLR)], f"Swapping [{i}] ↔ [{j}]"
                i += 1
        a[i], a[hi] = a[hi], a[i]
        yield a[:], [(i, SORTED_CLR), (hi, SWAP_CLR)], f"Pivot placed at index {i}"
        yield from _qs(lo, i - 1)
        yield from _qs(i + 1, hi)

    yield from _qs(0, len(a) - 1)
    yield a[:], [(k, SORTED_CLR) for k in range(len(a))], "Sorted!"


def merge_sort(arr):
    a = arr[:]

    def _ms(lo, hi):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        yield a[:], [(k, MERGE_CLR) for k in range(lo, hi+1)], f"Splitting [{lo}..{hi}] → [{lo}..{mid}] + [{mid+1}..{hi}]"
        yield from _ms(lo, mid)
        yield from _ms(mid + 1, hi)
        # merge
        left  = a[lo:mid+1]
        right = a[mid+1:hi+1]
        i = j = 0
        k = lo
        while i < len(left) and j < len(right):
            yield a[:], [(k, CMP_CLR)], f"Merging: comparing {left[i]} and {right[j]}"
            if left[i] <= right[j]:
                a[k] = left[i]; i += 1
            else:
                a[k] = right[j]; j += 1
            yield a[:], [(k, MERGE_CLR)], f"Placed {a[k]} at [{k}]"
            k += 1
        while i < len(left):
            a[k] = left[i]; i += 1
            yield a[:], [(k, MERGE_CLR)], f"Copying remaining left: {a[k]}"
            k += 1
        while j < len(right):
            a[k] = right[j]; j += 1
            yield a[:], [(k, MERGE_CLR)], f"Copying remaining right: {a[k]}"
            k += 1
        yield a[:], [(x, SORTED_CLR) for x in range(lo, hi+1)], f"Merged [{lo}..{hi}]"

    yield from _ms(0, len(a) - 1)
    yield a[:], [(k, SORTED_CLR) for k in range(len(a))], "Sorted!"


def heap_sort(arr):
    a = arr[:]
    n = len(a)

    def heapify(n, i):
        largest = i
        l, r = 2*i+1, 2*i+2
        if l < n:
            yield a[:], [(i, CMP_CLR), (l, CMP_CLR)], f"Heapify: comparing [{i}] and left child [{l}]"
            if a[l] > a[largest]:
                largest = l
        if r < n:
            yield a[:], [(i, CMP_CLR), (r, CMP_CLR)], f"Heapify: comparing [{i}] and right child [{r}]"
            if a[r] > a[largest]:
                largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            yield a[:], [(i, SWAP_CLR), (largest, SWAP_CLR)], f"Swap [{i}] ↔ [{largest}]"
            yield from heapify(n, largest)

    # Build max-heap
    yield a[:], [], "Building max-heap…"
    for i in range(n//2 - 1, -1, -1):
        yield from heapify(n, i)
    yield a[:], [], "Max-heap built — extracting elements"

    # Extract
    for i in range(n-1, 0, -1):
        a[0], a[i] = a[i], a[0]
        yield a[:], [(0, SWAP_CLR), (i, SORTED_CLR)], f"Extracted max → position {i}"
        yield from heapify(i, 0)
        yield a[:], [(i, SORTED_CLR)], f"Position {i} finalised"

    yield a[:], [(k, SORTED_CLR) for k in range(n)], "Sorted!"


ALGORITHMS = {
    "Bubble":    bubble_sort,
    "Insertion": insertion_sort,
    "Quick":     quick_sort,
    "Merge":     merge_sort,
    "Heap":      heap_sort,
}


# ──────────────────────────────────────────────
# APP
# ──────────────────────────────────────────────
class SortingVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sorting Visualizer")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.array       = []
        self.algo        = tk.StringVar(value="Bubble")
        self.size_var    = tk.IntVar(value=DEFAULT_SIZE)
        self.speed_var   = tk.IntVar(value=30)   # ms delay
        self.running     = False
        self._after_id   = None
        self._gen        = None
        self._comparisons= 0
        self._swaps      = 0
        self._start_time = None

        self._build_ui()
        self._new_array()

    # ── UI ───────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG, pady=8)
        hdr.pack(fill="x", padx=16)
        tk.Label(hdr, text="⬡ SORTING VISUALIZER", bg=BG, fg=ACCENT,
                 font=("Courier New", 16, "bold")).pack(side="left")
        tk.Label(hdr, text="Bubble · Insertion · Quick · Merge · Heap",
                 bg=BG, fg=MUTED, font=("Courier New", 9)).pack(side="left", padx=12)

        # Main layout
        main = tk.Frame(self, bg=BG)
        main.pack(padx=14, pady=4)

        # Canvas
        self.canvas = tk.Canvas(main, width=CANVAS_W, height=HEIGHT,
                                bg=BG, highlightthickness=1,
                                highlightbackground=BORDER)
        self.canvas.pack(side="left")

        # Panel
        panel = tk.Frame(main, bg=PANEL_BG, width=PANEL_W, padx=14, pady=14,
                         highlightthickness=1, highlightbackground=BORDER)
        panel.pack(side="left", fill="y", padx=(10,0))
        panel.pack_propagate(False)
        self._build_panel(panel)

        # Status bar
        self.status_var = tk.StringVar(value="Ready — generate an array and hit Sort!")
        sb = tk.Frame(self, bg=PANEL_BG, pady=6,
                      highlightthickness=1, highlightbackground=BORDER)
        sb.pack(fill="x", padx=14, pady=(4,10))
        tk.Label(sb, textvariable=self.status_var, bg=PANEL_BG, fg=TEXT_CLR,
                 font=("Courier New", 9), anchor="w").pack(side="left", padx=10)
        self.stat_right = tk.Label(sb, text="", bg=PANEL_BG, fg=MUTED,
                                   font=("Courier New", 9))
        self.stat_right.pack(side="right", padx=10)

    def _build_panel(self, p):
        def section(label):
            tk.Label(p, text=label, bg=PANEL_BG, fg=MUTED,
                     font=("Courier New", 7, "bold")).pack(anchor="w", pady=(10,2))

        # Algorithm
        section("ALGORITHM")
        for name in ALGORITHMS:
            rb = tk.Radiobutton(p, text=name, variable=self.algo, value=name,
                                bg=PANEL_BG, fg=TEXT_CLR, selectcolor=PANEL_BG,
                                activebackground=PANEL_BG, activeforeground=ACCENT,
                                font=("Courier New", 9), indicatoron=False,
                                relief="flat", bd=0, cursor="hand2", pady=3, padx=8,
                                command=self._update_info)
            rb.pack(fill="x", pady=1)
            rb.bind("<Enter>", lambda e, b=rb: b.configure(fg=ACCENT))
            rb.bind("<Leave>", lambda e, b=rb: b.configure(fg=TEXT_CLR))

        # Info box
        self.info_title = tk.Label(p, text="", bg=PANEL_BG, fg=ACCENT,
                                   font=("Courier New", 8, "bold"),
                                   wraplength=190, justify="left")
        self.info_title.pack(anchor="w", pady=(6,0))
        self.info_body  = tk.Label(p, text="", bg=PANEL_BG, fg=MUTED,
                                   font=("Courier New", 7), wraplength=190, justify="left")
        self.info_body.pack(anchor="w")
        self._update_info()

        # Array size
        section("ARRAY SIZE")
        size_row = tk.Frame(p, bg=PANEL_BG)
        size_row.pack(fill="x")
        tk.Label(size_row, text="10", bg=PANEL_BG, fg=MUTED,
                 font=("Courier New", 7)).pack(side="left")
        tk.Scale(size_row, from_=MIN_SIZE, to=MAX_SIZE, orient="horizontal",
                 variable=self.size_var, bg=PANEL_BG, fg=TEXT_CLR,
                 troughcolor=BTN_BG, highlightthickness=0,
                 showvalue=True, length=140, command=lambda _: self._new_array()
                 ).pack(side="left", padx=4)
        tk.Label(size_row, text="120", bg=PANEL_BG, fg=MUTED,
                 font=("Courier New", 7)).pack(side="left")

        # Speed
        section("SPEED")
        spd_row = tk.Frame(p, bg=PANEL_BG)
        spd_row.pack(fill="x")
        tk.Label(spd_row, text="Fast", bg=PANEL_BG, fg=MUTED,
                 font=("Courier New", 7)).pack(side="left")
        tk.Scale(spd_row, from_=1, to=200, orient="horizontal",
                 variable=self.speed_var, bg=PANEL_BG, fg=TEXT_CLR,
                 troughcolor=BTN_BG, highlightthickness=0,
                 showvalue=False, length=110).pack(side="left", padx=4)
        tk.Label(spd_row, text="Slow", bg=PANEL_BG, fg=MUTED,
                 font=("Courier New", 7)).pack(side="left")

        # Controls
        section("CONTROLS")
        self.sort_btn = self._button(p, "▶  SORT",        self._start_sort, bg=BTN_ACT)
        self._button(p, "↺  NEW ARRAY",   self._new_array)
        self._button(p, "⊘  STOP",        self._stop)

        # Presets
        section("ARRAY PRESET")
        for label, fn in [("Random", self._new_array),
                           ("Nearly Sorted", self._nearly_sorted),
                           ("Reversed",      self._reversed),
                           ("Few Unique",    self._few_unique)]:
            self._button(p, label, fn)

        # Stats
        section("STATS")
        self.cmp_label  = tk.Label(p, text="Comparisons: —", bg=PANEL_BG, fg=MUTED,
                                   font=("Courier New", 8))
        self.cmp_label.pack(anchor="w")
        self.swap_label = tk.Label(p, text="Swaps/Writes: —", bg=PANEL_BG, fg=MUTED,
                                   font=("Courier New", 8))
        self.swap_label.pack(anchor="w")
        self.time_label = tk.Label(p, text="Time: —", bg=PANEL_BG, fg=MUTED,
                                   font=("Courier New", 8))
        self.time_label.pack(anchor="w")

        # Legend
        section("LEGEND")
        for clr, lbl in [(BAR_CLR, "Unsorted"), (CMP_CLR, "Comparing"),
                         (SWAP_CLR, "Swapping"), (PIVOT_CLR, "Pivot"),
                         (MERGE_CLR, "Merging"), (SORTED_CLR, "Sorted")]:
            row = tk.Frame(p, bg=PANEL_BG)
            row.pack(anchor="w", pady=1)
            tk.Canvas(row, width=12, height=12, bg=clr,
                      highlightthickness=0).pack(side="left", padx=(0,6))
            tk.Label(row, text=lbl, bg=PANEL_BG, fg=MUTED,
                     font=("Courier New", 7)).pack(side="left")

    def _button(self, parent, label, cmd, bg=BTN_BG):
        btn = tk.Button(parent, text=label, command=cmd, bg=bg, fg=TEXT_CLR,
                        activebackground=BTN_HOV, activeforeground=ACCENT,
                        font=("Courier New", 9, "bold"), relief="flat",
                        cursor="hand2", pady=5, bd=0)
        btn.pack(fill="x", pady=2)
        btn.bind("<Enter>", lambda e: btn.configure(bg=BTN_HOV))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    def _update_info(self):
        a = self.algo.get()
        title, body = ALGO_INFO.get(a, ("",""))
        self.info_title.config(text=title)
        self.info_body.config(text=body)

    # ── ARRAY PRESETS ────────────────────────────
    def _new_array(self, _=None):
        if self.running: return
        n = self.size_var.get()
        self.array = [random.randint(5, 100) for _ in range(n)]
        self._reset_stats()
        self._draw(self.array, [])
        self.status_var.set("Random array generated — ready to sort")

    def _nearly_sorted(self):
        if self.running: return
        n = self.size_var.get()
        self.array = list(range(1, n+1))
        swaps = max(1, n//10)
        for _ in range(swaps):
            i, j = random.randrange(n), random.randrange(n)
            self.array[i], self.array[j] = self.array[j], self.array[i]
        self._reset_stats()
        self._draw(self.array, [])
        self.status_var.set("Nearly-sorted array — Insertion Sort shines here!")

    def _reversed(self):
        if self.running: return
        n = self.size_var.get()
        self.array = list(range(n, 0, -1))
        self._reset_stats()
        self._draw(self.array, [])
        self.status_var.set("Reversed array — Bubble Sort's worst case!")

    def _few_unique(self):
        if self.running: return
        n = self.size_var.get()
        vals = [10, 30, 50, 70, 90]
        self.array = [random.choice(vals) for _ in range(n)]
        self._reset_stats()
        self._draw(self.array, [])
        self.status_var.set("Few unique values — interesting for Quick Sort!")

    def _reset_stats(self):
        self._comparisons = 0
        self._swaps = 0
        self._start_time = None
        self.cmp_label.config(text="Comparisons: —")
        self.swap_label.config(text="Swaps/Writes: —")
        self.time_label.config(text="Time: —")
        self.stat_right.config(text="")

    # ── DRAWING ──────────────────────────────────
    def _draw(self, arr, highlights):
        self.canvas.delete("all")
        n = len(arr)
        if n == 0: return

        # Draw grid lines (subtle)
        for pct in [0.25, 0.5, 0.75, 1.0]:
            y = BAR_AREA_Y + BAR_AREA_H * (1 - pct)
            self.canvas.create_line(0, y, CANVAS_W, y,
                                    fill=BORDER, width=1, dash=(2,6))
            self.canvas.create_text(4, y, text=f"{int(pct*100)}",
                                    anchor="nw", fill=MUTED,
                                    font=("Courier New", 7))

        bar_w   = CANVAS_W / n
        gap     = max(1, int(bar_w * 0.15))
        max_val = max(arr) if arr else 1

        # Build highlight index map
        hi_map = {}
        for idx, clr in highlights:
            if 0 <= idx < n:
                hi_map[idx] = clr

        for i, val in enumerate(arr):
            x1 = i * bar_w + gap
            x2 = (i+1) * bar_w - gap
            bar_h = int((val / max_val) * (BAR_AREA_H - 10))
            y1 = BAR_AREA_Y + BAR_AREA_H - bar_h
            y2 = BAR_AREA_Y + BAR_AREA_H

            clr = hi_map.get(i, BAR_CLR)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=clr, outline="")

            # Value label on top of bar (only if bars wide enough)
            if bar_w >= 14:
                self.canvas.create_text((x1+x2)/2, y1-4, text=str(val),
                                        fill=MUTED, font=("Courier New", 7),
                                        anchor="s")

        # Array size label
        self.canvas.create_text(CANVAS_W - 8, BAR_AREA_Y - 12,
                                 text=f"n = {n}", fill=MUTED,
                                 font=("Courier New", 8), anchor="e")

    # ── SORT CONTROL ─────────────────────────────
    def _start_sort(self):
        if self.running: return
        if not self.array:
            self.status_var.set("⚠  Generate an array first!")
            return
        self.running = True
        self.sort_btn.config(state="disabled")
        self._comparisons = 0
        self._swaps = 0
        self._start_time = time.perf_counter()

        algo_fn = ALGORITHMS[self.algo.get()]
        self._gen = algo_fn(self.array[:])
        self._step()

    def _step(self):
        if not self.running:
            return
        try:
            arr_state, highlights, phase = next(self._gen)
            # Count comparisons and swaps from highlights
            for _, clr in highlights:
                if clr == CMP_CLR:
                    self._comparisons += 1
                elif clr in (SWAP_CLR, MERGE_CLR):
                    self._swaps += 1
            self._draw(arr_state, highlights)
            self.status_var.set(phase)
            self.cmp_label.config(text=f"Comparisons: {self._comparisons:,}")
            self.swap_label.config(text=f"Swaps/Writes: {self._swaps:,}")
            elapsed = time.perf_counter() - self._start_time
            self.time_label.config(text=f"Time: {elapsed*1000:.0f}ms")
            delay = self.speed_var.get()
            self._after_id = self.after(delay, self._step)
        except StopIteration:
            self._finish()

    def _finish(self):
        elapsed = time.perf_counter() - self._start_time if self._start_time else 0
        self.running = False
        self.sort_btn.config(state="normal")
        n = self.size_var.get()
        algo = self.algo.get()
        self.status_var.set(f"✓ {algo} Sort complete on {n} elements!")
        self.stat_right.config(
            text=f"{self._comparisons:,} comparisons · {self._swaps:,} writes · {elapsed*1000:.1f}ms")

    def _stop(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.running = False
        self.sort_btn.config(state="normal")
        self.status_var.set("Stopped — generate a new array or hit Sort again")


# ──────────────────────────────────────────────
# ENTRY
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = SortingVisualizer()
    app.mainloop()