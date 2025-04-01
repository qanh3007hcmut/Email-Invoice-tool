import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime
import re
from rich.progress import Progress


def fetch_emails_by_month(
    month, 
    email_user, 
    email_pass, 
    imap_server, 
    save_path, 
    attachment_path):
    """
    Lấy tất cả email trong một tháng cụ thể của năm hiện tại và lưu dưới dạng .eml cùng attachments.
    
    Args:
        month (int): Tháng cần lấy email (1-12)
        email_user (str): Địa chỉ email
        email_pass (str): Mật khẩu email hoặc app password
        imap_server (str): Server IMAP (mặc định cho Gmail)
        save_path (str): Đường dẫn lưu file .eml
        attachment_path (str): Đường dẫn lưu attachments
    """
    

    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(attachment_path, exist_ok=True)

    # Lấy năm hiện tại
    current_year = datetime.now().year

    # Kết nối đến server IMAP
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_user, email_pass)
    mail.select("inbox")  

    # Định dạng ngày tìm kiếm: "Since 01-Jan-2025 Before 01-Feb-2025"
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    start_date = f"01-{month_names[month-1]}-{current_year}"
    next_month = month % 12 + 1
    next_year = current_year + (1 if month == 12 else 0)
    end_date = f"01-{month_names[next_month-1]}-{next_year}"

    # Tìm kiếm email trong khoảng thời gian
    search_query = f'SINCE "{start_date}" BEFORE "{end_date}"'
    result, data = mail.search(None, search_query)
    
    email_ids = data[0].split()
    print(f"Tìm thấy {len(email_ids)} email trong tháng {month}/{current_year}")
    with Progress() as progress:
        task = progress.add_task("[cyan]Đang xử lý...", total=len(email_ids))
    
        # Duyệt qua từng email
        for idx, email_id in enumerate(email_ids, 1):
            
            # Lấy nội dung email
            result, msg_data = mail.fetch(email_id, "(RFC822)")
            if result != "OK":
                print(f"Lỗi khi tải email ID {email_id}")
                continue

            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Lưu file .eml
            eml_filename = f"{save_path}/{idx}.eml"
            with open(eml_filename, "wb") as f:
                f.write(raw_email)
            # print(f"Đã lưu email: {eml_filename}")

            # Xử lý attachments
            if email_message.get_content_maintype() == "multipart":
                for part in email_message.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    # Lấy tên file attachment
                    filename = part.get_filename()
                    if filename:
                        # Giải mã tên file nếu cần
                        decoded_name = decode_header(filename)
                        filename = decoded_name[0][0]
                        if isinstance(filename, bytes):
                            filename = filename.decode(decoded_name[0][1] or "utf-8")
                        
                        # Loại bỏ ký tự không hợp lệ trong tên file
                        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
                        attachment_path_idx = f"{attachment_path}/{idx}"
                        os.makedirs(attachment_path_idx, exist_ok=True)
                        attachment_filename = f"{attachment_path_idx}/{filename}"
                        # Lưu attachment
                        with open(attachment_filename, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        # print(f"Đã lưu attachment: {attachment_filename}")
            progress.update(task, advance=1)

        # Đóng kết nối
        mail.logout()
