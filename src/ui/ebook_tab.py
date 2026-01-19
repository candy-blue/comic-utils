import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import subprocess
import sys
from src.modules.ebook_to_cbz.converter import ConvertError, convert_ebook
from src.core.i18n import i18n
from tkinterdnd2 import DND_FILES

class EbookTab(ttk.Frame):
  def __init__(self, parent):
    super().__init__(parent)
    
    self.output_dir = tk.StringVar(value=str(Path.cwd()))
    self.format_var = tk.StringVar(value="cbz")
    self.status = tk.StringVar(value=i18n.get('ready'))
    self.is_working = False
    self._job_total = 0
    self._job_done = 0

    self.columnconfigure(0, weight=1)
    self.rowconfigure(1, weight=1)

    self._build_ui()
    
    # Bind i18n
    i18n.add_listener(self.update_texts)
    self.update_texts()

    # DnD
    self.drop_target_register(DND_FILES)
    self.dnd_bind('<<Drop>>', self.on_drop)

  def _build_ui(self):
    # Top Bar
    top = ttk.Labelframe(self, text=i18n.get('output_dir'), padding=10)
    top.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    self.top_frame = top # store reference
    top.columnconfigure(1, weight=1)

    self.entry_output = ttk.Entry(top, textvariable=self.output_dir)
    self.entry_output.grid(row=0, column=1, sticky="ew", padx=(0, 5))
    
    self.btn_select = ttk.Button(top, text=i18n.get('browse'), command=self.choose_output, bootstyle="secondary")
    self.btn_select.grid(row=0, column=2, sticky="e")
    
    self.btn_open = ttk.Button(top, text=i18n.get('open_output'), command=self.open_output_dir, bootstyle="info-outline")
    self.btn_open.grid(row=0, column=3, sticky="e", padx=(5, 0))

    # Middle Area
    mid = ttk.Frame(self, padding=(10, 0, 10, 0))
    mid.grid(row=1, column=0, sticky="nsew")
    mid.columnconfigure(0, weight=1)
    mid.rowconfigure(0, weight=1)

    table_wrap = ttk.Frame(mid)
    table_wrap.grid(row=0, column=0, sticky="nsew")
    table_wrap.columnconfigure(0, weight=1)
    table_wrap.rowconfigure(0, weight=1)

    columns = ("path", "type", "status")
    self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", selectmode="extended", bootstyle="primary")
    self.tree.heading("path", text=i18n.get('file_col'))
    self.tree.heading("type", text=i18n.get('type_col'))
    self.tree.heading("status", text=i18n.get('status_col'))
    self.tree.column("path", width=400, anchor="w")
    self.tree.column("type", width=80, anchor="center")
    self.tree.column("status", width=100, anchor="w")
    self.tree.grid(row=0, column=0, sticky="nsew")

    yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
    self.tree.configure(yscrollcommand=yscroll.set)
    yscroll.grid(row=0, column=1, sticky="ns")

    # Right Buttons
    right = ttk.Frame(mid, padding=(10, 0, 0, 0))
    right.grid(row=0, column=1, sticky="ns")

    self.btn_add = ttk.Button(right, text=i18n.get('add_files'), command=self.add_files, bootstyle="primary")
    self.btn_add.grid(row=0, column=0, sticky="ew")
    
    self.btn_remove = ttk.Button(right, text=i18n.get('remove_selected'), command=self.remove_selected, bootstyle="warning")
    self.btn_remove.grid(row=1, column=0, sticky="ew", pady=(8, 0))
    
    self.btn_clear = ttk.Button(right, text=i18n.get('clear_list'), command=self.clear_list, bootstyle="danger")
    self.btn_clear.grid(row=2, column=0, sticky="ew", pady=(8, 0))
    
    # Format Selection
    self.lbl_format = ttk.Label(right, text=i18n.get('format_label'))
    self.lbl_format.grid(row=3, column=0, sticky="w", pady=(15, 0))
    
    formats = [
            ("cbz", i18n.get('fmt_cbz')),
            ("pdf", i18n.get('fmt_pdf')),
            ("epub", i18n.get('fmt_epub')),
            ("mobi", i18n.get('fmt_mobi')),
            ("zip", i18n.get('fmt_zip')),
            ("rar", i18n.get('fmt_rar')),
            ("7z", i18n.get('fmt_7z')),
    ]
    self.format_combo = ttk.Combobox(right, textvariable=self.format_var, state="readonly", width=20, bootstyle="primary")
    self.format_combo['values'] = [f[0] for f in formats]
    self.format_combo.grid(row=4, column=0, sticky="ew", pady=(5, 0))

    # Hint
    self.lbl_hint = ttk.Label(right, text=i18n.get('drag_drop_hint'), wraplength=100, bootstyle="secondary", justify="center")
    self.lbl_hint.grid(row=5, column=0, sticky="ew", pady=(20, 0))

    self.btn_start = ttk.Button(right, text=i18n.get('start'), command=self.start_convert, bootstyle="success")
    self.btn_start.grid(row=6, column=0, sticky="ew", pady=(20, 0))

    # Bottom Area
    bottom = ttk.Frame(self, padding=10)
    bottom.grid(row=2, column=0, sticky="ew")
    bottom.columnconfigure(0, weight=1)

    self.progress = ttk.Progressbar(bottom, mode="determinate", bootstyle="success-striped")
    self.progress.grid(row=0, column=0, sticky="ew")
    ttk.Label(bottom, textvariable=self.status).grid(row=1, column=0, sticky="w", pady=(6, 0))

  def update_texts(self):
      self.top_frame.config(text=i18n.get('output_dir'))
      self.btn_select.config(text=i18n.get('browse'))
      self.btn_open.config(text=i18n.get('open_output'))
      
      self.tree.heading("path", text=i18n.get('file_col'))
      self.tree.heading("type", text=i18n.get('type_col'))
      self.tree.heading("status", text=i18n.get('status_col'))
      
      self.btn_add.config(text=i18n.get('add_files'))
      self.btn_remove.config(text=i18n.get('remove_selected'))
      self.btn_clear.config(text=i18n.get('clear_list'))
      self.btn_start.config(text=i18n.get('start'))
      self.lbl_hint.config(text=i18n.get('drag_drop_hint'))
      self.lbl_format.config(text=i18n.get('format_label'))
      
      if not self.is_working and self._job_total == 0:
          self.status.set(i18n.get('ready'))

  def on_drop(self, event):
      files = self.tk.splitlist(event.data)
      for p in files:
          if os.path.isfile(p):
              ext = Path(p).suffix.lower()
              if ext in ['.epub', '.mobi', '.zip', '.cbz', '.rar', '.cbr', '.pdf']:
                  self.add_file_to_list(p)

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
      messagebox.showwarning(i18n.get('error'), "Cannot open output directory")

  def add_files(self):
    paths = filedialog.askopenfilenames(filetypes=[("Archives", "*.epub *.mobi *.zip *.cbz *.rar *.cbr *.pdf *.7z *.cb7"), ("All", "*.*")])
    for p in paths:
      if not p: continue
      self.add_file_to_list(p)
      
  def add_file_to_list(self, p):
      if self._has_path(p):
        return
      ext = Path(p).suffix.lower().lstrip(".")
      self.tree.insert("", tk.END, values=(p, ext or "-", i18n.get('status_pending')))

  def remove_selected(self):
    selected = list(self.tree.selection())
    for item in selected:
      self.tree.delete(item)

  def clear_list(self):
    for item in self.tree.get_children(""):
      self.tree.delete(item)
    self.status.set(i18n.get('ready'))
    self.progress["value"] = 0
    self.progress["maximum"] = 0

  def start_convert(self):
    if self.is_working:
      return
    items = list(self.tree.get_children(""))
    if not items:
      messagebox.showwarning(i18n.get('error'), i18n.get('msg_no_files'))
      return

    out_dir = Path(self.output_dir.get()).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    fmt = self.format_var.get()

    self.is_working = True
    self._set_buttons_state(disabled=True)
    self._job_total = len(items)
    self._job_done = 0
    self.progress["maximum"] = self._job_total
    self.progress["value"] = 0
    self._set_progress(0, self._job_total, 0, 0)

    t = threading.Thread(target=self._convert_worker, args=(items, out_dir, fmt), daemon=True)
    t.start()

  def _convert_worker(self, items, out_dir: Path, fmt: str):
    ok = 0
    fail = 0
    last_error = ""
    for item in items:
      p = self.tree.item(item, "values")[0]
      try:
        self._set_item_status(item, i18n.get('status_converting'))
        convert_ebook(Path(p), output_dir=out_dir, fmt=fmt)
        ok += 1
        self._set_item_status(item, i18n.get('status_success'))
      except ConvertError as e:
        fail += 1
        last_error = str(e)
        self._set_item_status(item, i18n.get('status_failed'))
      except Exception as e:
        fail += 1
        last_error = str(e)
        self._set_item_status(item, i18n.get('status_failed'))

      self._job_done += 1
      self._set_progress(self._job_done, self._job_total, ok, fail)

    def done():
      self.is_working = False
      self._set_buttons_state(disabled=False)
      if fail == 0:
        messagebox.showinfo(i18n.get('msg_done_title'), i18n.get('msg_done_count', ok))
      else:
        messagebox.showwarning(i18n.get('msg_done_title'), i18n.get('msg_done_fail', ok, fail, last_error))

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
      self.status.set(i18n.get('progress_fmt', done, total, ok, fail))
    self.after(0, apply)

  def _has_path(self, path: str) -> bool:
    for item in self.tree.get_children(""):
      vals = self.tree.item(item, "values")
      if vals and vals[0] == path:
        return True
    return False
