# claude-skills

Personal [Claude Code](https://claude.com/claude-code) skills.

## Skills

| Skill | What it does |
|-------|--------------|
| [`blum-drawer`](./blum-drawer) | Interview-driven cut-list generator for Blum undermount drawer boxes (Tandem Plus BLUMOTION by default). Handles standard joinery and Shaper Origin box joints, with a deterministic calculator so the fraction math is never wrong. |

## Install

Clone and symlink a skill into your user skills directory:

```bash
git clone https://github.com/tgrahn2/claude-skills.git
ln -s "$PWD/claude-skills/blum-drawer" ~/.claude/skills/blum-drawer
```

Claude Code picks it up on the next session; invoke with `/blum-drawer`.

## License

[MIT](./LICENSE)
