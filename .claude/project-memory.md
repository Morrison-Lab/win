# Project memory

Decisions and facts about this repository that are not visible in the code.

## History and no-censoring event macros

- The shared macros `\hist{X}{k}`, `\trthist`, `\trtvalhist`, `\covhist`, `\covvalhist`, `\censhist`, `\censvalhist` and `\eventnocens` landed in `Morrison-Lab/macros#119` (2026-10-09).
  Chapters 17 and 19-21 use them for every subscripted history and for the no-censoring event indicator (#134, 2026-11-05).
- The names proposed in #76 (`\bA`, `\bL`, `\ba`, `\bl`) were not used.
  `\ba` is already `\begin{aligned}` in the macros, and the lab names macros for concepts, not for letter and decoration.
- Still raw LaTeX: bare `\bar{a}` and `\bar{c}` (a whole history, about 139 uses) and `\bar{U}_k`.
  #76 stays open for them; design a subscript-less form of `\hist` in `Morrison-Lab/macros` first, then sweep.
