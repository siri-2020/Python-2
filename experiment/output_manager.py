"""
Output management for the Bill Splitter application.
Handles file generation and result formatting.
"""
import datetime
import os
from typing import Dict, Optional
from models import Dish, Person

class OutputManager:
    """Manages output generation and file operations."""
    
    @staticmethod
    def generate_filename() -> str:
        """
        Generate a timestamped filename for the bill.
        
        Returns:
            Filename string in format: bill_YYYY-MM-DD_HH-MM-SS.txt
        """
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        return f"bill_{timestamp}.txt"

    @staticmethod
    def save_bill_to_file(
        dishes: Dict[str, Dish],
        people: Dict[str, Person],
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Save the bill summary to a text file.
        
        Args:
            dishes: Dictionary of dish names to Dish objects
            people: Dictionary of person names to Person objects
            filename: Optional custom filename. If None, generates timestamped filename
            
        Returns:
            The filename if successful, None if failed
        """
        if filename is None:
            filename = OutputManager.generate_filename()
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                # Write header
                f.write("=" * 50 + "\n")
                f.write("BILL SUMMARY\n")
                f.write("=" * 50 + "\n")
                
                now = datetime.datetime.now()
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"Generated: {timestamp}\n\n")
                
                # Write individual totals
                f.write("INDIVIDUAL AMOUNTS:\n")
                f.write("-" * 50 + "\n")
                for person in people.values():
                    f.write(f"{person.name:.<40} THB {person.total:>8.2f}\n")
                
                # Write total
                total_bill = sum(dish.price for dish in dishes.values())
                f.write("-" * 50 + "\n")
                f.write(f"{'TOTAL BILL':.<40} THB {total_bill:>8.2f}\n")
                f.write("=" * 50 + "\n\n")
                
                # Write dish breakdown
                f.write("DISH BREAKDOWN:\n")
                f.write("-" * 50 + "\n")
                for dish in dishes.values():
                    f.write(f"\n{dish.name} - THB {dish.price:.2f}\n")
                    if dish.eaters:
                        f.write(f"  Shared by: {', '.join(dish.eaters)}\n")
                        f.write(f"  Per person: THB {dish.get_shared_price():.2f}\n")
                    else:
                        f.write("  Not assigned to anyone\n")
                
                f.write("\n" + "=" * 50 + "\n")
            
            print(f"Bill successfully saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error saving bill to file: {e}")
            return None

    @staticmethod
    def get_file_absolute_path(filename: str) -> Optional[str]:
        """
        Get the absolute path of a file.
        
        Args:
            filename: The filename to get the path for
            
        Returns:
            Absolute path string, or None if error occurs
        """
        try:
            return os.path.abspath(filename)
        except Exception as e:
            print(f"Error getting file path: {e}")
            return None

    @staticmethod
    def format_currency(amount: float) -> str:
        """
        Format an amount as currency.
        
        Args:
            amount: The amount to format
            
        Returns:
            Formatted string like "THB 123.45"
        """
        return f"THB {amount:.2f}"

    @staticmethod
    def format_person_summary(name: str, amount: float) -> str:
        """
        Format a person's bill summary line.
        
        Args:
            name: Person's name
            amount: Amount they owe
            
        Returns:
            Formatted string
        """
        return f"{name}: {OutputManager.format_currency(amount)}"