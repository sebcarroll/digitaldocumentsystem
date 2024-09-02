"""
Unit tests for the FileExtractor class.

This module contains a set of pytest-based unit tests for the FileExtractor class,
which is responsible for extracting text from various file formats stored on Google Drive.
These tests cover different functionalities including file conversion, document loading,
and text extraction from different file types.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from app.services.natural_language.file_extractor import FileExtractor, DriveCore
from langchain.schema import Document


@pytest.fixture
def mock_drive_core():
    """
    Fixture to create a mock DriveCore object.

    Returns:
        Mock: A mock object representing DriveCore with a drive_service attribute.
    """
    mock_core = Mock(spec=DriveCore)
    mock_core.drive_service = Mock()
    return mock_core


@pytest.fixture
def file_extractor(mock_drive_core):
    """
    Fixture to create a FileExtractor instance with a mock DriveCore.

    Args:
        mock_drive_core (Mock): A mock DriveCore object.

    Returns:
        FileExtractor: An instance of FileExtractor for testing.
    """
    return FileExtractor(drive_core=mock_drive_core)


def test_convert_google_doc_to_docx(file_extractor):
    """
    Test the convert_google_doc_to_docx method of FileExtractor.

    This test verifies that a Google Doc is correctly converted to .docx format.

    Args:
        file_extractor (FileExtractor): The FileExtractor instance to test.
    """
    mock_request = MagicMock()
    mock_request.execute.return_value = b"mock docx content"
    file_extractor.drive_core.drive_service.files().export_media.return_value = mock_request

    result = file_extractor.convert_google_doc_to_docx("file_id")

    assert isinstance(result, BytesIO)
    assert result.getvalue() == b"mock docx content"
    file_extractor.drive_core.drive_service.files().export_media.assert_called_once_with(
        fileId="file_id",
        mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


def test_convert_google_sheet_to_xlsx(file_extractor):
    """
    Test the convert_google_sheet_to_xlsx method of FileExtractor.

    This test verifies that a Google Sheet is correctly converted to .xlsx format.

    Args:
        file_extractor (FileExtractor): The FileExtractor instance to test.
    """
    mock_request = MagicMock()
    mock_request.execute.return_value = b"mock xlsx content"
    file_extractor.drive_core.drive_service.files().export_media.return_value = mock_request

    result = file_extractor.convert_google_sheet_to_xlsx("file_id")

    assert isinstance(result, BytesIO)
    assert result.getvalue() == b"mock xlsx content"
    file_extractor.drive_core.drive_service.files().export_media.assert_called_once_with(
        fileId="file_id",
        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@pytest.mark.parametrize("file_type, expected_loader", [
    ('docx', 'Docx2txtLoader'),
    ('csv', 'CSVLoader'),
    ('txt', 'TextLoader'),
    ('pdf', 'PyPDFLoader'),
    ('xlsx', 'UnstructuredExcelLoader'),
])
def test_load_document_file_path(file_extractor, file_type, expected_loader):
    """
    Test the load_document method of FileExtractor with file paths.

    This test verifies that the correct loader is used for different file types.

    Args:
        file_extractor (FileExtractor): The FileExtractor instance to test.
        file_type (str): The type of file to test.
        expected_loader (str): The name of the expected loader class.
    """
    with patch(f'app.services.natural_language.file_extractor.{expected_loader}') as mock_loader:
        mock_loader.return_value.load.return_value = [Document(page_content="mock content")]
        
        result = file_extractor.load_document(f"mock_file.{file_type}", file_type)
        
        assert len(result) == 1
        assert result[0].page_content == "mock content"
        mock_loader.assert_called_once_with(f"mock_file.{file_type}")


@pytest.mark.parametrize("file_type, content", [
    ('docx', b"mock docx content"),
    ('csv', b"col1,col2\nval1,val2"),
    ('txt', b"mock text content"),
    ('pdf', b"%PDF-mock content"),
    ('xlsx', b"mock xlsx content"),
])
def test_load_document_bytesio(file_extractor, file_type, content):
    """
    Test the load_document method of FileExtractor with BytesIO objects.

    This test verifies that documents can be loaded correctly from BytesIO objects.

    Args:
        file_extractor (FileExtractor): The FileExtractor instance to test.
        file_type (str): The type of file to test.
        content (bytes): The mock content of the file.
    """
    mock_file = BytesIO(content)
    
    with patch('app.services.natural_language.file_extractor.docx2txt.process', return_value="mock docx text"), \
         patch('app.services.natural_language.file_extractor.chardet.detect', return_value={'encoding': 'utf-8'}), \
         patch('app.services.natural_language.file_extractor.PdfReader') as mock_pdf_reader, \
         patch('app.services.natural_language.file_extractor.openpyxl.load_workbook') as mock_load_workbook:
        
        if file_type == 'pdf':
            mock_pdf_reader.return_value.pages = [MagicMock(extract_text=lambda: "mock pdf text")]
        elif file_type in ['xlsx', 'xls']:
            mock_workbook = MagicMock()
            mock_workbook.sheetnames = ["Sheet1"]
            mock_sheet = MagicMock()
            mock_sheet.iter_rows.return_value = [[MagicMock(value="cell1"), MagicMock(value="cell2")]]
            mock_workbook.__getitem__.return_value = mock_sheet
            mock_load_workbook.return_value = mock_workbook
        
        result = file_extractor.load_document(mock_file, file_type)
        
        assert len(result) == 1
        assert isinstance(result[0], Document)
        assert result[0].page_content != ""


def test_download_file_from_google_drive(file_extractor):
    """
    Test the download_file_from_google_drive method of FileExtractor.

    This test verifies that a file can be downloaded correctly from Google Drive.

    Args:
        file_extractor (FileExtractor): The FileExtractor instance to test.
    """
    mock_request = MagicMock()
    file_extractor.drive_core.drive_service.files().get_media.return_value = mock_request
    
    with patch('app.services.natural_language.file_extractor.io.FileIO'), \
         patch('app.services.natural_language.file_extractor.MediaIoBaseDownload') as mock_downloader:
        mock_downloader.return_value.next_chunk.side_effect = [(None, False), (None, True)]
        
        result = file_extractor.download_file_from_google_drive("file_id", "file_name")
        
        assert result == "file_name"
        file_extractor.drive_core.drive_service.files().get_media.assert_called_once_with(fileId="file_id")


def test_extract_text_from_drive_file(file_extractor):
    """
    Test the extract_text_from_drive_file method of FileExtractor.

    This test verifies that text can be extracted correctly from a Google Drive file.

    Args:
        file_extractor (FileExtractor): The FileExtractor instance to test.
    """
    file_extractor.drive_core.drive_service.files().get().execute.return_value = {
        'mimeType': 'application/vnd.google-apps.document'
    }
    
    with patch.object(file_extractor, 'convert_google_doc_to_docx', return_value=BytesIO(b"mock docx content")), \
         patch.object(file_extractor, 'load_document', return_value=[Document(page_content="mock extracted text")]):
        
        result = file_extractor.extract_text_from_drive_file("file_id", "file_name")
        
        assert result == "mock extracted text"
        file_extractor.drive_core.drive_service.files().get.assert_called_once_with(fileId="file_id", fields='mimeType')


def test_extract_text_from_drive_file_unsupported_mime_type(file_extractor):
    """
    Test the extract_text_from_drive_file method with an unsupported MIME type.

    This test verifies that a ValueError is raised for unsupported file types.

    Args:
        file_extractor (FileExtractor): The FileExtractor instance to test.
    """
    file_extractor.drive_core.drive_service.files().get().execute.return_value = {
        'mimeType': 'unsupported/mime-type'
    }
    
    with pytest.raises(ValueError, match="Unsupported MIME type: unsupported/mime-type"):
        file_extractor.extract_text_from_drive_file("file_id", "file_name")