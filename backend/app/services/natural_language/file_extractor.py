import logging
import os
import io
from typing import BinaryIO

from app.services.google_drive.core import DriveCore
from googleapiclient.http import MediaIoBaseDownload
from langchain.document_loaders import Docx2txtLoader, CSVLoader, TextLoader, UnstructuredPDFLoader
from langchain.schema import Document

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

        Args:
            drive_core (DriveCore): An instance of the DriveCore class for Google Drive operations.
        """
        self.drive_core = drive_core

    def convert_google_doc_to_docx(self, file_id: str) -> BinaryIO:
        """
        Convert a Google Doc to .docx format.

        Args:
            file_id (str): The ID of the Google Doc file.

        Returns:
            BinaryIO: A file-like object containing the .docx content.

        Raises:
            Exception: If there's an error during the conversion process.
        """
        try:
            request = self.drive_core.drive_service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            file = io.BytesIO(request.execute())
            return file
        except Exception as e:
            logger.error(f"Error converting Google Doc to DOCX: {e}")
            raise

    def convert_google_sheet_to_xlsx(self, file_id: str) -> BinaryIO:
        """
        Convert a Google Sheet to .xlsx format.

        Args:
            file_id (str): The ID of the Google Sheet file.

        Returns:
            BinaryIO: A file-like object containing the .xlsx content.

        Raises:
            Exception: If there's an error during the conversion process.
        """
        try:
            request = self.drive_core.drive_service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            file = io.BytesIO(request.execute())
            return file
        except Exception as e:
            logger.error(f"Error converting Google Sheet to XLSX: {e}")
            raise

    def load_document(self, file: BinaryIO, file_type: str) -> list[Document]:
        """
        Load a document using the appropriate Langchain loader.

        Args:
            file (BinaryIO): A file-like object containing the document content.
            file_type (str): The type of the file (e.g., 'docx', 'csv', 'txt', 'pdf').

        Returns:
            list[Document]: A list of Langchain Document objects.

        Raises:
            ValueError: If the file type is not supported.
            Exception: If there's an error during the loading process.
        """
        try:
            if file_type == 'docx':
                loader = Docx2txtLoader(file)
            elif file_type == 'csv':
                loader = CSVLoader(file)
            elif file_type == 'txt':
                loader = TextLoader(file)
            elif file_type == 'pdf':
                loader = UnstructuredPDFLoader(file)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            raise

    def download_file_from_google_drive(self, file_id: str, file_name: str) -> str:
        """
        Download a file from Google Drive.

        Args:
            file_id (str): The ID of the file in Google Drive.
            file_name (str): The name to save the file as locally.

        Returns:
            str: The path to the downloaded file.

        Raises:
            Exception: If there's an error during the download process.
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

    def extract_text_from_drive_file(self, file_id: str, file_name: str) -> str:
        """
        Download and extract text from a Google Drive file using Langchain loaders.

        Args:
            file_id (str): The ID of the file in Google Drive.
            file_name (str): The name of the file.

        Returns:
            str: The extracted text content from the file.

        Raises:
            Exception: If there's an error during the extraction process.
        """
        try:
            # Determine the file type
            _, file_extension = os.path.splitext(file_name)
            file_extension = file_extension.lower()[1:]  # Remove the dot

            if file_extension == 'gdoc':
                file = self.convert_google_doc_to_docx(file_id)
                file_extension = 'docx'
            elif file_extension == 'gsheet':
                file = self.convert_google_sheet_to_xlsx(file_id)
                file_extension = 'xlsx'
            else:
                file = self.download_file_from_google_drive(file_id, file_name)

            documents = self.load_document(file, file_extension)
            return "\n\n".join([doc.page_content for doc in documents])
        except Exception as e:
            logger.error(f"Error extracting text from Drive file with ID {file_id}: {e}")
            raise