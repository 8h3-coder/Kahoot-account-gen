import requests
import random
import string
import customtkinter as ctk
from colorama import init, Fore
import threading

init(autoreset=True)

url = "https://create.kahoot.it/rest/users"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://create.kahoot.it",
    "Referer": "https://create.kahoot.it/auth/register/signup-options",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}

write_lock = threading.Lock()

class AccountGeneratorApp:
    def __init__(self):
        """Initialize the main GUI window."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.geometry("500x400")
        self.root.title("Kahoot Account Generator")

        ctk.CTkLabel(self.root, text="Number of Threads:").pack(pady=5)
        self.thread_entry = ctk.CTkEntry(self.root)
        self.thread_entry.pack(pady=5)

        ctk.CTkLabel(self.root, text="Number of Accounts:").pack(pady=5)
        self.accounts_entry = ctk.CTkEntry(self.root)
        self.accounts_entry.pack(pady=5)

        self.generate_button = ctk.CTkButton(self.root, text="Generate Accounts", command=self.start_generation)
        self.generate_button.pack(pady=20)

        self.result_text = ctk.CTkTextbox(self.root, height=150)
        self.result_text.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.root, text="")
        self.status_label.pack(pady=5)

        self.success_count = 0
        self.error_count = 0

        self.root.mainloop()

    def start_generation(self):
        """Start the account generation process."""
        try:
            threads = int(self.thread_entry.get())
            accounts = int(self.accounts_entry.get())
            if threads <= 0 or accounts <= 0:
                raise ValueError("Values must be positive integers.")
        except ValueError as e:
            self.status_label.configure(text=f"Error: {e}", fg_color="red")
            return

        self.generate_button.configure(state="disabled")
        self.status_label.configure(text="Generating accounts, please wait...", fg_color="yellow")

        threading.Thread(target=self.generate_accounts, args=(threads, accounts), daemon=True).start()

    def generate_accounts(self, threads, accounts):
        """Generate accounts using threading."""
        with threading.Semaphore(threads):
            for i in range(accounts):
                threading.Thread(target=self.create_account, args=(i + 1,), daemon=True).start()

    def create_account(self, thread_id):
        """Create a single Kahoot account."""
        random_letters = ''.join(random.choices(string.ascii_lowercase, k=7))
        data = {
            "consents": {"termsConditions": True, "internalMarketing": False},
            "email": f"{random_letters}@outlook.com",
            "username": random_letters,
            "password": "Daapdevontop!",
            "primary_usage": "teacher",
            "primary_usage_type": "SCHOOL",
            "locale": "en"
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                token = response.json().get('access_token', 'No token')
                self.log_success(data['email'], data['password'], token)
                self.update_result(f"[SUCCESS] {data['email']}:{data['password']}")
                self.success_count += 1
            else:
                self.update_result(f"[ERROR] {data['email']} (Status: {response.status_code})")
                self.error_count += 1
        except Exception as e:
            self.update_result(f"[EXCEPTION] Thread {thread_id}: {e}")
            self.error_count += 1

        if self.success_count + self.error_count == int(self.accounts_entry.get()):
            self.show_summary()

    def log_success(self, email, password, token):
        """Log successful accounts to files."""
        with write_lock:
            with open("token.txt", "a") as token_file:
                token_file.write(f"{token}\n")
            with open("credentials.txt", "a") as creds_file:
                creds_file.write(f"{email}:{password}\n")

    def update_result(self, message):
        """Update the result textbox."""
        self.result_text.insert("end", f"{message}\n")
        self.result_text.see("end")

    def show_summary(self):
        """Display a summary when generation is complete."""
        self.status_label.configure(
            text=f"Complete! Success: {self.success_count}, Errors: {self.error_count}",
            fg_color="green" if self.success_count > 0 else "red"
        )
        self.generate_button.configure(state="normal")


def console_mode():
    """Console mode for account generation."""
    threads = int(input("Number of threads: "))
    accounts = int(input("Number of accounts: "))
    with threading.Semaphore(threads):
        for i in range(accounts):
            threading.Thread(target=create_account_console, args=(i + 1,), daemon=True).start()

def create_account_console(thread_id):
    """Create a single Kahoot account in console mode."""
    random_letters = ''.join(random.choices(string.ascii_lowercase, k=7))
    data = {
        "consents": {"termsConditions": True, "internalMarketing": False},
        "email": f"{random_letters}@outlook.com",
        "username": random_letters,
        "password": "Daapdevontop!",
        "primary_usage": "teacher",
        "primary_usage_type": "SCHOOL",
        "locale": "en"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            token = response.json().get('access_token', 'No token')
            with write_lock:
                with open("token.txt", "a") as token_file:
                    token_file.write(f"{token}\n")
                with open("credentials.txt", "a") as creds_file:
                    creds_file.write(f"{data['email']}:{data['password']}\n")
            print(Fore.GREEN + f"[SUCCESS] {data['email']}:{data['password']}")
        else:
            print(Fore.RED + f"[ERROR] {data['email']} (Status: {response.status_code})")
    except Exception as e:
        print(Fore.RED + f"[EXCEPTION] Thread {thread_id}: {e}")


if __name__ == "__main__":
    print(Fore.YELLOW + "[*] Choose your mode:")
    print("1. Console Mode")
    print("2. GUI Mode")
    mode = input("Enter mode (1 or 2): ")

    if mode == "1":
        console_mode()
    elif mode == "2":
        AccountGeneratorApp()
    else:
        print(Fore.RED + "Invalid mode selected.")
