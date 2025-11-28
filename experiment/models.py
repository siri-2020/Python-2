"""
Data models for the Bill Splitter application.
Contains core business logic entities.
"""
from abc import ABC, abstractmethod

class MenuItem(ABC):
    """Abstract base class for menu items."""
    
    def __init__(self, name: str, price: float):
        self._name = name
        self._price = price

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @abstractmethod
    def get_info(self) -> str:
        """Return formatted information about the menu item."""
        pass


class Dish(MenuItem):
    """Represents a dish that can be shared among multiple people."""
    
    def __init__(self, name: str, price: float):
        super().__init__(name, price)
        self._eaters = []

    @property
    def eaters(self) -> list:
        """List of people sharing this dish."""
        return self._eaters

    def add_eater(self, person_name: str) -> None:
        """Add a person to the list of eaters for this dish."""
        if person_name not in self._eaters:
            self._eaters.append(person_name)

    def get_shared_price(self) -> float:
        """Calculate the price per person for this dish."""
        if len(self._eaters) == 0:
            return 0.0
        return self._price / len(self._eaters)

    def get_info(self) -> str:
        """Return formatted dish information."""
        return f"{self.name}: THB {self.price:.2f}"


class Person:
    """Represents a person participating in the bill split."""
    
    def __init__(self, name: str):
        self._name = name.strip()
        self._total = 0.0

    @property
    def name(self) -> str:
        return self._name

    @property
    def total(self) -> float:
        return self._total

    def add_to_total(self, amount: float) -> None:
        """Add an amount to this person's total bill."""
        self._total += amount

    def reset_total(self) -> None:
        """Reset the person's total to zero."""
        self._total = 0.0