from __future__ import annotations

import sys


class StreamHandler:
    """Callable callback that flushes streamed tokens directly to stdout."""

    def __call__(self, **kwargs) -> None:
        chunk = kwargs.get("data", "")
        if chunk:
            sys.stdout.write(chunk)
            sys.stdout.flush()


class Terminal:
    """Rich-powered terminal UI with plain-text fallback."""

    def __init__(self) -> None:
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.rule import Rule
            from rich.text import Text

            self._Console = Console
            self._Panel = Panel
            self._Table = Table
            self._Rule = Rule
            self._Text = Text
            self._console = Console()
            self.rich = True
        except ImportError:
            self.rich = False

    def welcome(self, model_id: str) -> None:
        if self.rich:
            banner = self._Text.assemble(
                ("ARIA\n", "bold cyan"),
                ("Autonomous Root-cause Intelligence Agent\n", "italic cyan"),
                ("\nPrivacy-first CloudOps Triage  |  All data stays local\n", "dim"),
                (f"Model: {model_id} via Ollama  |  Stack: Strands SDK", "dim"),
            )
            self._console.print(
                self._Panel(
                    banner,
                    title="[bold cyan]CloudOps Triage Agent[/bold cyan]",
                    subtitle="[dim]AWS UG Madurai — Builders Skill Sprint[/dim]",
                    border_style="cyan",
                )
            )
        else:
            print("=" * 62)
            print("  ARIA — Autonomous Root-cause Intelligence Agent")
            print("  Privacy-first CloudOps Triage  |  All data stays local")
            print(f"  Model: {model_id} via Ollama  |  Stack: Strands SDK")
            print("=" * 62)

    def commands(self) -> None:
        if self.rich:
            t = self._Table(show_header=False, box=None, padding=(0, 2))
            t.add_column(style="bold yellow")
            t.add_column(style="dim")
            t.add_row("/report", "Generate a full markdown incident report")
            t.add_row("/history", "Show conversation message count + last 3 exchanges")
            t.add_row("/reset", "Clear session and start a fresh triage")
            t.add_row("/quit", "Exit and print session stats")
            self._console.print(t)
        else:
            print("Commands: /report | /history | /reset | /quit")

    def rule(self, title: str = "") -> None:
        if self.rich:
            self._console.print(self._Rule(title, style="dim cyan"))
        else:
            sep = f"{'─' * 60}"
            print(f"{sep} {title}" if title else sep)

    def info(self, msg: str) -> None:
        if self.rich:
            self._console.print(msg, style="dim")
        else:
            print(msg)

    def prompt(self) -> str:
        if self.rich:
            return self._console.input("[bold green]>[/bold green] ").strip()
        return input("> ").strip()

    def error(self, title: str, body: str) -> None:
        if self.rich:
            self._console.print(
                self._Panel(body, title=f"[red]{title}[/red]", border_style="red")
            )
        else:
            print(f"\n[{title}]\n{body}")

    def farewell(self, duration: str, msg_count: int) -> None:
        body = (
            f"Session duration:   {duration}\n"
            f"Messages exchanged: {msg_count}\n\n"
            "Stay calm, triage methodically. Good luck out there."
        )
        if self.rich:
            self._console.print(
                self._Panel(body, title="[cyan]ARIA — Session Closed[/cyan]", border_style="cyan")
            )
        else:
            print(f"\n{body}")
