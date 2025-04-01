import fitz  # PyMuPDF
import os
import shutil

def find_company_in_pdf(pdf_path, company_list):
    """
    Tìm tên công ty trong nội dung của file PDF.

    Args:
        pdf_path (str): Đường dẫn tới file PDF.
        company_list (list): Danh sách các tên công ty cần tìm.

    Returns:
        str: Tên công ty tìm thấy đầu tiên, hoặc None nếu không tìm thấy.
    """
    try:
        # Mở file PDF
        doc = fitz.open(pdf_path)
        text = ""
        
        # Đọc nội dung từng trang
        for page in doc:
            text += page.get_text("text") + "\n"
        
        # Kiểm tra xem công ty nào có trong nội dung
        for company in company_list:
            if company.lower() in text.lower():
                return company  # Trả về công ty đầu tiên tìm thấy
        
        return None  # Không tìm thấy công ty nào
    except Exception as e:
        print(f"Lỗi khi đọc PDF {pdf_path}: {e}")
        return None
    
def process_folder(src_path, save_path, error_file, download_pdf, read_eml_file, process_eml=False):
    """ Xử lý thư mục, copy file PDF hoặc tải file từ EML nếu cần. """
    from rich.progress import Progress

    if not os.path.exists(src_path): return
    os.makedirs(save_path, exist_ok=True)
    dirnames = [d for d in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, d))]
    with Progress() as progress:
        task = progress.add_task("[cyan]Đang xử lý...", total=len(os.listdir(src_path)))
        for root, _, files in os.walk(src_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                progress.update(task, advance=1)
                if filename.lower().endswith(".pdf"):
                    res = shutil.copy(file_path, save_path)
                    # print(f"Đã copy: {res}")
                elif process_eml and filename.lower().endswith(".eml"):
                    if download_pdf(read_eml_file(file_path), save_path) is None:
                        if filename.split(".")[0] in dirnames:
                            continue
                        error_file.append(filename)
                    
def process_unknown_files(unknown_path, month, company_list, invoice_path):
    """ Xử lý các file PDF chưa phân loại và di chuyển vào đúng thư mục công ty. """
    from rich.progress import Progress

    file_left = []
    dirnames = [d for d in os.listdir(unknown_path) if os.path.isdir(os.path.join(unknown_path, d))]
    with Progress() as progress:
        task = progress.add_task("[cyan]Đang xử lý...", total=len(os.listdir(unknown_path)))
        for root, _, files in os.walk(unknown_path):
            for filename in files:
                progress.update(task, advance=1)
                file_path = os.path.join(root, filename)
                if filename.lower().endswith(".pdf"):
                    company_name = find_company_in_pdf(file_path, company_list)
                    if company_name:
                        save_path = os.path.join(invoice_path, f"Tháng {month}", company_name)
                        os.makedirs(save_path, exist_ok=True)
                        res = shutil.copy(file_path, save_path)
                        # print(f"Đã copy: {res}")
                    else:
                        file_left.append(filename)
                elif filename.lower().endswith(".eml"):
                    if filename.split(".")[0] not in dirnames:
                        file_left.append(filename)
   
    return file_left