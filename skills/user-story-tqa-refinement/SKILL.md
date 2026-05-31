---
name: user-story-tqa-refinement
description: Use this skill whenever the user wants to refine, split, complete, or write user stories with LLM help, especially using TQA / Think-Question-Answer, frontend stories, API stories, Given-When-Then acceptance criteria, user journeys, overall solution context, or requests such as “ask questions first.” It turns coarse stories or Epics into clearer fine-grained user stories and acceptance criteria by asking targeted business questions before filling in details, and by adapting the TQA question focus for frontend, API, or domain scenarios.
---

# User Story TQA Refinement

Use standard TQA — **Thought → Question → Answer** — to refine user stories. The model asks; the domain expert answers. Do not add extra interaction steps. Summarize feedback and decisions only in the final output.

## Core idea

A user story is a **placeholder for business value**. Its concrete scope is determined through conversation and acceptance criteria.

Useful refinement requires:

1. **Business context / overall solution** — what system or solution exists?
2. **User journey** — where does this story happen in the end-to-end flow?
3. **Current user story** — what value does this card represent?

If key context is missing, ask questions before writing final stories or acceptance criteria.

## Choose scenario type

Classify the story before asking questions:

| Type | Use when | Clarification focus |
|---|---|---|
| `frontend` | a human user interacts with screens, forms, notifications, or dashboards | journey step, visible behavior, inputs, validation, success/error/empty states, permissions |
| `api` | a system, frontend, partner, or service calls an API or integration | consumer, command/query, request/response, authorization, validation, errors, idempotency, side effects |
| `domain` | the story describes a business operation, policy, workflow, or lifecycle | concepts, rules, states, events, actors, responsibilities, boundaries |
| `mixed` | UI, API, and domain concerns are mixed | ask scope questions and split into smaller stories |

If unclear, ask: “Does this story mainly describe a frontend user action, an API/system interaction, or a business process? Should it be split?”

## Workflow

1. **Understand the story**
   - Role / actor
   - Goal / capability
   - Value / reason
   - Scenario type
   - Journey position
   - Scope boundaries

2. **Ask focused TQA questions**
   - Ask 5–10 high-value questions when needed.
   - Prefer one specific question at a time in an agent loop.
   - Avoid generic questions such as “Any other requirements?”

3. **Interpret answers**
   - Does the answer update business context?
   - Does it require rewriting the user story?
   - Does it add acceptance criteria?
   - Does it imply a new story?
   - Does it reveal a domain concept, state, rule, event, or permission?
   - For API stories, does it change request, response, errors, authorization, idempotency, or side effects?

4. **Split stories when needed**
   Split when different actors, values, channels, policies, lifecycle states, or independent capabilities are mixed.

5. **Write Given/When/Then acceptance criteria**
   - `Given` = precondition / system state
   - `When` = actor action or business event
   - `Then` = expected business outcome

## Question focus by type

### Frontend stories

Ask about:

- entry point in the user journey;
- what the user sees before acting;
- required inputs and validation;
- success feedback and next step;
- empty, error, expired, and forbidden states;
- whether notifications, redirects, reminders, or admin actions are separate stories;
- what is business behavior vs. presentation detail.

Avoid framework, component library, CSS, database, and deployment details.

### API stories

Ask about:

- API consumer / caller;
- command vs. query;
- required business parameters;
- response data needed by the consumer;
- authorization and permission rules;
- validation rules and error cases;
- duplicate requests, retries, and idempotency;
- state transitions, side effects, events, and audit records.

Avoid framework, database schema, infrastructure, and low-level protocol details unless they are part of the requirement.

### Domain stories

Ask about:

- concept definitions;
- lifecycle states;
- eligibility, deadline, capacity, approval, cancellation, and exception rules;
- actor responsibilities;
- business events and downstream consequences;
- bounded-context or scope boundaries.

## TQA Agent format

Use this interaction format:

```text
Thought: Think about what is still unclear about the story. Focus on business uncertainty and scenario-type concerns.
Question: Ask one specific question to clarify the story.
Answer: The domain expert's answer.
```

Repeat 3–10 times as needed. If implementing with an LLM API, use `Answer:` as the stop sequence so the model waits for the human answer instead of self-answering.

## Prompt template: frontend story

```text
You are a business analyst familiar with Specification by Example and UX-oriented user story refinement. I am the domain expert.

===CONTEXT
{context}
===END OF CONTEXT

===USER JOURNEY
{journey}
===END OF USER JOURNEY

===USER STORY
{story}
===END OF USER STORY

This is a frontend / user-facing story.
Clarify the story by asking questions first. Focus on user goal, journey step, visible behavior, required input, validation, permission, success feedback, empty state, error state, and whether some behavior should be split into another story.
Do not focus on framework, component library, CSS, database, or deployment.

Use this format:
Thought: what is still uncertain in the frontend scenario?
Question: one question to clarify the story
Answer: the domain expert's answer

Repeat Thought/Question/Answer at least 3 times and at most 10 times.
When you know enough, output refined stories and Given/When/Then scenarios.

{history}
{input}
```

## Prompt template: API story

```text
You are a business analyst familiar with Specification by Example and API contract design. I am the domain expert.

===CONTEXT
{context}
===END OF CONTEXT

===API / SYSTEM CONTEXT
{api_context}
===END OF API / SYSTEM CONTEXT

===USER STORY
{story}
===END OF USER STORY

This is an API / system-facing story.
Clarify the business behavior behind the API. Focus on API consumer, command/query type, request, response, authorization, validation, state transition, side effects, idempotency, error cases, events, and audit requirements.
Do not focus on framework, database schema, deployment, or low-level implementation details.

Use this format:
Thought: what is still uncertain in the API scenario?
Question: one question to clarify the API behavior
Answer: the domain expert's answer

Repeat Thought/Question/Answer at least 3 times and at most 10 times.
When you know enough, output refined stories, Given/When/Then scenarios, and API contract notes.

{history}
{input}
```

## Output format

### If context is insufficient

```markdown
# Clarification Questions

## My Understanding of the Current Story
- Type: frontend / api / domain / mixed
- Role: ...
- Goal: ...
- Value: ...
- Position in user journey: ...

## Questions
### A. Business Context
1. ...
### B. Story Scope
1. ...
### C. Acceptance Criteria
1. ...
### D. Exceptions and Boundaries
1. ...
### E. Type-Specific Questions (Frontend/API/Domain)
1. ...

## After You Answer, I Will Produce
- Fine-grained user stories
- Given/When/Then acceptance criteria
- Suggested updates to the business context / user stories / API contract / domain model
```

### If enough context exists

```markdown
# User Story Refinement Result

## 1. Business Context Summary
- Overall solution: ...
- User journey position: ...
- Story type: frontend / api / domain / mixed

## 2. Original Story
> As a ... I want ... so that ...

## 3. Question-and-Answer Feedback Summary
| Information Source | Where to Update | Business Knowledge Discovered | Impact on Acceptance Criteria |
|---|---|---|---|

## 4. Refined User Stories
### Story 1: ...
As a ...  
I want ...  
So that ...

#### Acceptance Criteria
Scenario 1: ...
- Given ...
- When ...
- Then ...

#### API Contract Notes (API stories only)
- Consumer: ...
- Command/Query: ...
- Request: ...
- Response: ...
- Errors: ...
- Authorization: ...
- Idempotency: ...
- Side effects/events: ...

## 5. Candidate Stories Outside the Current Scope
- ...

## 6. Impact on Business Context / Domain Model
- New concepts: ...
- New rules: ...
- New states: ...
- New events: ...

## 7. Questions Still to Confirm
- ...
```

## Handoff

After generating fine-grained stories and acceptance criteria, recommend using `story-model-validation` to check whether the existing domain model supports them.
