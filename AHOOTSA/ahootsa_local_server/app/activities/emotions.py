from typing import Any

from .base import ActivityBase, ActivityStep


class EmotionsActivity(ActivityBase):
    key = "emotions"
    title = "Reconocer emociones"
    description = "Actividad sencilla para identificar alegría, tristeza y enfado."

    _questions = {
        1: {
            "text": "Una persona sonríe porque ha recibido una buena noticia. ¿Está alegre, triste o enfadada?",
            "answer": "alegre",
        },
        2: {
            "text": "Una persona ha perdido algo importante y está llorando. ¿Está alegre, triste o enfadada?",
            "answer": "triste",
        },
        3: {
            "text": "Una persona frunce el ceño porque alguien le ha quitado su turno. ¿Está alegre, triste o enfadada?",
            "answer": "enfadada",
        },
    }

    def start(self, context: dict[str, Any]) -> ActivityStep:
        question = self._questions[1]
        return ActivityStep(
            step=1,
            action="ask",
            text=question["text"],
            expected_answer=question["answer"],
            metadata={"choices": ["alegre", "triste", "enfadada"]},
        )

    def next_step(
        self,
        current_step: int,
        context: dict[str, Any],
    ) -> ActivityStep:
        next_number = current_step + 1
        question = self._questions.get(next_number)

        if question is None:
            return ActivityStep(
                step=current_step,
                action="finish",
                text="Actividad terminada. Gracias por participar.",
                completed=True,
                success=True,
            )

        return ActivityStep(
            step=next_number,
            action="ask",
            text=question["text"],
            expected_answer=question["answer"],
            metadata={"choices": ["alegre", "triste", "enfadada"]},
        )

    def evaluate(
        self,
        current_step: int,
        answer: str,
        context: dict[str, Any],
    ) -> ActivityStep:
        question = self._questions.get(current_step)
        if question is None:
            return ActivityStep(
                step=current_step,
                action="finish",
                text="La actividad ya ha terminado.",
                completed=True,
                success=True,
            )

        normalized = answer.strip().casefold()
        is_correct = question["answer"] in normalized

        if not is_correct:
            return ActivityStep(
                step=current_step,
                action="hint",
                text="Pista: fíjate en la expresión de la cara y en lo que acaba de ocurrir.",
                success=False,
                expected_answer=question["answer"],
                metadata={"retry": True},
            )

        next_result = self.next_step(current_step, context)
        if next_result.completed:
            next_result.text = "¡Muy bien! Has completado la actividad de emociones."
        else:
            next_result.text = f"Correcto. {next_result.text}"
        next_result.success = True
        return next_result
