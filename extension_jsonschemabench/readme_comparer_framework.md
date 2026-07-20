# Comparaison des frameworks sur Github_medium

Ce fichier compare les resultats `Github_medium` pour trois frameworks:
`xgr` (XGrammar), `outlines` et `guidance` (LLGuidance).

Les resultats utilises sont dans:

- `extension_jsonschemabench/results/per_dataset_runs/xgr/Github_medium`
- `extension_jsonschemabench/results/per_dataset_runs/outlines/Github_medium`
- `extension_jsonschemabench/results/per_dataset_runs/guidance/Github_medium`

Pour `guidance`, le fichier `per_test_results.jsonl` a ete deduplique apres les
reprises du run. Le fichier brut avec doublons a ete conserve sous
`per_test_results.raw_with_resume_duplicates_20260720.jsonl`.

## Definitions

- `timeout`: un schema a depasse le timeout superviseur par schema.
- `compile_error`: le framework n'a pas pu compiler le schema en grammaire.
- `under`: test invalide accepte par le framework.
- `over`: test valide rejete par le framework.
- `passed`: le framework a eu le bon comportement sur le test.
- Les statistiques `under`, `over`, `passed` et `compile_error` sont comptees au
  niveau test.
- Les colonnes `schemas` comptent le nombre de schemas concernes.

Corpus `Github_medium`:

- Schemas avec tests: `1823`
- Tests attendus: `9210`

## Resume principal

| Framework | Tests couverts | Schemas couverts | Timeout schemas | Timeout tests estimes | Compile-error schemas | Compile-error tests | Under tests | Over tests | Passed tests |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| XGrammar (`xgr`) | 8390 | 1716 | 107 | 820 | 10 | 76 | 985 | 623 | 6706 |
| Outlines (`outlines`) | 8542 | 1736 | 88 | 668 | 292 | 1341 | 653 | 472 | 6076 |
| LLGuidance (`guidance`) | 9210 | 1823 | 0 | 0 | 369 | 1617 | 0 | 1607 | 5986 |

## Taux sur les tests executes

Ces taux excluent les tests en `compile_error` et les tests non decides par
timeout.

| Framework | Correct accept | Correct reject | Under rate | Over rate | Accuracy executee |
|---|---:|---:|---:|---:|---:|
| XGrammar (`xgr`) | 2268 | 4438 | 18.16% | 21.55% | 80.66% |
| Outlines (`outlines`) | 1960 | 4116 | 13.69% | 19.41% | 84.38% |
| LLGuidance (`guidance`) | 823 | 5163 | 0.00% | 66.13% | 78.84% |

## Lecture rapide

- `guidance` couvre tous les tests (`9210/9210`) et n'a aucun timeout avec le
  timeout de 10 minutes par schema.
- `guidance` a plus de `compile_error` que `xgr` et `outlines`: `1617` tests
  affectes, sur `369` schemas. Ces erreurs viennent surtout de mots-cles JSON
  Schema ou formats non supportes par LLGuidance, par exemple
  `patternProperties`, `dependencies`, `minProperties`, `maxProperties`, `not`,
  `oneOf`, `format: uri`, `format: path`.
- `guidance` n'a pas d'`under` dans ce run: il n'accepte pas de tests invalides.
- En revanche, `guidance` a beaucoup d'`over`: `1607` tests valides rejetes, ce
  qui donne un taux d'over de `66.13%` parmi les tests valides executes.
- `outlines` a moins d'`under` et moins d'`over` que `xgr` sur les tests
  executes, mais il a beaucoup plus de `compile_error`.
- `xgr` a peu de `compile_error`, mais davantage de timeouts que les deux
  autres sur ce run.

## Details par framework

### XGrammar (`xgr`)

- Tests uniques couverts: `8390`
- Schemas couverts: `1716 / 1823`
- Schemas timeout: `107`
- Tests estimes timeout: `820`
- Schemas en compile error: `10`
- Tests en compile error: `76`
- Under: `985`
- Over: `623`
- Passed: `6706`

### Outlines (`outlines`)

- Tests uniques couverts: `8542`
- Schemas couverts: `1736 / 1823`
- Schemas timeout: `88`
- Tests estimes timeout: `668`
- Schemas en compile error: `292`
- Tests en compile error: `1341`
- Under: `653`
- Over: `472`
- Passed: `6076`

### LLGuidance (`guidance`)

- Tests uniques couverts: `9210`
- Schemas couverts: `1823 / 1823`
- Schemas timeout: `0`
- Tests estimes timeout: `0`
- Schemas en compile error: `369`
- Tests en compile error: `1617`
- Under: `0`
- Over: `1607`
- Passed: `5986`
