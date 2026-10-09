# [SB-15 Audit 9] Secret Management & Zero-Leakage Policy

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Secret Isolation Matrix

- **Zero Secret in Code**: 소스 코드, Dockerfile 이미지, 클라이언트 번들에 API Key/JWT Secret 하드코딩 0건.
- **Production Secret Injection**: Docker Secret 또는 Vault/KMS 환경 변수를 통해서만 런타임에 주입됨.
