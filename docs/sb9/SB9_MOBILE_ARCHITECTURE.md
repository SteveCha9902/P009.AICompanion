# [SB-9 Architecture 2] Mobile Multi-Character Client Architecture

- **작성자**: 🐟 코다리 (Lead Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-9 Multi-Character Mobile Studio & Real-Time Switching UX

---

## 1. Client-Server Architecture

```text
                  Backend (Authoritative Truth)
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
           Registry        Resolver      Factory
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                       REST Endpoints
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
        characterApi.ts             characterCreationApi.ts
               │                             │
               └──────────────┬──────────────┘
                              ▼
                     useCharacterStore
                     (UI & Cache State)
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
        CharacterGallery   CompanionScreen  CreationWizard
```
