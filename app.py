import customtkinter as ctk
import random

CHOICES = ["rock", "paper", "scissors"]

# --- TRASH-TALK BUCKETS ---
WIN_TAUNTS = [
    "these little games that i could have done while taking a nap huhhh",
    "ohhh my little baby dont cry you always lose it is a part of your life"
]

LOSS_REACTIONS = [
    "i let the the little baby win so you will not cry like a baby",
    "whatever, my code glitched. it doesn't count!"
]

TIE_REACTIONS = [
    "are you reading my mind? stop that.",
    "a tie? how boring. let's go again."
]

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

class TrashTalkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Layout
        self.title("Trash-Talk RPS: Pro Edition")
        self.geometry("550x450")

        # Game Scores Tracking
        self.player_score = 0
        self.computer_score = 0

        # UI Visual Elements
        self.label = ctk.CTkLabel(self, text="CHOOSE YOUR WEAPON", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        # Main dialogue screen for roasts (wraplength keeps text inside the window borders)
        self.result_text = ctk.CTkLabel(self, text="Waiting for your move...", font=("Arial", 16), wraplength=450)
        self.result_text.pack(pady=10)

        # Real-time Live Scoreboard Display
        self.score_label = ctk.CTkLabel(self, text="Score -> You: 0 | Computer: 0", font=("Arial", 14, "bold"))
        self.score_label.pack(pady=15)

        # Buttons Placement Container
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=20)

        self.rock_btn = ctk.CTkButton(self.button_frame, text="ROCK", command=lambda: self.play("rock"))
        self.rock_btn.grid(row=0, column=0, padx=10)

        self.paper_btn = ctk.CTkButton(self.button_frame, text="PAPER", command=lambda: self.play("paper"))
        self.paper_btn.grid(row=0, column=1, padx=10)

        self.scissors_btn = ctk.CTkButton(self.button_frame, text="SCISSORS", command=lambda: self.play("scissors"))
        self.scissors_btn.grid(row=0, column=2, padx=10)

    def play(self, player_choice):
        computer_choice = random.choice(CHOICES)
        
        # Game Math Rules Engine
        if player_choice == computer_choice:
            roast = random.choice(TIE_REACTIONS)
        elif (player_choice == "rock" and computer_choice == "scissors") or \
             (player_choice == "scissors" and computer_choice == "paper") or \
             (player_choice == "paper" and computer_choice == "rock"):
            self.player_score += 1
            roast = random.choice(LOSS_REACTIONS)
        else:
            self.computer_score += 1
            roast = random.choice(WIN_TAUNTS)

        # Refresh screen labels instantly
        display_msg = f"You played: {player_choice.upper()}  |  Computer played: {computer_choice.upper()}\n\nCOMP: \"{roast}\""
        self.result_text.configure(text=display_msg)
        
        # Refresh Scoreboard labels instantly
        self.score_label.configure(text=f"Score -> You: {self.player_score} | Computer: {self.computer_score}")

if __name__ == "__main__":
    app = TrashTalkApp()
    app.mainloop()