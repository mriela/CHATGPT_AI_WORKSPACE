# SPALITUDA Receive Workflow

## Purpose
SPALITUDA receives work prepared on MRIELA through GitHub.

## Before Starting
- Make sure MRIELA has already pushed the latest work to GitHub.
- Work from MRIELA is expected under handoff/to-SPALITUDA/.
- Keep GitHub as the shared source of truth.

## Receive Work
Run on SPALITUDA:

```powershell
git -C C:\AI_AGENT_WORKSPACE_MRIELA\CHATGPT_AI_WORKSPACE pull
```

## Check Received Files
Review the files from MRIELA:

- handoff/to-SPALITUDA/
- assets/
- tasks/
- docs/

## Continue Work on SPALITUDA
- Move or copy needed files into the active SPALITUDA project area.
- Use SPALITUDA for Unity, VRChat SDK, builds, and other heavy GPU work.
- If SPALITUDA sends work back to MRIELA, place it under handoff/from-SPALITUDA/.

## Finish Work
After updating files on SPALITUDA, run:

```powershell
git -C C:\AI_AGENT_WORKSPACE_MRIELA\CHATGPT_AI_WORKSPACE status
git -C C:\AI_AGENT_WORKSPACE_MRIELA\CHATGPT_AI_WORKSPACE add .
git -C C:\AI_AGENT_WORKSPACE_MRIELA\CHATGPT_AI_WORKSPACE commit -m "Describe work done on SPALITUDA"
git -C C:\AI_AGENT_WORKSPACE_MRIELA\CHATGPT_AI_WORKSPACE push
```
