from __future__ import annotations

import sys
import time

from strands import Agent
from strands.models.ollama import OllamaModel
from strands.agent.conversation_manager import SlidingWindowConversationManager

from aria.config import AgentConfig, DEFAULT_CONFIG
from aria.prompts import SYSTEM_PROMPT, REPORT_PROMPT
from aria.ui import StreamHandler, Terminal


class TriageAgent:
    """Stateful CloudOps triage agent powered by a local LLM via Strands SDK."""

    def __init__(self, config: AgentConfig = DEFAULT_CONFIG) -> None:
        self._config = config
        self._start = time.time()
        self._handler = StreamHandler()
        # num_ctx passed via options dict - Ollama-native param not exposed as first-class OllamaModel arg
        self._model = OllamaModel(
            host=config.host,
            model_id=config.model_id,
            keep_alive=config.keep_alive,
            temperature=config.temperature,
            options={"num_ctx": config.context_window},
        )
        self._agent = Agent(
            model=self._model,
            tools=[],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=self._handler,
            # Chosen over SummarizingConversationManager - triage sessions are bounded; recent context > compressed history
            conversation_manager=SlidingWindowConversationManager(window_size=config.window_size),
            agent_id="aria-triage-v1",
            name=config.agent_name,
            description=config.agent_description,
        )
        self._ui = Terminal()

    def run(self) -> None:
        """Start the interactive triage REPL."""
        self._ui.welcome(self._config.model_id)
        print()
        self._ui.commands()
        self._ui.rule()

        while True:
            try:
                user_input = self._ui.prompt()
            except (EOFError, KeyboardInterrupt):
                print()
                self._ui.farewell(self._elapsed(), len(self._agent.messages))
                sys.exit(0)

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd in ("/quit", "/exit"):
                self._ui.farewell(self._elapsed(), len(self._agent.messages))
                sys.exit(0)
            elif cmd == "/report":
                self._ui.rule("INCIDENT REPORT")
                self.generate_report()
                self._ui.rule()
            elif cmd == "/history":
                self._show_history()
            elif cmd == "/reset":
                self._reset()
            else:
                print()
                # Catch ResponseError 404 so a cold-evicted model gives an actionable message, not a raw traceback
                try:
                    self._agent(user_input)
                except Exception as e:
                    msg = str(e)
                    if "not found" in msg.lower() or "404" in msg:
                        self._ui.error(
                            "Model Unavailable",
                            f"The model '{self._config.model_id}' disappeared mid-session.\n\n"
                            "Restart Ollama with OLLAMA_MODELS pointing to your models folder,\n"
                            "then re-run: python main.py",
                        )
                        sys.exit(1)
                    raise
                print()
                self._ui.rule()

    def generate_report(self) -> None:
        self._ui.info("Generating incident report…")
        self._agent(REPORT_PROMPT)
        print()

    def _show_history(self) -> None:
        messages = self._agent.messages
        count = len(messages)
        self._ui.info(f"Session messages: {count}")

        recent = messages[-6:] if len(messages) >= 6 else messages
        for msg in recent:
            role = msg.get("role", "?")
            content = msg.get("content", "")
            if isinstance(content, list):
                text = " ".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            else:
                text = str(content)

            preview = text[:120].replace("\n", " ")
            if len(text) > 120:
                preview += "…"

            self._ui.info(f"  {role}: {preview}")

    def _reset(self) -> None:
        self._agent.messages.clear()
        self._start = time.time()
        self._ui.info("Session cleared - ready for new triage.")

    def _elapsed(self) -> str:
        secs = int(time.time() - self._start)
        m, s = divmod(secs, 60)
        return f"{m}m {s}s"
