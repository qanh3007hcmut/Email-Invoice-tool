import os
import shutil
import re
from .get_body import read_eml_file

def is_invoice_related(email_body):
    """
    Kiểm tra xem email có chứa pattern 'Hóa đơn (điện tử)?' trong subject hoặc body không.
    
    Args:
        email_body (dict): Dictionary chứa thông tin email với cấu trúc
                          {"subject": str, "body": str}
    
    Returns:
        bool: True nếu email là hóa đơn, False nếu không
    """
    # Lấy subject và body
    subject = email_body["subject"] if email_body["subject"] else ""
    body = email_body["body"] if email_body["body"] else ""

    # Pattern: "Hóa đơn" hoặc "Hóa đơn điện tử" (không phân biệt hoa thường)
    pattern = r"(?i)hóa đơn(\s+điện tử)?"

    # Kiểm tra pattern trong subject hoặc body
    is_invoice = bool(re.search(pattern, subject) or re.search(pattern, body))
    
    return is_invoice

def extract_company_name(email_body, company_list):
    """
    Trích xuất tên công ty từ subject hoặc body dựa trên danh sách tên công ty có sẵn.
    
    Args:
        email_body (dict): Dictionary chứa thông tin email với cấu trúc
                          {"subject": str, "body": str}
        company_list (list): Danh sách tên công ty cần kiểm tra
    
    Returns:
        str or int: Tên công ty trong danh sách (in hoa) hoặc 0 nếu không tìm thấy
    """
    # Lấy subject và body, xử lý None thành chuỗi rỗng
    subject = email_body["subject"] if email_body["subject"] else ""
    body = email_body["body"] if email_body["body"] else ""

    # Gộp subject và body để tìm kiếm
    full_text = subject + " " + body

    # Chuyển full_text về dạng không phân biệt hoa thường để so sánh
    full_text_lower = full_text.lower()

    # Duyệt qua danh sách công ty
    for company in company_list:
        # Tạo pattern để tìm tên công ty (không phân biệt hoa/thường)
        pattern = r"(?i)\b" + re.escape(company) + r"\b"
        if re.search(pattern, full_text):
            return company.upper()  # Trả về tên công ty khớp đầu tiên, in hoa
    
    return 0  # Không tìm thấy công ty nào trong danh sách

def classify_emails(company_list, mail_path, attachments_path, base_output_path):
    """
    Phân loại các file .eml dựa trên danh sách công ty và tạo thư mục tương ứng.
    
    Args:
        company_list (list): Danh sách tên công ty cần kiểm tra
        mail_path (str): Đường dẫn đến thư mục chứa các file .eml
        base_output_path (str): Đường dẫn cơ sở để tạo các thư mục công ty
    
    Returns:
        dict: Mapping giữa tên công ty và số lượng email đã phân loại
    """
    from rich.progress import Progress
    unrelated = []
    # Tạo thư mục đầu ra nếu chưa tồn tại
    os.makedirs(base_output_path, exist_ok=True)

    # Danh sách để theo dõi kết quả
    classification_result = {company.upper(): 0 for company in company_list}
    classification_result["UNKNOWN"] = 0
    with Progress() as progress:
        task = progress.add_task("[cyan]Đang xử lý...", total=len(os.listdir(mail_path)))
        # Duyệt qua tất cả file .eml trong mail_path
        for filename in os.listdir(mail_path):
            progress.update(task, advance=1) 
            if not filename.endswith(".eml"):
                unrelated.append(filename)
                continue

            file_path = os.path.join(mail_path, filename)
            
            # Đọc file .eml
            # with open(file_path, "rb") as f:
            #     msg = email.message_from_bytes(f.read())
                
            #     # Trích xuất subject và body
            #     subject = msg.get("Subject", "")
            #     if subject:
            #         subject = email.header.decode_header(subject)
            #         subject = "".join([s.decode(c or "utf-8") if isinstance(s, bytes) else s for s, c in subject])
                
            #     body = ""
            #     if msg.is_multipart():
            #         for part in msg.walk():
            #             if part.get_content_type() == "text/plain":
            #                 body = part.get_payload(decode=True)
            #                 if isinstance(body, bytes):
            #                     body = body.decode("utf-8", errors="ignore")
            #                 break
            #     else:
            #         body = msg.get_payload(decode=True)
            #         if isinstance(body, bytes):
            #             body = body.decode("utf-8", errors="ignore")
            # email_body = {"subject": subject, "body": body}
            
            email_body = read_eml_file(file_path)
            if not is_invoice_related(email_body): 
                unrelated.append(filename)
                continue
            # Trích xuất tên công ty
            company_name = extract_company_name(email_body, company_list)
            folder_name = company_name if company_name != 0 else "UNKNOWN"

            # Tạo thư mục công ty nếu chưa tồn tại
            company_folder = os.path.join(base_output_path, folder_name)
            os.makedirs(company_folder, exist_ok=True)

            # Di chuyển file vào thư mục tương ứng
            new_file_path = os.path.join(company_folder, filename)
            shutil.copy(file_path, new_file_path)
            # print(f"Đã di chuyển {filename} vào thư mục {folder_name}")

            # Xử lý attachments: lấy idx từ tên file (ví dụ: "1.eml" -> idx = "1")
            idx = filename.replace(".eml", "")
            attachment_folder = os.path.join(attachments_path, idx)
            
            if os.path.isdir(attachment_folder):
                company_attachment_folder = os.path.join(company_folder, idx)
                shutil.copytree(attachment_folder, company_attachment_folder, dirs_exist_ok=True)
                # print(f"Đã sao chép thư mục attachments {idx} vào {folder_name}/attachments")
            # Cập nhật kết quả
            classification_result[folder_name] += 1
            

    return classification_result, unrelated