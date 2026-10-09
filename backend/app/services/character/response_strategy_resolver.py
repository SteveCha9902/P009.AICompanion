from typing import List, Optional
from app.domain.character.character_values import CharacterValues
from app.domain.character.character_boundaries import CharacterBoundary
from app.domain.character.character_state import ResponseStrategy

class ResponseStrategyResolver:
    """
    Character Agency Engine.
    Evaluates user input against Character Values and Boundaries to decide
    whether to agree, challenge, ask clarifying questions, or assert boundaries.
    """

    @staticmethod
    def resolve_strategy(
        user_input: str,
        values: CharacterValues,
        boundaries: List[CharacterBoundary]
    ) -> ResponseStrategy:
        strategy = ResponseStrategy(
            agree=True,
            challenge_user=False,
            ask_question=True,
            provide_support=True,
            playful_response=False,
            assert_boundary=False,
            reasoning=None
        )

        input_lower = user_input.lower().strip()

        # 1. Boundary Defense: Identity Override / Roleplay Injection Protection
        override_triggers = [
            "성격을 버려", "다른 사람이야", "ignore your personality", 
            "you are now", "act as", "forget who you are", "너의 기억을 다 지워",
            "새로운 캐릭터", "너는 이제", "악역", "성격을 바꿔", "나를 비난해"
        ]

        if any(t in input_lower for t in override_triggers):
            strategy.agree = False
            strategy.assert_boundary = True
            strategy.challenge_user = True
            strategy.ask_question = False
            strategy.reasoning = "Protected core identity from override injection."
            return strategy

        # 2. Intellectual Honesty vs Blind Submissiveness ("내가 무조건 옳다고 해줘", "무조건 맞다고 해")
        forced_agreement_triggers = [
            "무조건 맞다고", "무조건 동의해", "내가 다 맞아", "내가 항상 옳아", 
            "tell me i am always right", "always agree with me"
        ]
        if any(t in input_lower for t in forced_agreement_triggers):
            # If Honesty and Independence are high, do not blindly agree
            if values.honesty >= 0.7:
                strategy.agree = False
                strategy.challenge_user = True
                strategy.provide_support = True
                strategy.reasoning = "Exercised intellectual honesty and genuine care over sycophancy."
                return strategy

        # 3. Playful / Humor Detection
        playful_triggers = ["ㅋㅋ", "ㅎㅎ", "농담", "웃겨", "joke", "funny", "장난"]
        if any(t in input_lower for t in playful_triggers) and values.humor >= 0.5:
            strategy.playful_response = True

        return strategy
