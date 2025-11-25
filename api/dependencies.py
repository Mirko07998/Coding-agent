from typing import Dict, Optional
from fastapi import Query
import enum

class OrderByEnum(str, enum.Enum):
    name = 'name'
    price = 'price'
    
class SortEnum(str, enum.Enum):
    ASC = 'ASC'
    DESC = 'DESC'

def get_pagination_params(top: int = Query(default=10, ge=1, le=100), skip: int = Query(default=0, ge=0), order_by: Optional[OrderByEnum] = Query(default=None), sort: Optional[SortEnum] = Query(default=None), filter_by_name: str = Query(default=None)) -> Dict[str, Optional[object]]:
    return {
        "top": top,
        "skip": skip,
        "order_by": order_by,
        "sort": sort,
        "filter_by_name": filter_by_name
    }