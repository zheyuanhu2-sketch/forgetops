# Migration and workspace isolation verification

Verified on **2026-07-15 (Asia/Shanghai)**.

## Result

The active ForgetOps working tree and its project-owned development/runtime assets are on the `E:` drive. A targeted current-state search found no duplicate project signature in the normal user-controlled development locations on `C:`. This is a verification of the machine's current state, not a complete forensic proof of the earlier move and deletion.

## E-drive evidence

- `git rev-parse --show-toplevel` resolves to `E:/Codex Work/DataHub Hackathon`.
- The Git repository, Python environments, package/runtime caches, generated artifacts, web application, and installed web dependencies resolve beneath `E:\Codex Work\DataHub Hackathon`:
  - `.git`
  - `.venv`
  - `.venv-wsl`
  - `.runtime-home`
  - `.runtime-wsl\ext4.vhdx`
  - `.uv-cache`
  - `artifacts`
  - `web\node_modules`
- The Windows WSL registration for the project-owned distribution `forgetops-runtime` reports `E:\Codex Work\DataHub Hackathon\.runtime-wsl` as its `BasePath`.
- The project-local environments, runtime image, caches, and runtime artifacts above are ignored by Git. `git ls-files` reports no tracked files from those runtime directories.

These checks demonstrate that the current repository and its heavy project-owned runtime state are located on `E:`. They do not make claims about unrelated tools or global caches managed by Windows, Codex, npm, Python, or other applications.

## Current C-drive signature check

A read-only scan checked the user's normal development locations on `C:`:

- `C:\Users\胡哲源\Desktop`
- `C:\Users\胡哲源\Documents`
- `C:\Users\胡哲源\Downloads`
- conventional development roots such as `C:\Codex Work`, `C:\Projects`, `C:\Work`, `C:\Users\胡哲源\source`, and `C:\Users\胡哲源\repos` when present

The scan found:

- no directory whose exact name was `ForgetOps` or `DataHub Hackathon`; and
- no `pyproject.toml` carrying the project signature `name = "forgetops"`.

This supports the conclusion that there is no current duplicate in the likely original/user-development locations. It is deliberately not described as a byte-for-byte or forensic scan of every protected system directory, application cache, filesystem slack region, restore point, or backup on `C:`.

## Historical provenance limitation

The historical deletion provenance cannot be fully proven because no contemporaneous manifest was preserved with:

1. the exact original `C:` source path;
2. a complete file inventory and cryptographic hashes before the move;
3. matching hashes after the move; and
4. a deletion log tied to that inventory.

Without that original path/hash manifest, the current checks can establish the present location and absence of recognizable duplicates in the searched locations, but they cannot reconstruct or cryptographically attest every step of the past migration.

## Reverification commands

Run these commands from the repository root in PowerShell:

```powershell
git rev-parse --show-toplevel

@(
  '.git',
  '.venv',
  '.venv-wsl',
  '.runtime-home',
  '.runtime-wsl',
  '.runtime-wsl\ext4.vhdx',
  '.uv-cache',
  'artifacts',
  'web\node_modules'
) | ForEach-Object { (Resolve-Path -LiteralPath $_).Path }

Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' |
  ForEach-Object { Get-ItemProperty $_.PSPath } |
  Where-Object DistributionName -eq 'forgetops-runtime' |
  Select-Object DistributionName, BasePath, Version

git check-ignore -v -- .venv .venv-wsl .runtime-home .runtime-wsl .uv-cache artifacts/runtime
git ls-files -- .venv .venv-wsl .runtime-home .runtime-wsl .uv-cache artifacts/runtime
```

For any future migration, create and retain a signed or checksummed source manifest before moving files, verify the destination against it, and retain the deletion transcript. That would turn the historical limitation above into reproducible evidence.
