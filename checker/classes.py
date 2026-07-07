#parsers for diff websites


def wb_price(data: dict) -> int:
    """parse price from wb"""

    
    price: int = (data['products'][0]['sizes'][0]['price']['product'] + data['products'][0]['sizes'][0]['price']['logistics']) / 100
    return price

    
    
