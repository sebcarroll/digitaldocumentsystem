import logging
from app.services.google_drive.core import DriveCore
from docx import Document
import PyPDF2
import mammoth
import pandas as pd
import os
import io
from googleapiclient.http import MediaIoBaseDownload
from bs4 import BeautifulSoup
from pptx import Presentation
from striprtf.striprtf import rtf_to_text

# Set up logging
logger = logging.getLogger(__name__)

class FileExtractor:
    """
    A class to extract text from various file formats including .docx, .doc, PDFs, 
    Google Docs, Google Sheets, Excel files, and files stored on Google Drive.
    """

    def __init__(self, drive_core: DriveCore):
        """
        Initialize FileExtractor with a DriveCore instance.
        """
        self.drive_core = drive_core

    def extract_text_from_docx(self, file_path):
        """
        Extract text from a .docx file using mammoth.
        """
        try:
            with open(file_path, "rb") as docx_file:
                result = mammoth.extract_raw_text(docx_file)
            return result.value
        except Exception as e:
            logger.error(f"Error extracting text from DOCX file {file_path}: {e}")
            raise

    def extract_text_from_doc(self, file_path):
        """
        Extract text from a .doc file using mammoth.
        """
        try:
            with open(file_path, "rb") as doc_file:
                result = mammoth.extract_raw_text(doc_file)
            return result.value
        except Exception as e:
            logger.error(f"Error extracting text from DOC file {file_path}: {e}")
            raise

    def extract_text_from_pdf(self, file_path):
        """
        Extract text from a PDF file.
        """
        try:
            logger.info(f"Starting text extraction from PDF: {file_path}")
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                full_text = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    full_text.append(text)
                    logger.debug(f"Extracted text from page {i+1}")
            result = '\n'.join(full_text)
            logger.info(f"Successfully extracted text from PDF: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Error extracting text from PDF file {file_path}: {e}", exc_info=True)
            raise

    def extract_text_from_excel(self, file_path):
        """
        Extract text from an Excel file.
        """
        try:
            df = pd.read_excel(file_path)
            return df.to_csv(index=False)
        except Exception as e:
            logger.error(f"Error extracting text from Excel file {file_path}: {e}")
            raise

    def extract_text_from_google_doc(self, file_id):
        """
        Extract text from a Google Doc file using the DriveCore service.
        """
        try:
            mime_type = 'text/plain'
            data = self.drive_core.drive_service.files().export(fileId=file_id, mimeType=mime_type).execute()
            return data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting text from Google Doc with ID {file_id}: {e}")
            raise

    def extract_text_from_google_sheet(self, file_id):
        """
        Extract text from a Google Sheet file using the DriveCore service.
        """
        try:
            mime_type = 'text/csv'
            data = self.drive_core.drive_service.files().export(fileId=file_id, mimeType=mime_type).execute()
            return data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting text from Google Sheet with ID {file_id}: {e}")
            raise

    def download_file_from_google_drive(self, file_id, file_name):
        """
        Download a file from Google Drive.
        """
        try:
            request = self.drive_core.drive_service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_name, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Download progress: {int(status.progress() * 100)}%")
            
            fh.close()
            logger.info(f"File {file_name} downloaded successfully")
            return file_name
        except Exception as e:
            logger.error(f"Error downloading file with ID {file_id}: {e}")
            raise

    def extract_text_from_drive_file(self, file_id, file_name):
        """
        Download and extract text from a Google Drive file.
        """
        try:
            # Download the file
            local_path = self.download_file_from_google_drive(file_id, file_name)
            
            # Determine the file extension to decide which extraction method to use
            _, file_extension = os.path.splitext(local_path)
            
            if file_extension == '.pdf':
                return self.extract_text_from_pdf(local_path)
            elif file_extension == '.docx':
                return self.extract_text_from_docx(local_path)
            elif file_extension == '.doc':
                return self.extract_text_from_doc(local_path)
            elif file_extension in ['.xls', '.xlsx']:
                return self.extract_text_from_excel(local_path)
            elif file_extension == '.txt':
                return self.extract_text_from_txt(local_path)
            elif file_extension == '.md':
                return self.extract_text_from_md(local_path)
            elif file_extension == '.rtf':
                return self.extract_text_from_rtf(local_path)
            elif file_extension == '.html':
                return self.extract_text_from_html(local_path)
            elif file_extension in ['.pptx', '.ppt']:
                return self.extract_text_from_pptx(local_path)
            elif file_extension == '.csv':
                return self.extract_text_from_csv(local_path)
            else:
                logger.error(f"Unsupported file extension: {file_extension}")
                raise ValueError("Unsupported file type")
        except Exception as e:
            logger.error(f"Error extracting text from Drive file with ID {file_id}: {e}")
            raise

    def extract_text_from_txt(self, file_path):
        """
        Extract text from a plain text (.txt) file.
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT file {file_path}: {e}")
            raise

    def extract_text_from_md(self, file_path):
        """
        Extract text from a markdown (.md) file using plain text conversion.
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from MD file {file_path}: {e}")
            raise

    def extract_text_from_rtf(self, file_path):
        """
        Extract text from an RTF (.rtf) file using striprtf.
        """
        try:
            with open(file_path, 'r') as rtf_file:
                rtf_content = rtf_file.read()
                return rtf_to_text(rtf_content)
        except Exception as e:
            logger.error(f"Error extracting text from RTF file {file_path}: {e}")
            raise

    def extract_text_from_html(self, file_path):
        """
        Extract text from an HTML (.html) file.
        """
        try:
            with open(file_path, 'r') as file:
                soup = BeautifulSoup(file, 'html.parser')
                return soup.get_text()
        except Exception as e:
            logger.error(f"Error extracting text from HTML file {file_path}: {e}")
            raise

    def extract_text_from_csv(self, file_path):
        """
        Extract text from a CSV (.csv) file.
        """
        try:
            df = pd.read_csv(file_path)
            return df.to_csv(index=False)
        except Exception as e:
            logger.error(f"Error extracting text from CSV file {file_path}: {e}")
            raise

    def extract_text_from_pptx(self, file_path):
        """
        Extract text from a PowerPoint (.pptx) file.
        """
        try:
            prs = Presentation(file_path)
            text_runs = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text_runs.append(shape.text)
            return "\n".join(text_runs)
        except Exception as e:
            logger.error(f"Error extracting text from PPTX file {file_path}: {e}")
            raise
    def extract_text_from_file(self, file_id, file_name):
        """
        Extract text from any supported file type.
        """
        try:
            local_path = self.download_file_from_google_drive(file_id, file_name)
            _, file_extension = os.path.splitext(local_path)
            
            extraction_methods = {
                '.pdf': self.extract_text_from_pdf,
                '.docx': self.extract_text_from_docx,
                '.doc': self.extract_text_from_doc,
                '.xls': self.extract_text_from_excel,
                '.xlsx': self.extract_text_from_excel,
                '.txt': self.extract_text_from_txt,
                '.md': self.extract_text_from_md,
                '.rtf': self.extract_text_from_rtf,
                '.html': self.extract_text_from_html,
                '.pptx': self.extract_text_from_pptx,
                '.ppt': self.extract_text_from_pptx,
                '.csv': self.extract_text_from_csv
            }
            
            if file_extension in extraction_methods:
                return extraction_methods[file_extension](local_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
        except Exception as e:
            logger.error(f"Error extracting text from file {file_name}: {e}")
            raise