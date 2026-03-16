# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### GitHub 备份

- **用户**: sydical
- **Token**: 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
- **仓库**: https://github.com/sydical/Clawde-skills

### 快捷指令

| 指令 | 操作 |
|------|------|
| 备份Skills | 复制 ~/.openclaw/skills 到 workspace/skills，推送到 Clawde-skills 仓库 |
