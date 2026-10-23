# Knowledge-Based Systems: Final Manuscript Recheck

**Editorial audit:** 23 October 2026  
**Working title:** *Knowledge-Based AI and Data-Driven Decision Support for Digital Transformation, Innovation, and Entrepreneurship in Manufacturing SMEs*  
**Final recommendation: MAJOR REVISIONS** (scientific contribution and required author attestations), with the checked formatting, numerical citations, figures, tables, and accessible Word structure corrected.

## 1. Source hierarchy and approved-paper comparison

The current *Knowledge-Based Systems* (Elsevier) Guide for Authors is authoritative for submission. Its indexed guidance identifies Short Communications as **at most 10 double-line-spaced manuscript pages including figures and tables**; this guidance is subject to confirmation in the live submission portal, because the full journal-specific publisher page returned access restrictions during this audit.

The user-supplied accepted *Knowledge-Based Systems* research manuscript, `KNOSYS_116815_Thota_SourceFile.docx`, was read as a **presentation example only**, not as a formal, reusable journal template. It uses a descriptive title, article-type line, abstract, keywords, numbered scientific sections, experimental comparison, limitations, conclusion, separate declarations, and a numbered bibliography. The revised drafts follow that **scientific organization and caption/citation conventions**, without reproducing the paper's authored contents or asserting that its exact typesetting is required. Individual author names and affiliations from that example were deliberately not transferred.

## 2. Rendered file and structural checks

| Requirement | Expanded draft | Short Communication | Decision |
|---|---|---|---|
| Page count | **17 pages** | **9 pages** | Expanded meets user's 15–20-page request; only the short file meets the cited 10-page Short Communication cap |
| Double-spaced body | Yes | Yes | Checked in Word paragraph styles and PDF render |
| Abstract | 165 words | 165 words | Within the previously retrieved 250-word journal maximum |
| Keywords | Six | Six | Within the previously retrieved 1–7-keyword guidance |
| Figure count | Two | Two | Verified in DOCX structure and rendered PDF |
| Table count | Two editable tables | Two editable tables | Verified in DOCX structure and rendered PDF |
| Journal-style headings | Numbered sections with periods; separately labeled abstract and declarations | Same | Corrected from previous version |
| Numeric citations | **27/27** cited; first appearance sequential 1–27 | **27/27** cited; first appearance sequential 1–27 | **Corrected:** previous version cited all sources but numbered them out of first-use order |
| Bibliography | 27 entries, correctly reordered | 27 entries, correctly reordered | Checked for continuous 1–27 labels |
| Accessibility audit | 0 high / medium / low findings | 0 high / medium / low findings | Added figure alternative descriptions and repeatable table-header markers |
| Visual inspection | 17 rendered pages inspected, no observed clipping | 9 rendered pages inspected, no observed clipping | Corrected a nearly empty last page and confirmed final pagination |

**The 17-page PDF is an expanded research manuscript, not a Short Communication submission file.** The nine-page PDF is the length-appropriate Short Communication candidate. Neither should be described as an accepted article or a publisher-typeset proof.

## 3. Bibliography and citation verification

The manuscript contains **24 Q1-category journal articles**, subject to the journal/metric/year caveat below, and **three necessary non-journal sources**. The requested journal publisher/platform distribution was checked directly against all bibliography entries:

| Publisher / research provenance | Number of references | Journals / role |
|---|---:|---|
| Elsevier / ScienceDirect | 10 | *Knowledge-Based Systems*, *Computers in Industry*, *Journal of Manufacturing Systems*, *International Journal of Information Management*, *International Journal of Production Economics*, *Expert Systems with Applications* |
| IEEE Xplore | 4 | *IEEE Transactions on Industrial Informatics* |
| MDPI | 10 | *Sensors* and *Sustainability* |
| Foundational method / data | 3 | Original UCI dataset, NeurIPS selective classification, ICML probability calibration |

**27 bibliography entries** are cited in the body, with in-text appearances and reference-list labels strictly sequential, `[1]` to `[27]`. The list has **25 DOI identifiers** (24 journal articles + UCI dataset) and two stable conference-paper URLs. The existing reference-audit file records all 24 journal DOIs and the previously performed DOI/indexed-metadata checks. In this recheck no citations were invented, removed, replaced with uncited sources, or left attached to obsolete numbers.

**Quartile qualification:** Scopus CiteScore Q1 is specific to an indexed journal category and year, not a guarantee that every article is Q1 in the Artificial Intelligence category or under Clarivate JCR. MDPI *Sensors* and *Sustainability* qualify for Scopus Q1 in reported categories, while their JCR quartiles can differ. The three provenance/method references are not Q1-journal papers and are **not** counted toward the 20-plus requested Q1 journal articles. Before deposit, independently confirm each journal's quartile for the institutional assessment year and metric. The manuscript's full set includes **24** journal papers with previously checked Scopus Q1-category standing.

## 4. Methods, equations, computational results, and scientific integrity

- Public source: 1,941 records, 27 predictors, seven-class UCI Steel Plates Faults dataset; stratified 1,164 training / 388 validation / 389 test cases.
- Training-derived shallow decision-tree paths are an **interpretable symbolic proxy**, not verified expert-authored SOPs, a formal knowledge graph, or independently elicited industrial rules.
- The calibration and selection-policy distinction was checked: the fixed 0.65 factor penalizes the *selection score* on rule disagreement; it does **not** recalibrate the underlying predicted probabilities or alter predicted labels.
- The policy gate in Equation (3) selects the observed lower-validation-risk **policy**, with confidence-only winning ties. The held-out test labels do not choose the policy.
- Table 1 matches `results/results.json`: calibrated gradient boosting accuracy **77.89%**, macro-F1 **77.76%**, Brier score **0.3213**.
- Table 2 matches the JSON: at matched 80% coverage (**311 accepted cases**), confidence-only selective error **14.79%**, knowledge-guided selective error **16.72%**; difference **+1.93 percentage points**, paired-bootstrap 95% interval **−0.64 to +4.18 points** (2,000 resamples).
- The interval includes zero. **There is no justified claim that the hybrid policy outperforms confidence-only selection or that it is conclusively inferior in all settings.** The validation comparison selected confidence-only here.
- The two programmatically generated figures and two table captions correspond to the same policies and statistics; separate validation-fixed operational thresholds are explicitly distinguished from retrospective, coverage-matched test ranking curves.
- A previous independent 2,000-bootstrap rerun reproduced all 16 stored result keys and both figure checksums; this present editing pass changed only manuscript-generation and accessibility/citation formatting. It did **not** retrain models or alter `research.py`, input data, or measured outputs.

## 5. Scientific and editorial changes completed in this recheck

1. Corrected all numbered citations to **first order of appearance** and reordered the complete bibliography in both manuscripts; validated every reference from 1 through 27.
2. Aligned main numbered heading punctuation, abstract heading, and separate competing-interest, funding, and CRediT sections with the accepted-paper presentation pattern.
3. Removed repetitive prose to restore a professionally balanced **17-page expanded** and **nine-page Short Communication** layout, with no scientific conclusion changed.
4. Added useful alt descriptions to both figures and designated both Word table header rows for accessible reading and page repeats.
5. Re-rendered both files and performed another page-by-page layout and machine-readable figure/table/accessibility audit.

## 6. Final submission-readiness checklist

| Item | Final status | Follow-up required |
|---|---|---|
| Scope of KBS: technical knowledge-based intelligent decision support | **Partial** | Knowledge layer remains data-induced; novelty beyond confidence-ranking validation is limited |
| Scientific contribution and research gap | **Partial** | Test a genuine independent expert-authored rule base and external/repeated industrial cohorts |
| Honest conclusions and business interpretation | **Pass** | Preserve the negative/uncertain experimental result and describe SME, innovation and entrepreneurship outcomes as **hypotheses** |
| Publisher manuscript organization and numbered references | **Pass for checked elements** | Live Guide for Authors and portal instructions remain ultimate authority |
| 2 figures, 2 editable tables, equations, numerical traceability | **Pass** | Supply separate high-resolution figure uploads if portal requests them |
| Short Communication length | **Pass for nine-page file only** | The 17-page expanded manuscript requires a different eligible article type |
| Bibliographic first-use ordering and DOI metadata | **Pass for checked items** | Final DOI/publisher proof and year-specific Scopus/JCR quartile verification before submission |
| Author byline, affiliation, ORCID, corresponding-author details | **Incomplete** | Authors must provide real data |
| Competing interests, actual funding, individual CRediT contributions | **Incomplete** | Named authors must review and approve all three; current text is intentionally a placeholder |
| Generative-AI declaration | **Included; confirmation required** | Check publisher policy wording and obtain author acceptance |
| Graphical abstract, highlights, supplementary upload rules | **Not conclusively verified** | Confirm in the live KBS submission system; do not infer from another Elsevier journal |
| Cursor/GitHub manuscript synchronization | **Not independently verified** | The revised local manuscript and PDF are provided; no live Cursor synchronization or GitHub manuscript commit is claimed |

### Editorial verdict

**MAJOR REVISIONS.** These versions pass the mechanical checks explicitly reported above, but scientific novelty, real domain knowledge, external validation, and verified author/portal requirements remain significant blockers. A high-quality, truthful negative experiment is defensible; it must not be reframed as proven operational improvement, SME transformation, or entrepreneurship impact to fit an ambitious title.

**Official links for author confirmation:** [KBS Guide for Authors](https://www.sciencedirect.com/journal/knowledge-based-systems/publish/guide-for-authors); [Elsevier reference preparation](https://www.elsevier.support/publishing/answer/how-should-i-prepare-the-references-in-my-manuscript); [Elsevier highlights](https://www.elsevier.com/researcher/author/tools-and-resources/highlights); [Elsevier graphical abstracts](https://www.elsevier.com/researcher/author/tools-and-resources/graphical-abstract).
