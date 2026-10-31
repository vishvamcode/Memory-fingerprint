# In-brain (RAM FR1 iEEG) confirmatory result, 31 Oct 2026

Run with the code frozen on 23 Oct 2026 (FROZEN_SHA256 list hash 373dd738…), addendum registered at osf.io/xn4v9.

## Verdict by the frozen rule: AMBIGUOUS

| Measure | Value |
| --- | --- |
| People | 20 |
| Mean ΔAUC (brain + non-brain minus non-brain) | 0.0072 (median 0.0073) |
| 95% CI (hierarchical bootstrap, 10,000 draws, seed 20261021) | -0.0038 to 0.0236 |
| 90% CI | -0.0013 to 0.0216 |
| Robust-model 95% CI | -0.0037 to 0.0235 |
| One-sided Wilcoxon | W = 140, p = 0.10 |
| Smallest useful gain (SESOI) | 0.01 |

The 95% CI includes both 0 and 0.01, so the rule cannot call it a success or a failure.

Other numbers (not part of the verdict):

- Brain-only model AUC: mean 0.570 (range 0.497 to 0.671). Its permutation test was below 0.05 in 9 of 20 people.
- Non-brain model AUC: mean 0.596.
- ΔAUC was above 0 in 12 of 20 people and at least 0.01 in 9 of 20.
- Neighbour control: own-word ΔAUC 0.0088 against previous-word ΔAUC 0.0034 (difference 0.0054, one-sided Wilcoxon p = 0.06).
- No eye-channel control was possible, because RAM has no EOG.
- No recognition analysis was possible, because FR1 has no recognition test.

## Deviations and skips (reported next to the frozen result)

1. Six of the 20 confirmatory IDs had fewer than 3 usable sessions: R1077T (1), R1068J (2), R1311T (1), R1334T (1), R1158T (2) and R1350D (0). Following the registered rule, each was replaced by the next ID in the same shuffled order (seed 20261023).
2. Two candidate replacements were skipped for the same reason: R1309M (1) and R1308T (2).
3. The addendum listed only 5 reserves (R1067P, R1092J, R1309M, R1147P, R1195E). Two replacements, R1384J and R1441T, came from further down the same shuffled order. The rule's wording ("next ID in the same shuffled order") covers this, but the list of named reserves did not.
   - Final mapping: R1077T→R1067P, R1068J→R1092J, R1311T→R1147P, R1334T→R1195E, R1158T→R1384J, R1350D→R1441T.
4. Nine sessions were skipped by the frozen schema checks. Either the sample and onset columns disagreed, or the study-word samples fell outside the recording.
5. The first group-statistics run was killed by a 25-minute time limit set by me, the operator. It was rerun unchanged with no time limit. No code was changed.
