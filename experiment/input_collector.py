"""
Input collection and validation for the Bill Splitter application.
Handles user data entry and validation logic.
"""
from typing import Dict, Optional
from models import Dish, Person

class InputCollector:
    """Manages data collection and storage for dishes and people."""
    
    def __init__(self):
        self.dishes: Dict[str, Dish] = {}
        self.people: Dict[str, Person] = {}
        self.current_person_index: int = 0
        self.selected_dishes: list = []

    def add_dish(self, name: str, price_str: str) -> bool:
        """
        Add a dish to the collection.
        
        Args:
            name: The dish name
            price_str: The price as a string
            
        Returns:
            True if dish was added successfully, False otherwise
        """
        name = name.strip()
        price_str = price_str.strip()
        
        if not name or not price_str:
            return False
            
        if name in self.dishes:
            return False
            
        try:
            price = float(price_str)
            if price < 0:
                return False
            self.dishes[name] = Dish(name, price)
            return True
        except ValueError:
            return False

    def add_person(self, name: str) -> bool:
        """
        Add a person to the collection.
        
        Args:
            name: The person's name
            
        Returns:
            True if person was added successfully, False otherwise
        """
        name = name.strip()
        
        if not name:
            return False
            
        if name in self.people:
            return False
            
        self.people[name] = Person(name)
        return True

    def toggle_dish_selection(self, dish_name: str) -> None:
        """Toggle the selection state of a dish."""
        if dish_name in self.selected_dishes:
            self.selected_dishes.remove(dish_name)
        else:
            self.selected_dishes.append(dish_name)

    def assign_selected_dishes_to_current_person(self) -> None:
        """Assign all selected dishes to the current person."""
        people_list = list(self.people.values())
        
        if self.current_person_index < len(people_list):
            person = people_list[self.current_person_index]
            for dish_name in self.selected_dishes:
                if dish_name in self.dishes:
                    self.dishes[dish_name].add_eater(person.name)

    def advance_to_next_person(self) -> bool:
        """
        Move to the next person in the assignment process.
        
        Returns:
            True if there are more people to process, False if finished
        """
        self.assign_selected_dishes_to_current_person()
        self.current_person_index += 1
        self.selected_dishes = []
        
        return self.current_person_index < len(self.people)

    def get_current_person(self) -> Optional[Person]:
        """Get the person currently being assigned dishes."""
        people_list = list(self.people.values())
        
        if 0 <= self.current_person_index < len(people_list):
            return people_list[self.current_person_index]
        return None

    def is_last_person(self) -> bool:
        """Check if the current person is the last one to assign."""
        return self.current_person_index >= len(self.people) - 1

    def reset(self) -> None:
        """Reset all collected data."""
        self.dishes.clear()
        self.people.clear()
        self.current_person_index = 0
        self.selected_dishes.clear()

    def has_dishes(self) -> bool:
        """Check if any dishes have been added."""
        return len(self.dishes) > 0

    def has_people(self) -> bool:
        """Check if any people have been added."""
        return len(self.people) > 0