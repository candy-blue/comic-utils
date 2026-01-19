import tkinter as tk
from tkinter import filedialog, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import os
from src.modules.comic_folder import converter
from src.core.i18n import i18n
from tkinterdnd2 import DND_FILES

class ComicFolderTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Variables
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.format_var = tk.StringVar(value="cbz")
        
        # Layout
        self.create_widgets()
        
        # Bind i18n
        i18n.add_listener(self.update_texts)
        self.update_texts()

        # DnD
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)
        
    def create_widgets(self):
        padding = {'padx': 10, 'pady': 5}
        
        # Input Directory
        input_frame = ttk.Labelframe(self, text=i18n.get('input_dir'), padding=10)
        input_frame.pack(fill='x', **padding)
        self.input_label_frame = input_frame

        self.entry_input = ttk.Entry(input_frame, textvariable=self.input_var)
        self.entry_input.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        self.btn_browse_input = ttk.Button(input_frame, text=i18n.get('browse'), command=self.select_input, bootstyle="secondary")
        self.btn_browse_input.pack(side='right')
        
        # Output Directory
        output_frame = ttk.Labelframe(self, text=i18n.get('output_dir'), padding=10)
        output_frame.pack(fill='x', **padding)
        self.output_label_frame = output_frame

        self.entry_output = ttk.Entry(output_frame, textvariable=self.output_var)
        self.entry_output.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        self.btn_browse_output = ttk.Button(output_frame, text=i18n.get('browse'), command=self.select_output, bootstyle="secondary")
        self.btn_browse_output.pack(side='right')
        
        # Format Selection
        fmt_frame = ttk.Frame(self)
        fmt_frame.pack(fill='x', **padding)
        
        self.lbl_format = ttk.Label(fmt_frame, text=i18n.get('format_label'))
        self.lbl_format.pack(side='left')
        
        formats = [
            ("cbz", i18n.get('fmt_cbz')),
            ("pdf", i18n.get('fmt_pdf')),
            ("epub", i18n.get('fmt_epub')),
            ("mobi", i18n.get('fmt_mobi')),
            ("zip", i18n.get('fmt_zip')),
            ("7z", i18n.get('fmt_7z')),
        ]
        
        # Improved Combobox style
        self.format_combo = ttk.Combobox(fmt_frame, textvariable=self.format_var, state="readonly", width=20, bootstyle="primary")
        self.format_combo['values'] = [f[0] for f in formats]
        self.format_combo.pack(side='left', padx=10)
        
        # Drag Drop Hint
        self.lbl_hint = ttk.Label(self, text=i18n.get('drag_drop_hint'), bootstyle="info", font=("Helvetica", 9, "italic"))
        self.lbl_hint.pack(pady=5)

        # Start Button
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', **padding)
        self.start_btn = ttk.Button(btn_frame, text=i18n.get('start'), command=self.start_processing, bootstyle="success")
        self.start_btn.pack(fill='x', ipady=5)
        
        # Progress
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill='x', **padding)
        self.status_label = ttk.Label(progress_frame, text=i18n.get('ready'))
        self.status_label.pack(anchor='w')
        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate', bootstyle="success-striped")
        self.progress_bar.pack(fill='x', pady=(5, 0))
        
        # Log Area
        log_frame = ttk.Labelframe(self, text=i18n.get('log'), padding=10)
        log_frame.pack(fill='both', expand=True, **padding)
        self.log_label_frame = log_frame

        self.log_area = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_area.pack(fill='both', expand=True)
    
    def update_texts(self):
        self.input_label_frame.config(text=i18n.get('input_dir'))
        self.btn_browse_input.config(text=i18n.get('browse'))
        self.output_label_frame.config(text=i18n.get('output_dir'))
        self.btn_browse_output.config(text=i18n.get('browse'))
        self.lbl_hint.config(text=i18n.get('drag_drop_hint'))
        self.start_btn.config(text=i18n.get('start'))
        self.status_label.config(text=i18n.get('ready'))
        self.log_label_frame.config(text=i18n.get('log'))
        self.lbl_format.config(text=i18n.get('format_label'))

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        if files:
            path = files[0]
            if os.path.isdir(path):
                self.input_var.set(path)
                if not self.output_var.get():
                    self.output_var.set(path)
            else:
                self.input_var.set(os.path.dirname(path))
                if not self.output_var.get():
                    self.output_var.set(os.path.dirname(path))

    def select_input(self):
        path = filedialog.askdirectory()
        if path:
            self.input_var.set(path)
            if not self.output_var.get():
                self.output_var.set(path)
            
    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_var.set(path)
            
    def start_processing(self):
        input_dir = self.input_var.get()
        output_dir = self.output_var.get()
        fmt = self.format_var.get()
        
        if not input_dir:
            self.log(i18n.get('select_input'))
            return
            
        if not os.path.exists(input_dir):
            self.log(i18n.get('input_not_exist', input_dir))
            return
            
        # Disable buttons
        self.start_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.log_area.delete(1.0, tk.END)
        self.log(f"{i18n.get('processing')}\nInput: {input_dir}\nOutput: {output_dir}\nFormat: {fmt}\n")
        
        # Run in thread
        threading.Thread(target=self.run_conversion, args=(input_dir, output_dir, fmt), daemon=True).start()
        
    def run_conversion(self, input_dir, output_dir, fmt):
        try:
            target_output = output_dir if output_dir.strip() else None
            
            converter.process_directory(
                input_dir, 
                target_output, 
                fmt=fmt,
                progress_callback=self.update_progress,
                log_callback=self.log
            )
            self.log(i18n.get('done'))
        except Exception as e:
            self.log(f"{i18n.get('error')}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.after(0, lambda: self.start_btn.config(state='normal'))

    def update_progress(self, current, total, desc):
        self.after(0, lambda: self._update_progress_gui(current, total, desc))
        
    def _update_progress_gui(self, current, total, desc):
        if total > 0:
            self.progress_bar['maximum'] = total
            self.progress_bar['value'] = current
        self.status_label.config(text=desc)

    def log(self, message):
        self.after(0, lambda: self._log_gui(message))
        
    def _log_gui(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
