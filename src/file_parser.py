from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator, TypeVar, Generic, Type
from pathlib import Path
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)
class FileParser(ABC, Generic[T]):
    """Abstract base class for parsing input files into Pydantic models."""
    
    def __init__(self, filepath: str, model: Type[T]):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        self.model = model
        self._data: T | None = None
        self._parse()
    
    @abstractmethod
    def _read_file(self) -> Dict[str, Any]:
        """Read and parse the file into a dictionary."""
        pass

    def _parse(self) -> None:
        """Parse the file and validate against the Pydantic model."""
        try:
            raw_data = self._read_file()
            self._data = self.model.model_validate(raw_data)
        except ValidationError as e:
            raise ValueError(f"Data validation failed for {self.filepath}: {str(e)}")
    
    @property
    def data(self) -> T:
        """Access the parsed and validated data."""
        if self._data is None:
            raise RuntimeError("Data not yet parsed")
        return self._data

class JsonParser(FileParser[T]):
    """Implementation of FileParser for JSON files."""
    
    def _read_file(self) -> Dict[str, Any]:
        import json
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.filepath}: {str(e)}")
        except IOError as e:
            raise IOError(f"Error reading {self.filepath}: {str(e)}")

class CsvParser(FileParser[T]):
    """Implementation of FileParser for CSV files."""
    
    def __init__(self, filepath: str, model: Type[T], list_delimiter: str = '|'):
        """
        Args:
            filepath: Path to CSV file
            model: Pydantic model to validate against
            list_delimiter: Character used to separate items in list fields (default: '|')
        """
        self.list_delimiter = list_delimiter
        super().__init__(filepath, model)
    
    def _read_file(self) -> Dict[str, Any]:
        import csv
        try:
            with open(self.filepath, 'r') as f:
                reader = csv.DictReader(f)
                row = next(reader)  # Get first row
                
                # Special handling for schedule format
                if 'users' in row:
                    row['users'] = row['users'].split(self.list_delimiter)
                    # Convert string to int for handover_interval_days
                    row['handover_interval_days'] = int(row['handover_interval_days'])
                    return row
                
                # Handle overrides format
                overrides = []
                while row:
                    overrides.append(row)
                    try:
                        row = next(reader)
                    except StopIteration:
                        break
                return {"overrides": overrides}
                
        except csv.Error as e:
            raise ValueError(f"Invalid CSV in {self.filepath}: {str(e)}")
        except IOError as e:
            raise IOError(f"Error reading {self.filepath}: {str(e)}") 