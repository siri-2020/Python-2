"""
Bill calculation logic for the Bill Splitter application.
Handles splitting costs and generating results.
"""
from typing import Dict, List, Tuple
from models import Dish, Person

def dish_iterator(dishes: Dict[str, Dish]):
    """Iterator for dishes dictionary values."""
    for dish in dishes.values():
        yield dish

class BillCalculator:
    """Handles bill calculation and result generation."""
    
    @staticmethod
    def calculate_bills(dishes: Dict[str, Dish], people: Dict[str, Person]) -> None:
        """
        Calculate the total bill for each person based on shared dishes.
        
        Args:
            dishes: Dictionary of dish names to Dish objects
            people: Dictionary of person names to Person objects
        """
        # Reset all totals
        for person in people.values():
            person._total = 0.0
        
        # Calculate shared costs
        for dish in dish_iterator(dishes):
            shared_price = dish.get_shared_price()
            for eater_name in dish.eaters:
                if eater_name in people:
                    people[eater_name].add_to_total(shared_price)

    @staticmethod
    def get_total_bill(dishes: Dict[str, Dish]) -> float:
        """
        Calculate the total bill amount.
        
        Args:
            dishes: Dictionary of dish names to Dish objects
            
        Returns:
            Total bill amount
        """
        return sum(dish.price for dish in dishes.values())

    @staticmethod
    def get_bill_summary(
        dishes: Dict[str, Dish], 
        people: Dict[str, Person]
    ) -> Tuple[List[Tuple[str, float]], float]:
        """
        Generate a summary of the bill.
        
        Args:
            dishes: Dictionary of dish names to Dish objects
            people: Dictionary of person names to Person objects
            
        Returns:
            Tuple of (list of (person_name, amount) tuples, total_bill)
        """
        person_amounts = [(person.name, person.total) for person in people.values()]
        total_bill = BillCalculator.get_total_bill(dishes)
        
        return person_amounts, total_bill

    @staticmethod
    def validate_bill_split(
        dishes: Dict[str, Dish], 
        people: Dict[str, Person]
    ) -> Tuple[bool, str]:
        """
        Validate that the bill split is correct.
        
        Args:
            dishes: Dictionary of dish names to Dish objects
            people: Dictionary of person names to Person objects
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not dishes:
            return False, "No dishes have been added"
        
        if not people:
            return False, "No people have been added"
        
        # Check if all dishes have at least one eater
        unassigned_dishes = [
            dish.name for dish in dishes.values() 
            if len(dish.eaters) == 0
        ]
        
        if unassigned_dishes:
            return False, f"Unassigned dishes: {', '.join(unassigned_dishes)}"
        
        # Verify totals match
        total_bill = BillCalculator.get_total_bill(dishes)
        total_paid = sum(person.total for person in people.values())
        
        if abs(total_bill - total_paid) > 0.01:  # Allow for small floating point errors
            return False, f"Total mismatch: Bill={total_bill:.2f}, Paid={total_paid:.2f}"
        
        return True, ""
