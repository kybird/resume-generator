from typing import List, Optional
import sys

class Menu:
    @staticmethod
    def print_header(text: str):
        print(f"\n{'='*40}")
        print(f" {text}")
        print(f"{'='*40}")

    @staticmethod
    def print_section(text: str):
        print(f"\n[{text}]")
        print("-" * 20)

    @staticmethod
    def print_info(text: str):
        print(f"[INFO] {text}")

    @staticmethod
    def print_warn(text: str):
        print(f"[WARN] {text}")
    
    @staticmethod
    def print_error(text: str):
        print(f"[ERROR] {text}")

    @staticmethod
    def get_input(prompt: str, default: Optional[str] = None) -> str:
        prompt_text = f"{prompt} "
        if default:
            prompt_text += f"[{default}] "
        prompt_text += ": "
        
        user_input = input(prompt_text).strip()
        return user_input if user_input else (default or "")

    @staticmethod
    def select_option(options: List[str], prompt: str = "Select an option") -> int:
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        
        while True:
            choice = input(f"\n{prompt} (1-{len(options)}): ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(options):
                    return idx - 1
            print("Invalid selection. Please try again.")

    @staticmethod
    def confirm(question: str, default: bool = True) -> bool:
        choice = input(f"{question} (y/n) [{'Y/n' if default else 'y/N'}]: ").strip().lower()
        if not choice:
            return default
        return choice == 'y'

    @staticmethod
    def exit_app():
        print("\nExiting. Goodbye!")
        sys.exit(0)
