---
name: user-story-modeling-workflow
description: Use this skill whenever the user wants an end-to-end workflow that combines Epic user stories, fine-grained user stories, TQA refinement, domain modeling, and model validation. It guides the user to maintain a story-set file containing both Epic stories and detailed stories, use Epics as the modeling/learning input, and use fine-grained stories plus Given/When/Then acceptance criteria as the validation/test input. Especially use for user story modeling workflows, Epic modeling with fine-grained story validation, LLM-assisted user stories and domain modeling, or organizing requirements files for this process.
---

# User Story Modeling Workflow

Use this skill to orchestrate the full workflow:

```text
Business context / user journey
  ↓
Epic Stories
  ↓
TQA refinement of user stories and acceptance criteria
  ↓
Story-set file: Epics + fine-grained stories
  ↓
Model using only Epics
  ↓
Validate the model with fine-grained stories
  ↓
Revise the model, stories, or business context
```

The key rule is to separate **modeling input** from **validation input**:

- **Epic stories** = learning/modeling set.
- **Fine-grained stories + Given/When/Then** = testing/validation set.
- It is okay to keep both in one file, but do not mix them during the modeling step.

## Related skills

This workflow coordinates:

1. `user-story-tqa-refinement` — refine/split stories and write acceptance criteria.
2. `tqa-acceptance-criteria-writer` — produce Given/When/Then scenarios after TQA clarification.
3. `modeling` — extract a concept dictionary and first-pass Fulfillment Model from Epics.
4. `story-model-validation` — validate the model with detailed stories.

## Recommended workflow

### Step 1: Create or update a story-set file

Create one Markdown file per coherent business capability, product slice, or bounded-context candidate.

Suggested names:

```text
[business-capability]-user-story-set.md
[business-capability]-story-set.md
```

### Step 2: Capture business background

Record:

- overall solution / system boundary;
- actors and roles;
- user journey;
- known policies and constraints;
- open questions.

### Step 3: Record Epic stories

Epic stories express broad business value and will be used as modeling input.

For each Epic, record:

- ID, title, status;
- story text;
- business value;
- related user journey steps;
- child stories, if known.

### Step 4: Refine detailed stories with TQA

If detailed stories are missing or weak:

1. Provide business background, user journey, and Epic/current story.
2. Let LLM ask clarifying questions first.
3. Let the domain expert answer.
4. Generate fine-grained user stories and Given/When/Then acceptance criteria.

Mark generated stories as `draft` until reviewed by humans.

### Step 5: Build the initial domain model from Epics only

When modeling, explicitly instruct:

> Use only the Epic Stories section as modeling input. Do not use detailed stories or acceptance criteria during initial model extraction.

Expected artifacts:

- concept dictionary;
- entities / roles / value objects;
- relationships;
- states and lifecycle;
- business rules;
- events;
- assumptions and gaps.

### Step 6: Validate the model with detailed stories

For each fine-grained story/scenario, check:

- Can the model express the Given state?
- Can the model explain the When action/event?
- Can the model produce the Then outcome?
- Are all actors, concepts, rules, states, permissions, and events present?

### Step 7: Feed findings back

Validation can lead to:

1. **Update the model** — missing concept, state, rule, relationship, event.
2. **Update the story** — unclear actor, incorrect operation, mixed scope, missing acceptance criteria.
3. **Update the business background** — misunderstood process, hidden policy, newly discovered knowledge.

## Story-set file template

```markdown
# [Business Capability] - User Story Set

## 1. Business Background

### Overall Solution
- ...

### System Boundary
- Inside the system: ...
- Outside the system: ...

### Roles
| Role | Description |
|---|---|

## 2. User Journey

1. ...
2. ...
3. ...

## 3. Epic Stories (Modeling Input / Learning Set)

### EPIC-001 [Title]

Status: draft / reviewed / confirmed  
Related journey steps: ...

As a ...  
I want ...  
So that ...

#### Business Value
- ...

#### Known Constraints
- ...

#### Child Stories
- US-001 ...
- US-002 ...

## 4. Fine-grained User Stories (Validation Input / Test Set)

### US-001 [Title]

Parent Epic: EPIC-001  
Status: draft / reviewed / confirmed

As a ...  
I want ...  
So that ...

#### Acceptance Criteria

Scenario 1: [Scenario name]
- Given ...
- When ...
- Then ...

Scenario 2: [Scenario name]
- Given ...
- When ...
- Then ...

#### Notes
- ...

## 5. Open Clarification Questions

| ID | Question | Source | Status | Answer/Decision |
|---|---|---|---|---|
| Q-001 | ... | EPIC-001 / US-001 / model validation | open | ... |

## 6. Domain Model Snapshot

> Link to a separate model file, or record a summary here.

### Concept Dictionary Summary
| Concept | Definition | Source |
|---|---|---|

### Mermaid Model
```mermaid
classDiagram
```

## 7. Model Validation Log

| Date | Model Version | Validation Stories | Conclusion | Major Gaps |
|---|---|---|---|---|

## 8. Change Log

| Date | Change | Reason |
|---|---|---|
```

## Suggested prompts

### Create story-set file

```text
Please create a user story set file for [business capability]. Include business background, user journey, Epic Stories, fine-grained User Stories, acceptance criteria, open clarification questions, and model validation records. Use Epics as modeling input and fine-grained stories as validation input.
```

### Refine stories

```text
Based on this Epic, business background, and user journey, please use the TQA method to ask clarification questions first. After I answer, generate fine-grained user stories and Given/When/Then acceptance criteria.
```

### Build model

```text
Please extract a domain model using only the “Epic Stories (Modeling Input)” section. Do not use fine-grained stories. Output a concept dictionary, relationships, rules, states, events, and assumptions to validate.
```

### Validate model

```text
Please validate this domain model using the “Fine-grained User Stories (Validation Input)” section and acceptance criteria. Identify missing concepts, relationships, states, rules, and events, and provide correction suggestions.
```

## Output behavior

First identify where the user is:

1. No story-set file → propose/create template.
2. Epics exist but details missing → use TQA refinement.
3. Epics and details exist but no model → run Epic-only modeling.
4. Model exists → run detailed-story validation.
5. Validation findings exist → revise model, stories, or business background.

Always preserve the separation between learning set and test set.
