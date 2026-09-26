import os
"""Provide the Tkinter interface for scanning and updating photo dates."""

import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from filename_dates import parse_filename_datetime
    from photo_metadata import set_photo_datetime
except ImportError:
    raise SystemExit(
        "Missing libraries. Run:\n"
        "pip install Pillow piexif"
    )

class App:
    def __init__(self, root):
        self.root = root
        root.title("Fix Photo Date from Filename")
        root.geometry("900x600")
        root.minsize(760, 500)

        self.folder = tk.StringVar()
        self.backup = tk.BooleanVar(value=True)
        self.dry_run = tk.BooleanVar(value=False)

        top = ttk.Frame(root, padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Thư mục ảnh:").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.folder).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top, text="Chọn...", command=self.choose_folder).grid(row=0, column=2)
        top.columnconfigure(1, weight=1)

        opts = ttk.Frame(root, padding=(12, 0, 12, 8))
        opts.pack(fill="x")
        ttk.Checkbutton(opts, text="Tạo backup (.bak) trước khi sửa", variable=self.backup).pack(side="left")
        ttk.Checkbutton(opts, text="Dry run (chỉ xem, không sửa)", variable=self.dry_run).pack(side="left", padx=20)

        btns = ttk.Frame(root, padding=(12, 0, 12, 8))
        btns.pack(fill="x")
        ttk.Button(btns, text="Quét ảnh", command=self.scan).pack(side="left")
        ttk.Button(btns, text="Sửa tất cả", command=self.fix_all).pack(side="left", padx=8)
        ttk.Button(btns, text="Mở thư mục", command=self.open_folder).pack(side="left")

        self.tree = ttk.Treeview(root, columns=("file", "old", "new", "status"), show="headings")
        self.tree.heading("file", text="Tên file")
        self.tree.heading("old", text="Ngày hiện tại (tên/EXIF)")
        self.tree.heading("new", text="Ngày sẽ đặt")
        self.tree.heading("status", text="Trạng thái")
        self.tree.column("file", width=360)
        self.tree.column("old", width=180)
        self.tree.column("new", width=180)
        self.tree.column("status", width=130)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.log = tk.Text(root, height=7)
        self.log.pack(fill="x", padx=12, pady=(0, 12))

        self.items = []

    def write_log(self, text):
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(folder)
            self.scan()

    def open_folder(self):
        folder = self.folder.get()
        if folder and os.path.isdir(folder):
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')

    def clear_tree(self):
        for x in self.tree.get_children():
            self.tree.delete(x)

    def scan(self):
        folder = self.folder.get()
        if not os.path.isdir(folder):
            messagebox.showwarning("Thiếu thư mục", "Hãy chọn thư mục ảnh trước.")
            return

        self.clear_tree()
        self.items = []

        files = sorted(os.listdir(folder), key=str.lower)
        for name in files:
            if not name.lower().endswith((".jpg", ".jpeg")):
                continue

            dt = parse_filename_datetime(name)
            path = os.path.join(folder, name)

            if dt:
                status = "Sẵn sàng"
                new_text = dt.strftime("%d/%m/%Y %H:%M:%S")
                self.items.append((path, dt))
            else:
                status = "Không nhận dạng"
                new_text = "-"

            self.tree.insert("", "end", values=(
                name,
                "-",
                new_text,
                status
            ))

        self.write_log(f"Đã quét: {len(files)} file trong thư mục; {len(self.items)} ảnh có ngày/giờ trong tên.")

    def fix_all(self):
        if not self.items:
            self.scan()
        if not self.items:
            return

        if self.dry_run.get():
            messagebox.showinfo("Dry run", f"Có {len(self.items)} ảnh sẽ được sửa, nhưng Dry run đang bật nên chưa thay đổi file.")
            return

        ok = messagebox.askyesno(
            "Xác nhận",
            f"Sẽ sửa ngày chụp cho {len(self.items)} ảnh.\n\n"
            "Ví dụ IMG_UPLOAD_20230422_103446.jpg → 22/04/2023 10:34:46.\n\n"
            + ("Backup sẽ được tạo trước khi sửa." if self.backup.get() else "Không tạo backup.")
            + "\n\nTiếp tục?"
        )
        if not ok:
            return

        success = 0
        failed = 0

        for path, dt in self.items:
            name = os.path.basename(path)
            try:
                if self.backup.get():
                    backup = path + ".bak"
                    shutil.copy2(path, backup)

                set_photo_datetime(path, dt)
                success += 1
                self.write_log(f"OK  {name} -> {dt.strftime('%Y:%m:%d %H:%M:%S')}")
            except Exception as e:
                failed += 1
                self.write_log(f"ERR {name}: {e}")

        self.write_log(f"Hoàn tất: {success} OK, {failed} lỗi.")
        messagebox.showinfo("Hoàn tất", f"Đã sửa {success} ảnh.\nLỗi: {failed}")

        self.scan()


if __name__ == "__main__":
    import sys
    root = tk.Tk()
    App(root)
    root.mainloop()
