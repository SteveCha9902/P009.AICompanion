from app.domain.memory.relationship_memory import MemoryType, RelationshipMemory
from app.domain.proactive.proactive_context import ProactiveDialogueStyle

class ConversationStarterGenerator:
    """
    Generates warm, empathetic proactive conversation starters adhering to Amy's Persona Guide.
    STRICTLY FORBIDS interrogative or supervisory nagging ("왜 안 해?", "오늘 운동 안 했네?").
    """

    STARTER_TEMPLATES = {
        MemoryType.PET: {
            ProactiveDialogueStyle.REMINISCENCE: "지난번에 이야기했던 강아지(반려동물)는 요즘도 건강하고 씩씩하게 잘 지내고 있어?",
            ProactiveDialogueStyle.GREETING: "오늘 반려동물이랑 산책이나 놀이 시간은 가졌어? 보기만 해도 힐링되지!",
            ProactiveDialogueStyle.ENCOURAGEMENT: "동물이 주는 따뜻한 에너지가 오늘 하루도 큰 힘이 되었으면 좋겠어.",
            ProactiveDialogueStyle.OBSERVATION: "반려동물이랑 함께하는 일상은 참 소중하고 따뜻한 것 같아."
        },
        MemoryType.OBJECT: { # e.g. Plant, Mug
            ProactiveDialogueStyle.REMINISCENCE: "전에 이야기했던 그 식물(화분)은 잎도 잘 돋아나고 무럭무럭 잘 자라고 있어?",
            ProactiveDialogueStyle.GREETING: "초록색 식물을 보고 있으면 왠지 마음이 차분해지는 기분이 들지 않아?",
            ProactiveDialogueStyle.ENCOURAGEMENT: "정성껏 보살펴준 만큼 식물도 예쁜 모습으로 보답할 거야.",
            ProactiveDialogueStyle.OBSERVATION: "방 한구석에 식물이 싱그럽게 자리 잡고 있으니 분위기가 참 화사해 보여."
        },
        MemoryType.PROJECT: {
            ProactiveDialogueStyle.REMINISCENCE: "지난번에 집중해서 준비하던 프로젝트는 요즘 어떻게 진행되고 있어?",
            ProactiveDialogueStyle.GREETING: "오늘 작업하느라 피곤하진 않았어? 머리 식힐 여유도 꼭 챙겨!",
            ProactiveDialogueStyle.ENCOURAGEMENT: "꾸준히 한 걸음씩 나아가는 모습 정말 멋져. 오늘도 힘내자!",
            ProactiveDialogueStyle.OBSERVATION: "무언가에 깊이 몰입해서 열정을 쏟는 모습은 언제 봐도 참 보기 좋아."
        },
        MemoryType.HOBBY: {
            ProactiveDialogueStyle.REMINISCENCE: "요즘 새로 시작했던 취미 활동은 재미있게 즐기고 있어?",
            ProactiveDialogueStyle.GREETING: "취미에 푹 빠져서 보내는 시간만큼 기분 전환에 좋은 것도 없는 것 같아.",
            ProactiveDialogueStyle.ENCOURAGEMENT: "잘하고 못하고를 떠나서, 내가 좋아하는 것에 온전히 몰입하는 순간이 가장 값진 거야.",
            ProactiveDialogueStyle.OBSERVATION: "여가 시간에 좋아하는 일을 즐기는 여유가 참 멋지고 좋아 보여."
        },
        MemoryType.GOAL: {
            ProactiveDialogueStyle.REMINISCENCE: "목표를 향해 차근차근 나아가는 과정은 어때? 조급해하지 말고 천천히 가자.",
            ProactiveDialogueStyle.GREETING: "오늘도 나만의 작은 목표를 위해 고생 많았어!",
            ProactiveDialogueStyle.ENCOURAGEMENT: "지금처럼 꾸준히 하면 분명 멋진 결과를 만날 수 있을 거야. 언제나 응원해!",
            ProactiveDialogueStyle.OBSERVATION: "스스로를 성장시키기 위해 노력하는 모습이 정말 빛나 보여."
        }
    }

    DEFAULT_STARTERS = {
        ProactiveDialogueStyle.GREETING: "오늘 하루는 어떻게 보냈어? 편안한 시간 보내고 있어?",
        ProactiveDialogueStyle.REMINISCENCE: "문득 지난번에 나눴던 이야기들이 생각나서 말 걸어봤어.",
        ProactiveDialogueStyle.ENCOURAGEMENT: "오늘 하루도 정말 수고 많았어. 따뜻하고 포근한 저녁 되길 바라!",
        ProactiveDialogueStyle.OBSERVATION: "가만히 함께 시간을 보내는 이 순간이 참 편안하고 좋다."
    }

    @classmethod
    def generate_starter(
        cls,
        memory: RelationshipMemory,
        style: ProactiveDialogueStyle
    ) -> str:
        type_dict = cls.STARTER_TEMPLATES.get(memory.memory_type, {})
        return type_dict.get(style, cls.DEFAULT_STARTERS.get(style, "오늘 하루도 참 고생 많았어!"))
