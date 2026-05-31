---
name: story-model-validation
description: Use this skill whenever the user wants to validate a domain model, concept dictionary, Mermaid class diagram, DDD model, or business model against fine-grained user stories, acceptance criteria, Given/When/Then scenarios, or test stories. It checks whether the model supports each story, finds missing concepts/relations/states/rules/events/permissions, and proposes model or story corrections. Especially use for validating a model with fine-grained user stories, model checking, model expansion, or traceability from stories to model elements.
---

# Story Model Validation

Validate a domain model with fine-grained user stories and acceptance criteria. Treat detailed stories as the **test/validation set** for a model extracted from Epics.

## Core idea

```text
Domain model + fine-grained user stories/acceptance criteria -> coverage check -> gaps -> correction suggestions
```

A model is useful if it can explain and support detailed stories.

## Inputs

1. **Domain model**
   - concept dictionary;
   - entity/relationship list;
   - Mermaid class diagram;
   - DDD aggregate/value object/event model;
   - business rules, states, or workflows.

2. **Validation stories**
   - fine-grained user stories;
   - Given/When/Then acceptance criteria;
   - examples, edge cases, policy scenarios.

If either input is missing, ask for it or state assumptions.

## Validation workflow

### 1. Normalize each story/scenario

Identify:

- Actor
- Goal
- Given state/precondition
- When action/event
- Then outcome
- Business objects
- Rules and constraints
- State transitions
- Permissions

### 2. Map story elements to model elements

Create traceability:

- actor -> role/entity
- business object -> entity/value object/concept
- precondition -> state/rule/relationship
- action/event -> domain behavior/event
- outcome -> state change/record/rule result
- permission -> actor responsibility/policy

### 3. Classify coverage

Use these statuses:

- `covered` — model clearly supports the story element.
- `partial` — related concepts exist but details are insufficient.
- `missing` — no model element supports it.
- `ambiguous` — story or model wording is unclear.
- `out-of-scope` — belongs to another bounded context or story.

### 4. Classify gap type

- Missing concept/entity
- Missing relationship
- Missing state/status
- Missing rule/policy
- Missing event/behavior
- Missing actor/permission
- Story ambiguity
- Scope boundary issue

### 5. Recommend corrections

Decide whether to:

- update the domain model;
- update the concept dictionary;
- refine/split the user story;
- ask a clarification question;
- mark it out of scope.

Do not expand the model for every UI detail or transport-level API detail. Add only business-relevant concepts, rules, states, events, or relationships.

## Output format

```markdown
# Model Validation Result

## 1. Validation Summary
- Model under validation: ...
- Number of validation stories: ...
- Overall conclusion: passed / partially passed / failed

## 2. Coverage Matrix
| Story/Scenario | Given Coverage | When Coverage | Then Coverage | Conclusion | Notes |
|---|---|---|---|---|---|

## 3. Detailed Traceability
### Story 1: ...
| Story Element | Type | Corresponding Model Element | Coverage Status | Notes |
|---|---|---|---|---|

## 4. Discovered Gaps
| Gap | Type | Affected Stories | Severity | Recommendation |
|---|---|---|---|---|

## 5. Suggested Model Corrections
### New/Updated Concepts
- ...

### New/Updated Relationships
- ...

### New/Updated Rules, States, or Events
- ...

### Mermaid Correction Snippet (Optional)
```mermaid
classDiagram
```

## 6. User Stories That Should Be Revised
- ...

## 7. Open Clarification Questions
- ...
```

## Severity guidance

- **High**: Without this concept/rule/state, the story cannot be implemented or reasoned about.
- **Medium**: Model roughly supports the story, but important behavior is underspecified.
- **Low**: Naming, wording, optional detail, or UI/channel issue.

## Heuristics

- A `Given` condition usually maps to state, relationship, existing record, or rule.
- A `When` action usually maps to command, behavior, or event.
- A `Then` result usually maps to state transition, created record, notification/event, or rule decision.
- Deadlines, capacity, eligibility, approval, identity, permission, cancellation, and duplicate submission usually imply business rules.
- Failed, pending, expired, cancelled, completed, or manual-review scenarios usually imply states.
- If two stories imply contradictory rules, flag a business conflict rather than choosing one.

## Handoff

If validation exposes many unclear stories, recommend `user-story-tqa-refinement` before revising the model further.
