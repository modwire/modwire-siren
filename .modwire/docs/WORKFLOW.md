# Delivery

Open pull requests ready for review by default. Create a draft only when the user explicitly requests one.
Target the base branch named by the user. Any fallback must preserve the requested branch, base, and review status;
otherwise stop and ask.

After the user accepts completed work, update the linked GitHub issue and Project status. A merged pull request must close its issue with `Fixes #<issue>`; confirm its head branch is deleted remotely and prune its local tracking branch. Keep only protected long-lived branches unless instructed otherwise.
