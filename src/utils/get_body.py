import email
from email import policy

def read_eml_file(eml_path):
    """
    Đọc nội dung của file .eml và trả về nội dung email (subject, from, to, body).
    
    Args:
        eml_path (str): Đường dẫn đến file .eml.
    
    Returns:
        dict: Dictionary chứa thông tin email gồm 'subject', 'from', 'to', và 'body'.
    """
    try:
        with open(eml_path, "rb") as f:
            raw_email = f.read()
        
        # Phân tích nội dung email
        email_message = email.message_from_bytes(raw_email, policy=policy.default)
        
        # Lấy tiêu đề
        subject = email_message["Subject"]
        
        # Giải mã subject nếu cần
        if subject:
            from email.header import decode_header
            subject, encoding = decode_header(subject)[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

        # Lấy nội dung email (chỉ lấy phần text)
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(part.get_content_charset(), errors="replace")
                    break  # Lấy phần text đầu tiên
        else:
            body = email_message.get_payload(decode=True).decode(email_message.get_content_charset(), errors="replace")
        
        return {
            "subject": subject,
            "body": body
        }
    
    except Exception as e:
        print(f"Lỗi khi đọc file .eml: {e}")
        return None
