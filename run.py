from src.CONFIG import *
from src.utils.get_emails import *
from src.utils.get_body import *
from src.utils.invoice_classifier import *
from src.utils.clean_cache import *
from src.handle_pdf.download import *
from src.handle_pdf.folder_and_file import *
import argparse

from src.utils.open_file import *

import os
from dotenv import load_dotenv
load_dotenv()

def has_subfolders(path):
    return any(os.path.isdir(os.path.join(path, entry)) for entry in os.listdir(path))

def main():
    # Thiết lập argument parser
    parser = argparse.ArgumentParser(description="Lấy và phân loại email theo tháng")
    parser.add_argument("month", type=int, help="Tháng cần lấy email (1-12)")
    parser.add_argument("--clean", action="store_true", help="Xóa cache trước khi lấy email")
    args = parser.parse_args()


    # Kiểm tra tháng hợp lệ
    if not 1 <= args.month <= 12:
        print("Tháng phải từ 1 đến 12")
        return

    # Nếu có flag --clean thì xóa cache
    if args.clean:
        print("Xóa cache trước khi lấy email...")
        clear_directory(TEMP_MAIL)
        clear_directory(ATTACHMENTS)
        clear_directory(COMPANY_INVOICE)

    # Gọi hàm lấy email
    print(f"Lấy email tháng {args.month}...")
    
    fetch_emails_by_month(
        args.month,
        email_user=os.getenv("EMAIL_ADDRESS"),
        email_pass=os.getenv("APP_PASSWORD"),
        imap_server=IMAP_SERVER,
        save_path=TEMP_MAIL,
        attachment_path=ATTACHMENTS
    )

    # Phân loại email
    print("\nPhân loại email...")
    result, unrelated_list = classify_emails(COMPANY, TEMP_MAIL, ATTACHMENTS, COMPANY_INVOICE)

    # In kết quả
    print("\nKết quả phân loại:")
    for company, count in result.items():
        if count != 0:
            print(f"{company}: {count} email")
        
    os.makedirs(os.path.join(END_INVOICE, f"Tháng {args.month}"), exist_ok=True)
    os.makedirs(UNKNOWN_PATH, exist_ok=True)
    file_left = []
    for company in COMPANY:
        src_path = os.path.join(COMPANY_INVOICE, company)
        save_path = os.path.join(END_INVOICE, f"Tháng {args.month}", company)
        print("Xử lý công ty:", company, end="")
        process_folder(src_path, save_path, file_left, download_pdf, read_eml_file,process_eml=True)
    
    print("Xử lý UNKNOWN ", end="")
    file_left += process_unknown_files(UNKNOWN_PATH, args.month, COMPANY, END_INVOICE)
    
    print("Email không liên quan:", unrelated_list)
    print("Email không xử lý được:", file_left)
    
    # open_eml_files_sequentially(unrelated_list, TEMP_MAIL)
    open_eml_files_sequentially(file_left, TEMP_MAIL)
    
if __name__ == "__main__":
    main()