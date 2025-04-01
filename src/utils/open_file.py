import os
import subprocess
import time
import psutil

def is_outlook_running():
    """Kiểm tra Outlook có đang mở file EML không."""
    for p in psutil.process_iter(attrs=['name']):
        if p.info['name'] and "OUTLOOK.EXE" in p.info['name'].upper():
            return True
    return False

def open_eml_files_sequentially(eml_files, directory):
    """
    Mở từng file .eml bằng Outlook và chờ người dùng đóng trước khi mở file tiếp theo.

    Args:
        eml_files (list): Danh sách tên file .eml.
        directory (str): Đường dẫn chứa các file .eml.
    """
    for eml_file in eml_files:
        eml_path = os.path.join(directory, eml_file)
        if not os.path.exists(eml_path):
            print(f"❌ Không tìm thấy: {eml_file}")
            continue

        print(f"🟢 Đang mở: {eml_file}")

        process = subprocess.Popen(["start", "", eml_path], shell=True)
        print(process.pid)
        process.wait()
        print("Mã thoát:", process.returncode)
        # Chờ cho đến khi Outlook đóng file
        while is_outlook_running():
            time.sleep(1)  # Kiểm tra mỗi giây
        
        print(f"✅ Đã đóng: {eml_file}, mở file tiếp theo...")