from src.CONFIG import *
from src.utils.get_emails import *
from src.utils.get_body import *
from src.utils.invoice_classifier import *
from src.utils.clean_cache import *
from src.handle_pdf.download import *
from src.handle_pdf.folder_and_file import *
from src.utils.open_file import *

unrelated_list = ['68.eml']

open_eml_files_sequentially(unrelated_list, TEMP_MAIL)
