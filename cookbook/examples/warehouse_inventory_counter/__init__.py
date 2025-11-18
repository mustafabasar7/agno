"""
Warehouse Inventory Counter
Automatic product detection and counting for e-commerce warehouses and retail

Components:
- WarehouseDetector: YOLOv8-based object detection
- OCRReader: Product label text recognition
- Streamlit App: Web interface for easy use
"""

from .detector import WarehouseDetector
from .ocr_reader import OCRReader

__version__ = "1.0.0"
__all__ = ["WarehouseDetector", "OCRReader"]
