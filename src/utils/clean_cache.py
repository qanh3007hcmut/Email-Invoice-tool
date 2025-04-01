import os
import shutil

def clear_directory(directory_path):
    """
    Xóa toàn bộ file và thư mục con bên trong thư mục chỉ định.

    Args:
        directory_path (str): Đường dẫn đến thư mục cần xóa file.
    """
    try:
        if not os.path.exists(directory_path):
            print(f"Thư mục '{directory_path}' không tồn tại.")
            return

        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # Xóa file
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Xóa thư mục con và nội dung bên trong

        print(f"Đã xóa toàn bộ nội dung trong thư mục: {directory_path}")

    except Exception as e:
        print(f"Lỗi khi xóa file: {e}")
