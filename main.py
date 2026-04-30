import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from agent.gemini_agent import build_agent, ask_agent
from modules.educator import get_topics, validate_question, build_education_prompt
from modules.quiz import (
    build_quiz_prompt,
    parse_quiz_response,
    calculate_score,
    DIFFICULTY_LEVELS,
)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="civiciq",
        description="CivicIQ — AI-powered Election Process Education Assistant",
        epilog="""
Examples:
python main.py
python main.py --prompt "How do I vote?"
python main.py --quiz --topic "voting"
python main.py --topics
python main.py --no-color
python main.py --lang Hindi
""",
    )

    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Ask a single civic question non-interactively",
    )
    parser.add_argument(
        "--quiz",
        action="store_true",
        help="Start quiz mode directly",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="general elections",
        help="Topic for quiz mode (default: general elections)",
    )
    parser.add_argument(
        "--difficulty",
        choices=DIFFICULTY_LEVELS,
        default="beginner",
        help="Quiz difficulty level",
    )
    parser.add_argument(
        "--topics",
        action="store_true",
        help="List all available civic education topics",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output for screen readers or plain terminals",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="English",
        help="Response language (e.g. Hindi, Tamil, French)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="CivicIQ 1.0.0",
    )
    return parser.parse_args()


def make_console(no_color: bool) -> Console:
    return Console(highlight=not no_color, markup=not no_color)


def print_welcome(console: Console):
    console.print(
        Panel(
            "[bold cyan]🗳️ Welcome to CivicIQ[/bold cyan]\n"
            "[white]Your AI-powered Election Process Education Assistant[/white]\n\n"
            "[dim]Learn how elections work • Take civic quizzes • Track your progress[/dim]\n"
            "[dim]Type 'quiz' to start a quiz • 'learn' to explore topics • 'exit' to quit[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def print_response(console: Console, text: str, title: str = "CivicIQ"):
    console.print(
        Panel(
            text,
            title=f"[bold green]{title}[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )


def show_topics(console: Console):
    table = Table(
        title="📚 Available Civic Education Topics",
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("No.", style="cyan", width=4)
    table.add_column("Topic", style="white")

    for i, topic in enumerate(get_topics(), 1):
        table.add_row(str(i), topic)

    console.print(table)


def resolve_topic_selection(selection: str) -> str | None:
    """Convert a numeric topic choice into the real topic text."""
    selection = selection.strip()
    topics = get_topics()

    if selection.isdigit():
        idx = int(selection)
        if 1 <= idx <= len(topics):
            return topics[idx - 1]
        return None

    return selection


def run_quiz_mode(console: Console, chat, topic: str, difficulty: str):
    """Interactive quiz mode with scoring."""
    console.print(
        Panel(
            f"[bold yellow]🧠 Quiz Mode[/bold yellow]\n"
            f"Topic: [cyan]{topic}[/cyan] | Difficulty: [magenta]{difficulty}[/magenta]",
            border_style="yellow",
        )
    )

    with console.status("[bold cyan]Generating your civic quiz...[/bold cyan]", spinner="dots"):
        prompt = build_quiz_prompt(topic, difficulty, num_questions=3)
        raw = ask_agent(chat, prompt)
        quiz_data = parse_quiz_response(raw)

    if "error" in quiz_data or not quiz_data.get("questions"):
        console.print("[red]Could not generate quiz. Please try again.[/red]")
        return

    questions = quiz_data["questions"]
    user_answers = []
    correct_answers = []

    for i, q in enumerate(questions, 1):
        console.print(f"\n[bold cyan]Question {i}/{len(questions)}:[/bold cyan]")
        console.print(f"[white]{q['question']}[/white]\n")

        for opt in q["options"]:
            console.print(f"  {opt}")

        answer = Prompt.ask(
            "\n[bold yellow]Your answer (A/B/C/D)[/bold yellow]"
        ).strip().upper()

        user_answers.append(answer)
        correct_answers.append(q["correct"])

        if answer == q["correct"]:
            console.print(f"[bold green]✅ Correct![/bold green] {q['explanation']}")
        else:
            console.print(
                f"[bold red]❌ Incorrect.[/bold red] "
                f"Correct answer: [green]{q['correct']}[/green]\n{q['explanation']}"
            )

    result = calculate_score(user_answers, correct_answers)

    console.print(
        Panel(
            f"[bold]Quiz Complete![/bold]\n\n"
            f"Score: [cyan]{result['score']}/{result['total']}[/cyan] "
            f"([magenta]{result['percentage']}%[/magenta])\n\n"
            f"{result['feedback']}\n\n"
            f"[dim]Recommended next difficulty: {result['next_difficulty']}[/dim]",
            border_style="yellow",
            title="[bold yellow]Results[/bold yellow]",
        )
    )

    with console.status("[dim]Logging results to Google Sheets...[/dim]"):
        log_response = ask_agent(
            chat,
            f"Log quiz result: topic='{topic}', score={result['score']}, total={result['total']}, difficulty='{difficulty}'",
        )

    console.print(f"[dim]{log_response}[/dim]")


def main():
    args = parse_args()
    console = make_console(args.no_color)

    if args.topics:
        show_topics(console)
        sys.exit(0)

    print_welcome(console)

    with console.status("[bold cyan]Initializing CivicIQ...[/bold cyan]", spinner="dots"):
        chat = build_agent()

    console.print("[bold green]✅ CivicIQ is ready![/bold green]\n")

    if args.prompt:
        if not validate_question(args.prompt):
            console.print("[yellow]⚠️ Please ask a civic or election-related question.[/yellow]")
            sys.exit(1)

        with console.status("[bold cyan]Researching...[/bold cyan]", spinner="dots"):
            response = ask_agent(chat, build_education_prompt(args.prompt, args.lang))
        print_response(console, response)
        sys.exit(0)

    if args.quiz:
        run_quiz_mode(console, chat, args.topic, args.difficulty)
        sys.exit(0)

    console.print("[dim]Commands: 'quiz' | 'learn' | 'topics' | 'progress' | 'exit'[/dim]\n")

    while True:
        user_input = Prompt.ask("[bold yellow]You[/bold yellow]").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("[bold cyan]Stay civically engaged! Goodbye 🗳️[/bold cyan]")
            break

        elif user_input.lower() == "topics":
            show_topics(console)

        elif user_input.lower() == "quiz":
            topic_input = Prompt.ask("[cyan]Quiz topic[/cyan]", default="general elections")
            topic = resolve_topic_selection(topic_input)
            if not topic:
                console.print("[yellow]⚠️ Invalid topic number. Please choose one from the list.[/yellow]")
                continue

            difficulty = Prompt.ask(
                "[cyan]Difficulty[/cyan]",
                choices=DIFFICULTY_LEVELS,
                default="beginner",
            )
            run_quiz_mode(console, chat, topic, difficulty)

        elif user_input.lower() == "progress":
            with console.status("[cyan]Fetching your learning progress...[/cyan]", spinner="dots"):
                response = ask_agent(chat, "Show me my learning progress from Google Sheets")
            print_response(console, response, "Your Progress")

        elif user_input.lower() == "learn":
            show_topics(console)
            topic_selection = Prompt.ask("[cyan]Choose a topic to learn about[/cyan]")
            topic = resolve_topic_selection(topic_selection)

            if not topic:
                console.print("[yellow]⚠️ Invalid topic number. Please choose one from the list.[/yellow]")
                continue

            with console.status("[cyan]Preparing your lesson...[/cyan]", spinner="dots"):
                prompt = build_education_prompt(topic, args.lang)
                response = ask_agent(chat, prompt)
            print_response(console, response, "📚 Civic Lesson")

        else:
            if not validate_question(user_input):
                console.print(
                    "[yellow]⚠️ I focus on civic education and election processes.\n"
                    "Try: 'How does voting work?' or type 'topics' to see what I can teach.[/yellow]"
                )
                continue

            with console.status("[cyan]Researching...[/cyan]", spinner="dots"):
                response = ask_agent(chat, build_education_prompt(user_input, args.lang))
            print_response(console, response)


if __name__ == "__main__":
    main()