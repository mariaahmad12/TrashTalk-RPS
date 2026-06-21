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

# New Premium Feature: Savage streaks
ULTRA_ROASTS = [
    "THREE IN A ROW?! You are mathematically a disaster.",
    "A triple loss streak? My artificial intelligence is feeling secondhand embarrassment.",
    "Unbelievable. Even a random number generator has more strategy than you right now."
]

# --- GAME ENGINE MACHINES ---
def get_computer_choice():
    return random.choice(CHOICES)

def get_player_choice():
    choice = input("Choose rock, paper, scissors (or 'quit'): ").lower().strip()
    return choice

def determine_winner(player, computer):
    if player == computer:
        return "tie"
    elif (player == "rock" and computer == "scissors") or \
         (player == "scissors" and computer == "paper") or \
         (player == "paper" and computer == "rock"):
        return "player"
    else:
        return "computer"

# --- THE MAIN EXECUTIVE CONTROL ROOM ---
def main():
    player_score = 0
    computer_score = 0
    total_rounds = 0
    player_streak = 0
    computer_streak = 0
    
    print("==============================================")
    print("=== WELCOME TO TRASH-TALK RPS: ULTRA EDITION ===")
    print("==============================================\n")

    while True:
        player = get_player_choice()
        
        if player == "quit":
            break
            
        if player not in CHOICES:
            print("That's not a valid move! Focus up and try again.\n")
            continue

        total_rounds += 1
        computer = get_computer_choice()
        print(f"\n-> You played: {player.upper()} | Computer played: {computer.upper()}")

        result = determine_winner(player, computer)
        
        # PROCESSING OUTCOMES & STREAKS
        if result == "tie":
            player_streak = 0
            computer_streak = 0
            print(f"COMP: {random.choice(TIE_REACTIONS)}")
            
        elif result == "player":
            player_score += 1
            player_streak += 1
            computer_streak = 0  # Computer's streak is broken
            print(f"COMP: {random.choice(LOSS_REACTIONS)}")
            if player_streak >= 3:
                print("🔥 You're on a 3+ win streak! The computer is sweating.")
                
        else:
            computer_score += 1
            computer_streak += 1
            player_streak = 0  # Player's streak is broken
            
            # Check if computer earned an Ultra Roast
            if computer_streak >= 3:
                print(f"🚨 ULTRA ROAST 🚨\nCOMP: {random.choice(ULTRA_ROASTS)}")
                computer_streak = 0 # Reset so it doesn't spam every single round
            else:
                print(f"COMP: {random.choice(WIN_TAUNTS)}")
            
        # Display Live Scoreboard
        print(f"[Score -> You: {player_score} | Computer: {computer_score}]")
        print("-" * 46 + "\n")

    # --- END GAME FINAL METRICS PANEL ---
    print("\n==============================================")
    print("              FINAL MATCH REPORT              ")
    print("==============================================")
    print(f"Total Rounds Contested : {total_rounds}")
    print(f"Final Score            : You {player_score} - {computer_score} Computer")
    
    if total_rounds > 0:
        # Calculate performance analytics
        win_rate = (player_score / total_rounds) * 100
        tie_count = total_rounds - (player_score + computer_score)
        tie_rate = (tie_count / total_rounds) * 100
        
        print(f"Your Win Efficiency    : {win_rate:.1f}%")
        print(f"Match Tie Ratio        : {tie_rate:.1f}%")
    print("==============================================")
    print("Thanks for playing! Go dry your tears.")
    print("==============================================\n")

if __name__ == "__main__":
    main()