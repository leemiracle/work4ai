# Explainability

| Field | Response |
| --- | --- |
| Intended Task/Domain: | Video quality screening using task-specific good/bad labels. |
| Model Type: | Frozen video transformer, learned attention pooling and binary linear classifier. |
| Intended Users: | Developers and researchers evaluating or filtering video datasets. |
| Output: | Bad-class logit and sigmoid scores and the thresholded good-or-bad decision. |
| Describe how the model works: | Frozen V-JEPA 2.1 encodes video into space-time tokens. A learned query pools normalized tokens into one vector; a linear classifier produces a bad logit. A calibrated threshold determines the decision. |
| List the groups (or group characteristics) for which this was tested to produce comparable outcomes: | Not Applicable |
| Technical Limitations & Mitigation: | Performance can change with scenes, generators, cameras, duration and labels. Sparse sampling can miss brief defects. Evaluate representative held-out videos, separate related scenes, and recalibrate on target data. Attention weights are not validated explanations or localization masks. |
| Verified to have met prescribed NVIDIA quality standards: | Yes |
| Performance Metrics: | Bad-class ROC AUC, bad recall and good-video rejection. |
| Potential Known Risks: | Missed defects, rejection of useful videos and misleading confidence under distribution shift. Scores do not certify physical correctness. Class balancing does not establish demographic fairness or comparable outcomes across groups. |
| Licensing: | [OpenMDW-1.1](https://openmdw.ai/license/1-1/) |
