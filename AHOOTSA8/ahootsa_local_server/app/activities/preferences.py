from typing import Any

from .base import ActivityBase, ActivityStep


class PreferencesActivity(ActivityBase):
    key = "preferences"
    title = "Mis preferencias"
    description = "Conversación guiada breve sobre actividades y gustos."

    _prompts = {
        1: "¿Qué te gusta más: escuchar música, bailar o ver una película?",
        2: "¿Prefieres hacer actividades solo o acompañado?",
        3: "¿Hay alguna actividad que te gustaría hacer otro día?",
    }

    def start(self, context: dict[str, Any]) -> ActivityStep:
        return ActivityStep(
            step=1,
            action="ask",
            text=self._prompts[1],
            metadata={"open_answer": True},
        )

    def next_step(
        self,
        current_step: int,
        context: dict[str, Any],
    ) -> ActivityStep:
        next_number = current_step + 1
        prompt = self._prompts.get(next_number)
        if prompt is None:
            return ActivityStep(
                step=current_step,
                action="finish",
                text="Gracias. He terminado las preguntas sobre tus preferencias.",
                completed=True,
                success=True,
            )
        return ActivityStep(
            step=next_number,
            action="ask",
            text=prompt,
            metadata={"open_answer": True},
        )

    def evaluate(
        self,
        current_step: int,
        answer: str,
        context: dict[str, Any],
    ) -> ActivityStep:
        if not answer.strip():
            return ActivityStep(
                step=current_step,
                action="repeat",
                text="No he entendido la respuesta. Puedes responder con pocas palabras.",
                success=False,
                metadata={"retry": True},
            )

        result = self.next_step(current_step, context)
        if result.completed:
            result.text = "Gracias por contármelo. Hemos terminado esta actividad."
        else:
            result.text = f"Gracias por contármelo. {result.text}"
        result.success = True
        result.metadata["captured_preference"] = answer.strip()
        return result
