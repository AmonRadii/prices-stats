import statistics

class PriceModel:
    """Stores product data and handles mathematical calculations."""
    
    def __init__(self):
        """Initializes the data model with an empty item list."""
        self._items = []

    def add_item(self, name: str, price: float):
        """
        Adds a new product and its price to the model.

        Args:
            name (str): The name of the product.
            price (float): The price of the product.
        """
        self._items.append((name, price))

    def remove_item(self, index: int):
        """
        Removes an item from the model at the specified index.

        Validates the index bounds before removal to prevent IndexError.

        Args:
            index (int): The zero-based index of the item to be removed.
        """
        if 0 <= index < len(self._items):
            self._items.pop(index)

    def clear(self):
        """Clears all items from the model."""
        self._items.clear()

    def get_items(self) -> list:
        """
        Returns the current list of all items.

        Returns:
            list[tuple[str, float]]: A list of tuples in the format (product_name, price).
        """
        return self._items

    def get_statistics(self) -> dict:
        """Calculates basic statistical metrics for item prices.

        Returns:
            dict: A dictionary containing 'min', 'max', and 'median' keys.
                  If the item list is empty, all values are set to None.
        """
        if not self._items:
            return {"min": None, "max": None, "median": None}
        
        prices = [price for _, price in self._items]
        return {
            "min": min(prices),
            "max": max(prices),
            "median": statistics.median(prices)
        }