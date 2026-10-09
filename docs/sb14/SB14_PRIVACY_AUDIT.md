# [SB-14 Audit 12] Privacy & Sensitive Data Masking Audit

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-14 Production Hardening & Reliability Engineering

---

## 1. Privacy Protection Standards

- **로그 마스킹 규칙**:
  - `password`, `token`, `secret`, `api_key`, `raw_conversation`, `audio_bytes`, `image_base64`는 로그에 평문으로 남지 않고 `[REDACTED]`로 마스킹됨.
