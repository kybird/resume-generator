import os
import sys
from career_writer.cli.init import init_baseline
from career_writer.cli.interviewer import Interviewer
from career_writer.generator import Generator
from career_writer.models.config import Config
from career_writer.llm.openai_client import OpenAIClient
from career_writer.llm.local_client import LocalClient
from career_writer.llm.groq_client import GroqClient
from career_writer.llm.google_client import GoogleClient
from career_writer.llm.antigravity_client import AntigravityClient

class Menu:
    @staticmethod
    def print_header():
        print("\n" + "="*40)
        print("  CAREER STATEMENT GENERATOR (v2)")
        print("  Baseline + Linked Facts Architecture")
        print("="*40)

    @staticmethod
    def print_menu():
        print("\n1. Start Interview (Add Facts)")
        print("2. Generate Resume (Merge Baseline + Facts)")
        print("3. Authenticate (Antigravity)")
        print("4. Exit")
        print("-" * 30)

    @staticmethod
    def get_choice():
        return input("Select option (1-4): ").strip()

def main():
    # 1. Load Config
    try:
        config = Config.load()
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    # 2. Init LLM
    try:
        if config.llm.provider == "openai":
            llm = OpenAIClient(api_key=config.llm.api_key, model_name=config.llm.model_name)
        elif config.llm.provider == "local":
            llm = LocalClient(endpoint_url=config.llm.files_url)
        elif config.llm.provider == "groq":
            llm = GroqClient(api_key=config.llm.api_key, model_name=config.llm.model_name)
        elif config.llm.provider == "google":
            llm = GoogleClient(api_key=config.llm.api_key, model_name=config.llm.model_name)
        elif config.llm.provider == "antigravity":
            llm = AntigravityClient(api_key=config.llm.api_key)
        else:
            print(f"Unknown provider: {config.llm.provider}")
            return
    except Exception as e:
        print(f"LLM Init Failed: {e}")
        return

    # 3. Init Baseline (Frozen Metadata)
    baseline = init_baseline(config, llm)
    if not baseline:
        print("Failed to initialize baseline. Exiting.")
        return

    # 4. Main Loop
    while True:
        Menu.print_header()
        print(f"User: {baseline.person.name} | Experiences: {len(baseline.experiences)}")
        Menu.print_menu()
        choice = Menu.get_choice()

        if choice == "1":
            interviewer = Interviewer(llm, baseline)
            interviewer.start()
            
        elif choice == "2":
            print("\nGenerating Resume...")
            gen = Generator(llm)
            result = gen.generate_resume()
            print("\n" + "-"*20 + " Generated Output " + "-"*20)
            print(result[:500] + "...\n(See output/v2_resume.md for full text)")
            input("\nPress Enter to continue...")

        elif choice == "3":
            if isinstance(llm, AntigravityClient):
                llm.authenticate()
            else:
                print("Provider is not Antigravity.")
                
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid.")

if __name__ == "__main__":
    main()
