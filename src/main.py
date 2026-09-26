"""Provide the Tkinter interface for scanning and updating photo dates."""

import os
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from filename_dates import parse_filename_datetime
    from manual_datetime import parse_manual_datetime
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
        self.manual_folder_path = tk.StringVar()
        self.manual_datetime = tk.StringVar()
        self.backup = tk.BooleanVar(value=True)
        self.dry_run = tk.BooleanVar(value=False)

        options = ttk.Frame(root, padding=(12, 12, 12, 8))
        options.pack(fill="x")
        ttk.Checkbutton(options, text="Tạo backup (.bak) trước khi sửa", variable=self.backup).pack(side="left")
        ttk.Checkbutton(options, text="Dry run (chỉ xem, không sửa)", variable=self.dry_run).pack(side="left", padx=20)

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=12)

        bulk_tab = ttk.Frame(notebook, padding=12)
        notebook.add(bulk_tab, text="Sửa hàng loạt")

        folder_row = ttk.Frame(bulk_tab)
        folder_row.pack(fill="x", pady=(0, 8))
        ttk.Label(folder_row, text="Thư mục ảnh:").grid(row=0, column=0, sticky="w")
        ttk.Entry(folder_row, textvariable=self.folder).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(folder_row, text="Chọn...", command=self.choose_folder).grid(row=0, column=2)
        folder_row.columnconfigure(1, weight=1)

        bulk_buttons = ttk.Frame(bulk_tab)
        bulk_buttons.pack(fill="x", pady=(0, 8))
        ttk.Button(bulk_buttons, text="Quét ảnh", command=self.scan).pack(side="left")
        ttk.Button(bulk_buttons, text="Sửa tất cả", command=self.fix_all).pack(side="left", padx=8)
        ttk.Button(bulk_buttons, text="Mở thư mục", command=self.open_folder).pack(side="left")

        self.tree = ttk.Treeview(bulk_tab, columns=("file", "old", "new", "status"), show="headings")
        self.tree.heading("file", text="Tên file")
        self.tree.heading("old", text="Ngày hiện tại (tên/EXIF)")
        self.tree.heading("new", text="Ngày sẽ đặt")
        self.tree.heading("status", text="Trạng thái")
        self.tree.column("file", width=360)
        self.tree.column("old", width=180)
        self.tree.column("new", width=180)
        self.tree.column("status", width=130)
        self.tree.pack(fill="both", expand=True)

        manual_tab = ttk.Frame(notebook, padding=16)
        notebook.add(manual_tab, text="Sửa thủ công")

        ttk.Label(manual_tab, text="Chọn thư mục JPEG và nhập ngày giờ muốn đặt cho tất cả ảnh trong thư mục.").pack(
            anchor="w", pady=(0, 12)
        )

        manual_folder_row = ttk.Frame(manual_tab)
        manual_folder_row.pack(fill="x", pady=(0, 12))
        ttk.Label(manual_folder_row, text="Thư mục ảnh:", width=18).grid(row=0, column=0, sticky="w")
        ttk.Entry(manual_folder_row, textvariable=self.manual_folder_path).grid(
            row=0, column=1, sticky="ew", padx=8
        )
        ttk.Button(manual_folder_row, text="Chọn thư mục...", command=self.choose_manual_folder).grid(
            row=0, column=2
        )
        manual_folder_row.columnconfigure(1, weight=1)

        datetime_row = ttk.Frame(manual_tab)
        datetime_row.pack(fill="x", pady=(0, 12))
        ttk.Label(datetime_row, text="Ngày giờ:", width=18).grid(row=0, column=0, sticky="w")
        ttk.Entry(datetime_row, textvariable=self.manual_datetime, width=24).grid(
            row=0, column=1, sticky="w", padx=8
        )
        ttk.Label(datetime_row, text="Định dạng: YYYY-MM-DD HH:MM:SS").grid(
            row=0, column=2, sticky="w"
        )

        ttk.Button(manual_tab, text="Sửa tất cả ảnh trong thư mục", command=self.fix_manual_folder).pack(
            anchor="w"
        )

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

    def choose_manual_folder(self):
        folder_path = filedialog.askdirectory(title="Chọn thư mục ảnh")
        if folder_path:
            self.manual_folder_path.set(folder_path)

    def fix_manual_folder(self):
        folder_path = self.manual_folder_path.get().strip()
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showwarning("Thiếu thư mục", "Hãy chọn một thư mục hợp lệ.")
            return

        image_paths = [
            os.path.join(folder_path, name)
            for name in sorted(os.listdir(folder_path), key=str.lower)
            if name.lower().endswith((".jpg", ".jpeg"))
            and os.path.isfile(os.path.join(folder_path, name))
        ]
        if not image_paths:
            messagebox.showinfo("Không có ảnh", "Thư mục không có ảnh JPG/JPEG.")
            return

        try:
            photo_datetime = parse_manual_datetime(self.manual_datetime.get())
        except ValueError:
            messagebox.showwarning(
                "Ngày giờ không hợp lệ",
                "Nhập ngày giờ theo định dạng YYYY-MM-DD HH:MM:SS.",
            )
            return

        display_datetime = photo_datetime.strftime("%Y-%m-%d %H:%M:%S")
        if self.dry_run.get():
            self.write_log(
                f"DRY RUN {len(image_paths)} ảnh trong {folder_path} -> {display_datetime}"
            )
            messagebox.showinfo(
                "Dry run",
                f"{len(image_paths)} ảnh sẽ được đặt ngày giờ {display_datetime}.\n"
                "Chưa có file nào thay đổi.",
            )
            return

        backup_message = "Backup sẽ được tạo trước khi sửa." if self.backup.get() else "Không tạo backup."
        if not messagebox.askyesno(
            "Xác nhận sửa ảnh trong thư mục",
            f"Sẽ đặt ngày giờ {display_datetime} cho {len(image_paths)} ảnh trong thư mục:\n"
            f"{folder_path}\n\n"
            f"{backup_message}\n\nTiếp tục?",
        ):
            return

        success = 0
        failed = 0
        for image_path in image_paths:
            try:
                if self.backup.get():
                    shutil.copy2(image_path, image_path + ".bak")
                set_photo_datetime(image_path, photo_datetime)
                success += 1
                self.write_log(f"OK  {os.path.basename(image_path)} -> {display_datetime}")
            except Exception as error:
                failed += 1
                self.write_log(f"ERR {os.path.basename(image_path)}: {error}")

        self.write_log(f"Sửa thủ công hoàn tất: {success} OK, {failed} lỗi.")
        messagebox.showinfo("Hoàn tất", f"Đã sửa {success} ảnh.\nLỗi: {failed}")

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
    root = tk.Tk()
    App(root)
    root.mainloop()
