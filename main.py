import flet as ft
import flet_audio as fta
import random
import asyncio
import os

# ---------------------------------------------------------------------------
# Palette — dark "arena" theme: charcoal/navy base with neon cyan/pink/gold
# ---------------------------------------------------------------------------
BG_TOP = "#161829"
BG_BOTTOM = "#0B0C14"
CARD_BG = "#1E2138"
CARD_BORDER = "#33365A"
NEON_CYAN = "#00F5D4"
NEON_PINK = "#FF2E93"
NEON_GOLD = "#FFD23F"
TEXT_LIGHT = "#F4F4F8"
TEXT_MUTED = "#8B8FA8"
WIN_COLOR = "#3DDC84"
LOSE_COLOR = "#FF4D6D"
TIE_COLOR = "#FFD23F"

CHOICE_EMOJI = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}

TRASH_TALK = {
    "win": [
        "GG. Better luck never.",
        "That was almost embarrassing to watch.",
        "Pack it up, champ.",
        "I have no sweat glands and I still didn't break one.",
        "Skill issue, detected and confirmed.",
    ],
    "lose": [
        "Beginner's luck. Run it back.",
        "Okay, fine, that one's on me.",
        "One point doesn't make a rivalry.",
        "My circuits slipped. That's all that happened.",
        "Cute. Won't happen again.",
    ],
    "tie": [
        "Great minds, identical hands.",
        "We're basically the same person.",
        "A standoff. How dramatic.",
        "Nobody wins. Everybody's mildly annoyed.",
    ],
}


def main(page: ft.Page):
    page.title = "Trash-Talk RPS"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 420
    page.window.height = 720
    page.padding = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = BG_BOTTOM

    scores = {"player": 0, "computer": 0}
    busy = {"value": False}

    # -----------------------------------------------------------------
    # Audio — in current Flet, Audio is a "Service" (not a visible
    # control), so instances go in page.services (not page.overlay),
    # and .play() is now a coroutine that must be awaited.
    # Install with: pip install flet-audio
    # Put your mp3 files in an "assets" folder next to this script:
    #   assets/win.mp3, assets/lose.mp3, assets/boom.mp3
    # -----------------------------------------------------------------
    win_sound = fta.Audio(src="win.mp3")
    lose_sound = fta.Audio(src="lose.mp3")
    win_round_sound = fta.Audio(src="win.mp3")  # reuses win.mp3 — no separate file needed
    boom_sound = fta.Audio(src="boom.mp3")
    page.services.extend([win_sound, lose_sound, win_round_sound, boom_sound])

    async def safe_play(audio_ctrl: fta.Audio):
        try:
            await audio_ctrl.play()
        except Exception:
            pass  # missing file or unsupported platform — fail quietly

    # -----------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------
    title_row = ft.Row(
        [
            ft.Text("TRASH-TALK", size=26, weight=ft.FontWeight.BOLD, color=NEON_PINK, italic=True),
            ft.Text("RPS", size=26, weight=ft.FontWeight.BOLD, color=NEON_CYAN),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=6,
    )
    subtitle = ft.Text("where pixels throw shade", size=12, color=TEXT_MUTED, italic=True)

    # -----------------------------------------------------------------
    # Scoreboard
    # -----------------------------------------------------------------
    def score_card(label, emoji, color):
        value_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=color)
        card = ft.Container(
            content=ft.Column(
                [
                    ft.Text(emoji, size=20),
                    value_text,
                    ft.Text(label, size=11, color=TEXT_MUTED),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=CARD_BG,
            border=ft.Border.all(1.5, color),
            border_radius=16,
            padding=14,
            width=150,
        )
        return card, value_text

    player_card, player_score_value = score_card("PLAYER", "🧑", NEON_CYAN)
    comp_card, comp_score_value = score_card("COMPUTER", "🤖", NEON_PINK)

    # -----------------------------------------------------------------
    # Battle arena — the signature visual: two AnimatedSwitchers reveal
    # each side's pick with a quick scale-pop, framed by a card whose
    # border recolors to match the round's outcome.
    # -----------------------------------------------------------------
    player_display = ft.AnimatedSwitcher(
        content=ft.Text("❔", size=46, key="p0"),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=250,
    )
    comp_display = ft.AnimatedSwitcher(
        content=ft.Text("❔", size=46, key="c0"),
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=250,
    )

    arena_ref = ft.Ref[ft.Container]()
    verdict_text = ft.Text(
        "Ready to start?", size=16, weight=ft.FontWeight.BOLD, color=TEXT_LIGHT,
        text_align=ft.TextAlign.CENTER,
    )
    trash_text = ft.Text("", size=13, italic=True, color=NEON_GOLD, text_align=ft.TextAlign.CENTER)

    arena = ft.Container(
        ref=arena_ref,
        content=ft.Column(
            [
                ft.Row(
                    [player_display, ft.Text("VS", size=18, color=TEXT_MUTED, weight=ft.FontWeight.BOLD), comp_display],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=24,
                ),
                ft.Container(height=10),
                verdict_text,
                trash_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=CARD_BG,
        border=ft.Border.all(2, CARD_BORDER),
        border_radius=20,
        padding=20,
        width=360,
        animate=ft.Animation(duration=250, curve=ft.AnimationCurve.EASE_OUT),
    )

    # -----------------------------------------------------------------
    # Choice buttons — round, glowing-border, scale up slightly on hover
    # -----------------------------------------------------------------
    def make_choice_button(choice, emoji, color):
        container = ft.Container(
            content=ft.Column(
                [ft.Text(emoji, size=30), ft.Text(choice.upper(), size=11, color=TEXT_MUTED)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            width=92,
            height=92,
            border_radius=50,
            bgcolor=CARD_BG,
            border=ft.Border.all(2, color),
            alignment=ft.Alignment.CENTER,
            ink=True,
            scale=1.0,
            animate_scale=ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_OUT),
            on_click=lambda e: page.run_task(play_round, choice),
        )

        def on_hover(e):
            container.scale = 1.08 if e.data else 1.0
            container.update()

        container.on_hover = on_hover
        return container

    rock_btn = make_choice_button("rock", "🪨", NEON_CYAN)
    paper_btn = make_choice_button("paper", "📄", NEON_GOLD)
    scissors_btn = make_choice_button("scissors", "✂️", NEON_PINK)

    quit_btn = ft.TextButton(
        "QUIT GAME",
        style=ft.ButtonStyle(color=LOSE_COLOR),
        on_click=lambda e: page.run_task(exit_game),
    )

    # -----------------------------------------------------------------
    # Game logic (async so sounds/animations never freeze the window)
    # -----------------------------------------------------------------
    async def play_round(choice):
        if busy["value"]:
            return
        busy["value"] = True

        comp_display.content = ft.Text("🤔", size=46, key=f"think-{random.random()}")
        verdict_text.value = "Computer is choosing..."
        verdict_text.color = TEXT_MUTED
        trash_text.value = ""
        page.update()
        await asyncio.sleep(0.45)

        comp = random.choice(["rock", "paper", "scissors"])

        if choice == comp:
            outcome = "tie"
            verdict_text.value = "A tie."
            verdict_text.color = TIE_COLOR
            arena_ref.current.border = ft.Border.all(2, TIE_COLOR)
        elif (
            (choice == "rock" and comp == "scissors")
            or (choice == "scissors" and comp == "paper")
            or (choice == "paper" and comp == "rock")
        ):
            scores["player"] += 1
            outcome = "win"
            verdict_text.value = "You won this round!"
            verdict_text.color = WIN_COLOR
            arena_ref.current.border = ft.Border.all(2, WIN_COLOR)
            await safe_play(win_round_sound)
        else:
            scores["computer"] += 1
            outcome = "lose"
            verdict_text.value = "Computer won this round!"
            verdict_text.color = LOSE_COLOR
            arena_ref.current.border = ft.Border.all(2, LOSE_COLOR)
            await safe_play(boom_sound)

        player_display.content = ft.Text(CHOICE_EMOJI[choice], size=46, key=f"p-{random.random()}")
        comp_display.content = ft.Text(CHOICE_EMOJI[comp], size=46, key=f"c-{random.random()}")
        trash_text.value = random.choice(TRASH_TALK[outcome])

        player_score_value.value = str(scores["player"])
        comp_score_value.value = str(scores["computer"])

        page.update()
        busy["value"] = False

    async def exit_game():
        if busy["value"]:
            return
        busy["value"] = True

        verdict_text.value = f"GAME OVER — Player {scores['player']} : {scores['computer']} Computer"
        verdict_text.color = TEXT_LIGHT
        trash_text.value = "Thanks for playing!"
        arena_ref.current.border = ft.Border.all(2, NEON_GOLD)
        page.update()

        if scores["player"] > scores["computer"]:
            await safe_play(win_sound)
        else:
            await safe_play(lose_sound)

        await asyncio.sleep(2)
        page.window.close()

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=20),
                    title_row,
                    subtitle,
                    ft.Container(height=16),
                    ft.Row([player_card, comp_card], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
                    ft.Container(height=18),
                    arena,
                    ft.Container(height=22),
                    ft.Row(
                        [rock_btn, paper_btn, scissors_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=14,
                    ),
                    ft.Container(height=10),
                    quit_btn,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[BG_TOP, BG_BOTTOM],
            ),
            expand=True,
            padding=10,
        )
    )


if __name__ == "__main__":
    # Flet errors out if assets_dir doesn't exist at all — create it
    # automatically so missing sound files never crash the app.
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_path, exist_ok=True)
    ft.run(main, assets_dir="assets")