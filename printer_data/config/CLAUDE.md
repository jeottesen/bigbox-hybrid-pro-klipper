# Working in this repo

## Doc scope

`docs/printer-spec-sheet.md` and `docs/printer-upgrade-plan.md` are about
the printer only: hardware, wiring, motors, probe, firmware, motion tuning,
print quality. Nothing about the repo itself, git, klipper-backup,
Mainsail/Fluidd, or any other tooling belongs in them. That kind of thing
goes in commit messages, PR descriptions, or the README instead.

## Making changes

Anything beyond a trivial fix (typo, a stale value, a one-line doc
correction) goes through a branch and a pull request, not straight to
`main`. This applies especially to anything that changes the repo's
structure, `.env`/secrets handling, or how the automated backup behaves.
