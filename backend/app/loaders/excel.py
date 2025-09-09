"""
Pandas Excel reader.

Pandas parser for .xlsx files.

"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document


class PandasExcelReader(BaseReader):
    r"""Pandas-based CSV parser.

    Parses CSVs using the separator detection from Pandas `read_csv`function.
    If special parameters are required, use the `pandas_config` dict.

    Args:

        pandas_config (dict): Options for the `pandas.read_excel` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
            for more information. Set to empty dict by default, this means defaults will be used.

    """

    def __init__(
        self,
        *args: Any,
        pandas_config: Optional[dict] = None,
        concat_rows: bool = True,
        row_joiner: str = "\n",
        **kwargs: Any
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._pandas_config = pandas_config or {}
        self._concat_rows = concat_rows
        self._row_joiner = row_joiner if row_joiner else "\n"

    def load_data(
    self,
    file: Path,
    sheet_name: Optional[Union[str, int, list]] = None,
    extra_info: Optional[Dict] = None,
) -> List[Document]:
        """Parse Excel file and extract data.

        Args:
            file (Path): The path to the Excel file to read.
            sheet_name (Union[str, int, list, None]): The specific sheet to read from, default is None which reads all sheets.
            extra_info (Dict): Additional information to be added to the Document object.

        Returns:
            List[Document]: A list of Document objects containing the processed text from Excel sheets.
        """
        import pandas as pd

        dfs = pd.read_excel(file, sheet_name=sheet_name, **self._pandas_config)
        documents = []
        
        # Handle both single and multiple sheets
        if not isinstance(dfs, dict):
            dfs = {sheet_name if sheet_name else 0: dfs}
            
        for sheet_name, df in dfs.items():
            df = df.fillna('')
            
            rows = []
            for _, row in df.iterrows():
                row_text = ' '.join(str(cell).strip() for cell in row if str(cell).strip())
                if row_text:
                    rows.append(row_text)
            
            text = self._row_joiner.join(rows)
            
            if text.strip():
                doc_extra_info = {
                    'file_name': file.name,
                    'sheet_name': sheet_name
                }
                if extra_info:
                    doc_extra_info.update(extra_info)
                    
                doc = Document(
                    text=text,
                    extra_info=doc_extra_info
                )
                documents.append(doc)
        
        return documents