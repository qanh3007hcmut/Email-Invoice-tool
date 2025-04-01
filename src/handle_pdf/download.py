
import re
import requests
import os
from urllib.parse import urlparse, parse_qs

def extract_api_from_html(html_content, base_url, token):
    """Tìm API từ nội dung HTML nếu file tải về không phải PDF."""
    url_match = re.search(r'var url = "(.+?)";', html_content)
    if url_match:
        api_endpoint = url_match.group(1)
        return(f"{base_url}{api_endpoint}?token={token}")
    return None

def download_pdf(email_data, save_path):
    """
    Tìm và tải file PDF từ đường link trong body email, sử dụng tên file gốc từ URL nếu có.

    Args:
        email_data (dict): Dictionary chứa "subject" và "body" của email.
        save_path (str): Đường dẫn thư mục lưu file PDF.

    Returns:
        str: Đường dẫn file PDF đã tải về, hoặc None nếu không tìm thấy link.
    """
    body = email_data.get("body", "")
    
    # Regex để tìm link trong thẻ <a> có nội dung "Để tải hóa đơn dạng PDF:"
    match = re.search(r"- Để tải hóa đơn dạng PDF:\s*<a href=[\"'](https?://[^\"']+)[\"']", body)
    if not match:
        match = re.search(r'<a\s+href=[\'"](?P<url>https?://[^\'"]+)[\'"]><b>link</b></a>\s* để tải nhanh hóa đơn dạng PDF.', body)
        if not match:
            return None

    pdf_url = match.group(1)  # Lấy đường link trong href

    # Tạo thư mục lưu trữ nếu chưa có
    os.makedirs(save_path, exist_ok=True)

    # Tải file PDF
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        # Lấy tên file từ URL
        parsed_url = urlparse(pdf_url)
        filename = os.path.basename(parsed_url.path)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        token = parse_qs(parsed_url.query).get("token", [""])[0]

        if "application/pdf" not in response.headers.get("Content-Type", "").lower():
            # print("Không nhận được file PDF, thử tìm API từ HTML...")
            api_url = extract_api_from_html(response.text, base_url, token)
            if api_url:
                # print(f"Gọi API: {api_url}")
                response = requests.get(api_url, stream=True)
                response.raise_for_status()
            else:
                print("Không tìm thấy API trong HTML.")
                return None

        # Nếu URL không có tên file, thử lấy từ header Content-Disposition
        if not filename or "." not in filename:
            content_disp = response.headers.get("Content-Disposition", "") 
            match = re.search(r'filename="?([^";]+)"?', content_disp)
            if match:
                filename = match.group(1)
            else:
                filename = "invoice.pdf"  # Tên mặc định

        # Xóa ký tự không hợp lệ trong tên file
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)

        pdf_filename = f"{save_path}/{filename}"

        with open(pdf_filename, "wb") as pdf_file:
            for chunk in response.iter_content(1024):
                pdf_file.write(chunk)
        
        # print(f"Đã tải file PDF: {pdf_filename}")
        return pdf_filename
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải PDF: {e}")
        return None

