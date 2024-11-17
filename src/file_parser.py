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
