from enum import Enum

class BookStatus(str, Enum):
    AVAILABLE = 'available'
    ISSUED = 'issued'