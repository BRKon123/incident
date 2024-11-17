from pathlib import Path
from typing import Type, TypeVar, Dict, Any
from pydantic import BaseModel
from file_parser import FileParser, JsonParser

T = TypeVar('T', bound=BaseModel)

class ParserFactory:
    """Factory class to create appropriate parser based on file extension."""
    
    _parsers = {
        '.json': JsonParser,
    }
    
    # Define which arguments are valid for which parser types
    _parser_args = {
        JsonParser: set(),  # No special arguments
    }
    
    @classmethod
    def register_parser(cls, extension: str, parser_class: Type[FileParser], valid_args: set[str] = None):
        """Register a new parser for a file extension."""
        cls._parsers[extension.lower()] = parser_class
        if valid_args is not None:
            cls._parser_args[parser_class] = valid_args
    
    @classmethod
    def create_parser(cls, filepath: str, model: Type[T], **parser_kwargs) -> FileParser[T]:
        """Create appropriate parser for the given file using some logic"""
        extension = Path(filepath).suffix.lower()
        parser_class = cls._parsers.get(extension)
        
        if not parser_class:
            supported = ", ".join(cls._parsers.keys())
            raise ValueError(
                f"Unsupported file extension '{extension}'. "
                f"Supported extensions are: {supported}"
            )
        
        # Filter kwargs to only include valid arguments for this parser type
        valid_args = cls._parser_args.get(parser_class, set())
        filtered_kwargs = {
            k: v for k, v in parser_kwargs.items() 
            if k in valid_args
        }
        
        return parser_class(filepath, model, **filtered_kwargs) 