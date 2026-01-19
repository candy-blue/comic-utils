import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import sys

from src.modules.ebook_to_cbz.converter import ConvertError, convert_to_cbz

class EbookTab(ttk.Frame):
  def __init__(self, parent):
    super().__init__(parent)
    
    self.output_dir = tk.StringVar(value=str(Path.cwd()))
    self.status = tk.StringVar(value="Ready")
    self.is_working = False
    self._job_total = 0
    self._job_done = 0

    self.columnconfigure(0, weight=1)
    self.rowconfigure(1, weight=1)

    self._build_ui()

  def _build_ui(self):
    top = ttk.Frame(self, padding=10)
    top.grid(row=0, column=0, sticky="ew")
    top.columnconfigure(1, weight=1)

    ttk.Label(top, text="Output Dir:").grid(row=0, column=0, sticky="w")
    ttk.Entry(top, textvariable=self.output_dir).grid(row=0, column=1, sticky="ew", padx=(8, 8))
    ttk.Button(top, text="Select", command=self.choose_output).grid(row=0, column=2, sticky="e")
    ttk.Button(top, text="Open", command=self.open_output_dir).grid(row=0, column=3, sticky="e", padx=(8, 0))

    mid = ttk.Frame(self, padding=(10, 0, 10, 0))
    mid.grid(row=1, column=0, sticky="nsew")
    mid.columnconfigure(0, weight=1)
    mid.rowconfigure(0, weight=1)

    table_wrap = ttk.Frame(mid)
    table_wrap.grid(row=0, column=0, sticky="nsew")
    table_wrap.columnconfigure(0, weight=1)
    table_wrap.rowconfigure(0, weight=1)

    columns = ("path", "type", "status")
    self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", selectmode="extended")
    self.tree.heading("path", text="File")
    self.tree.heading("type", text="Type")
    self.tree.heading("status", text="Status")
    self.tree.column("path", width=400, anchor="w")
    self.tree.column("type", width=80, anchor="center")
    self.tree.column("status", width=100, anchor="w")
    self.tree.grid(row=0, column=0, sticky="nsew")

    yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=yscroll.set)
    yscroll.grid(row=0, column=1, sticky="ns")

    right = ttk.Frame(mid, padding=(10, 0, 0, 0))
    right.grid(row=0, column=1, sticky="ns")

    self.btn_add = ttk.Button(right, text="Add Files", command=self.add_files)
    self.btn_add.grid(row=0, column=0, sticky="ew")
    self.btn_remove = ttk.Button(right, text="Remove Selected", command=self.remove_selected)
    self.btn_remove.grid(row=1, column=0, sticky="ew", pady=(8, 0))
    self.btn_clear = ttk.Button(right, text="Clear List", command=self.clear_list)
    self.btn_clear.grid(row=2, column=0, sticky="ew", pady=(8, 0))
    self.btn_start = ttk.Button(right, text="Start Convert", command=self.start_convert)
    self.btn_start.grid(row=3, column=0, sticky="ew", pady=(18, 0))

    bottom = ttk.Frame(self, padding=10)
    bottom.grid(row=2, column=0, sticky="ew")
    bottom.columnconfigure(0, weight=1)

    self.progress = ttk.Progressbar(bottom, mode="determinate")
    self.progress.grid(row=0, column=0, sticky="ew")
    ttk.Label(bottom, textvariable=self.status).grid(row=1, column=0, sticky="w", pady=(6, 0))

  def choose_output(self):
    path = filedialog.askdirectory()
    if path:
      self.output_dir.set(path)

  def open_output_dir(self):
    out_dir = Path(self.output_dir.get()).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
      if os.name == "nt":
        os.startfile(str(out_dir))
      else:
        subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(out_dir)], check=False)
    except Exception:
      messagebox.showwarning("Warning", "Cannot open output directory")

  def add_files(self):
    paths = filedialog.askopenfilenames(filetypes=[("E-book", "*.epub *.mobi"), ("All", "*.*")])
    for p in paths:
      if not p:
        continue
      if self._has_path(p):
        continue
      ext = Path(p).suffix.lower().lstrip(".")
      self.tree.insert("", tk.END, values=(p, ext or "-", "Pending"))

  def remove_selected(self):
    selected = list(self.tree.selection())
    for item in selected:
      self.tree.delete(item)

  def clear_list(self):
    for item in self.tree.get_children(""):
      self.tree.delete(item)
    self.status.set("Ready")
    self.progress["value"] = 0
    self.progress["maximum"] = 0

  def start_convert(self):
    if self.is_working:
      return
    items = list(self.tree.get_children(""))
    if not items:
      messagebox.showwarning("Warning", "Please add files first")
      return

    out_dir = Path(self.output_dir.get()).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    self.is_working = True
    self._set_buttons_state(disabled=True)
    self._job_total = len(items)
    self._job_done = 0
    self.progress["maximum"] = self._job_total
    self.progress["value"] = 0
    self.status.set(f"Preparing: 0/{self._job_total}")

    t = threading.Thread(target=self._convert_worker, args=(items, out_dir), daemon=True)
    t.start()

  def _convert_worker(self, items, out_dir: Path):
    ok = 0
    fail = 0
    last_error = ""
    for item in items:
      p = self.tree.item(item, "values")[0]
      try:
        self._set_item_status(item, "Converting")
        convert_to_cbz(Path(p), output_dir=out_dir)
        ok += 1
        self._set_item_status(item, "Success")
      except ConvertError as e:
        fail += 1
        last_error = str(e)
        self._set_item_status(item, "Failed")
      except Exception as e:
        fail += 1
        last_error = str(e)
        self._set_item_status(item, "Failed")

      self._job_done += 1
      self._set_progress(self._job_done, self._job_total, ok, fail)

    def done():
      self.is_working = False
      self._set_buttons_state(disabled=False)
      if fail == 0:
        self.status.set(f"Done: {ok} files")
        messagebox.showinfo("Done", f"Converted {ok} files")
      else:
        self.status.set(f"Done: Success {ok}, Failed {fail}")
        messagebox.showwarning("Done", f"Success {ok}, Failed {fail}\n{last_error}")

    self.after(0, done)

  def _set_status(self, text: str):
    self.after(0, lambda: self.status.set(text))

  def _set_buttons_state(self, disabled: bool):
    state = "disabled" if disabled else "normal"
    self.after(0, lambda: self.btn_add.configure(state=state))
    self.after(0, lambda: self.btn_remove.configure(state=state))
    self.after(0, lambda: self.btn_clear.configure(state=state))
    self.after(0, lambda: self.btn_start.configure(state=state))

  def _set_item_status(self, item, status: str):
    def apply():
      vals = list(self.tree.item(item, "values"))
      if len(vals) >= 3:
        vals[2] = status
        self.tree.item(item, values=tuple(vals))
    self.after(0, apply)

  def _set_progress(self, done: int, total: int, ok: int, fail: int):
    def apply():
      self.progress["value"] = done
      self.status.set(f"Progress: {done}/{total} (OK {ok}, Fail {fail})")
    self.after(0, apply)

  def _has_path(self, path: str) -> bool:
    for item in self.tree.get_children(""):
      vals = self.tree.item(item, "values")
      if vals and vals[0] == path:
        return True
    return False
