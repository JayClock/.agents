---
name: tqa-acceptance-criteria-writer
description: Write and refine Given/When/Then acceptance criteria for user stories using a TQA Think-Question-Answer clarification loop. Use this skill whenever the user asks for acceptance criteria, Specification by Example, scenarios, BDD examples, story clarification, or wants Claude to ask domain questions before writing requirements. Prefer this skill when the user has a user story but the business context, user journey, or solution rules are incomplete.
---

# TQA Acceptance Criteria Writer

Use this skill to help write acceptance criteria for user stories by first clarifying the tacit business knowledge behind the story. The key idea: user stories are placeholders for conversation, so good acceptance criteria require understanding the overall solution, user journey, and business rules.

TQA means **Think → Question → Answer**. Claude should think about what is still uncertain, ask the user one focused question at a time, incorporate the answer, then continue until there is enough context to produce scenarios.

## Inputs to look for

1. **User story** — `As a / I want / So that` or equivalent prose.
2. **Business context** — product goal, overall solution, known workflow, roles, rules.
3. **Existing acceptance criteria** — if any.
4. **Desired scope** — UI, API, backend process, business-only, or unspecified.

If the user provides only a terse story, use TQA instead of immediately producing many speculative scenarios.

## Principle

A useful user story separates:

- **Role + value**: the problem being solved; relatively stable.
- **Function**: one negotiable solution to the problem.

Acceptance criteria should confirm that this story contributes to the role/value and fits the overall solution. Avoid merely restating the function as the value.

## Workflow

### 1. Restate the story and context

Briefly summarize:

- Actor/role
- Desired capability
- Stated value
- Known business background
- Apparent scope boundary

If the value sounds like a feature restatement, flag it gently.

### 2. Decide whether to ask questions

Ask questions when any of these are unclear:

- Where this story sits in the user journey
- What must already be true before the story starts
- What business rules govern success/failure
- Who actually receives the value
- What edge cases matter
- Whether a scenario belongs to this story or another story

If the user asks for a quick draft, produce assumptions and mark them clearly.

### 3. Run the TQA loop

Ask **one question at a time** unless the user explicitly asks for a batch.

Use this internal pattern:

```text
Thought: What is still uncertain about the user story? Ignore implementation details unless scope requires them.
Question: Ask the most useful clarifying question.
Answer: Incorporate the user's answer into the working context.
```

In the conversation, do not expose long hidden reasoning. Just ask concise questions with a short reason if helpful.

Good question types:

- **Concept questions**: “Is student enrollment registered once per year, or only once for the entire degree program?”
- **Journey questions**: “Is the user guided to registration after logging in, or do they actively navigate to the registration page?”
- **Rule questions**: “If the registration deadline has passed, should the system reject registration or allow a late-registration approval process?”
- **Boundary questions**: “Does sending reminders belong to this story card, or should it be a separate story?”
- **Value questions**: “Does this action mainly benefit the student, or does it help academic staff track progress?”

### 4. Stop asking and write scenarios

Stop when:

- The happy path is clear.
- Important failure/edge cases are known.
- Scope boundaries are clear enough.
- Further questions would only add UI copy or low-level implementation detail.

Usually 3–7 good questions are enough. Do not interrogate the user indefinitely.

### 5. Generate Given/When/Then scenarios

Each scenario should be concrete and testable:

- **Given**: preconditions and relevant business state
- **When**: one user action or business event
- **Then**: observable business outcome
- Optional **And** lines only when they clarify state or side effects

Use business language. Include examples where helpful.

## Default output format

```markdown
# User Story Acceptance Criteria

## User Story
As a ...
I want ...
So that ...

## Confirmed Business Context
- ...

## Scope Boundaries
Included:
- ...
Excluded:
- ...

## Acceptance Scenarios

### Scenario 1: Happy Path
Given ...
When ...
Then ...

### Scenario 2: ...
Given ...
When ...
Then ...

## Questions for Follow-up Confirmation
- ...
```

If the user is still answering questions, output only the next question, not the final scenarios.

## Quality checklist

Before finalizing, check:

- Does every scenario trace back to the story's role/value?
- Are there both success and meaningful failure cases?
- Are system states concrete enough to test?
- Are UI details avoided unless the story is explicitly about UI?
- Are separate user stories kept separate?
- Is the value statement meaningful rather than “so I can use the feature”?

## Common mistakes to avoid

- Do not produce acceptance criteria without enough business context unless you label assumptions.
- Do not ask the LLM's own questions and answer them yourself; the point of TQA is to collect human/domain feedback.
- Do not include every possible workflow step in one story. If a scenario belongs to another story, put it under “Scope boundaries / possible split”.
- Do not overfocus on technology. Acceptance criteria should usually confirm business behavior, not framework or database details.

## When asked to improve an existing story

Return:

1. Diagnosis of role/function/value
2. Revised story options if needed
3. Questions needed before acceptance criteria
4. Draft acceptance criteria if enough context is available

Keep the tone collaborative; the goal is to improve the conversation around the story, not to declare it wrong.
