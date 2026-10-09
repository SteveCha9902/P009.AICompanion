# [SB-9 Architecture 7] Character Creation Wizard to Gallery Navigation Integration

- **작성자**: ✍️ Amy (Growth/UX Lead) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-9 Multi-Character Mobile Studio & Real-Time Switching UX

---

## 1. Creation to Gallery Flow

```mermaid
graph TD
    Gallery[Character Gallery Screen] -->|Click '+ 새 캐릭터 만들기'| Wizard[Character Creation Wizard]
    Wizard -->|Step 1~7 Inputs| Preview[POST /characters/preview]
    Preview -->|Step 8 Confirm & Create| Factory[POST /characters]
    Factory -->|201 Created| Success[Alert '캐릭터 생성 완료']
    Success -->|onCreated Callback| Refresh[useCharacterStore.refreshCharacters]
    Refresh -->|Auto Navigate Back| GalleryUpdated[Gallery Screen with New Character]
```
