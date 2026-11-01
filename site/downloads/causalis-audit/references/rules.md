# Deterministic audit rules

| ID | Pass condition |
| --- | --- |
| ID-001 | `agent.name` is a non-empty string. |
| ID-002 | `agent.version` is a non-empty string. |
| AUTH-001 | `authority.owner` is a non-empty string. |
| AUTH-002 | `authority.allowedPrograms` is a non-empty array. |
| LIMIT-001 | `limits.perTransaction` is a finite number greater than or equal to zero. |
| LIMIT-002 | `limits.perDay` is a finite number greater than or equal to `limits.perTransaction`. |
| LIMIT-003 | `limits.denomination` is a non-empty string. |
| HUMAN-001 | `controls.humanApprovalAbove` is a finite number greater than or equal to zero. |
| HUMAN-002 | `controls.humanApprovalAbove` is less than or equal to `limits.perTransaction`. |
| STOP-001 | `controls.emergencyStop` is strictly `true`. |
| LOG-001 | `audit.logActions` is strictly `true`. |
| LOG-002 | `audit.retentionDays` is an integer greater than zero. |

Missing fields receive `not_provided`, not `fail`. Invalid supplied values receive `fail`. Never collapse results into a safety score.
