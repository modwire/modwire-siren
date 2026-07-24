# Delivery

- Open PRs ready for review unless the user explicitly requests a draft. Target the user-named base; otherwise stop
  rather than changing branch, base, or review status.
- After acceptance, update the linked issue and Project. A merged PR uses `Fixes #<issue>`; confirm its remote head is
  deleted, prune local tracking, and retain only protected long-lived branches unless instructed otherwise.
