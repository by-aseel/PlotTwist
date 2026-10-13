# C3 tool definitions and output contract

These are local Python functions exposed to the model through function-calling schemas. Their documentation follows the class's MCP-style fields: name, description, input parameters, expected output, and side effect. A running MCP server is not required by this implementation.

## record_customer_interest

- **Signature:** `record_customer_interest(email, name, message)`.
- **Description:** Save an enquiry after the customer supplies their own contact details and event notes.
- **Input schema:** an object containing exactly three required string properties: `email` (customer email), `name` (customer name), and `message` (experience preferences and notes). Additional properties are rejected. Email syntax and nonempty field lengths are validated.
- **Side effect:** save a session-scoped `lead` event in the local SQLite database. Duplicate identical records reuse the existing reference.
- **Expected output:** the success or error object below. Success uses `kind: "lead"`.

## record_feedback

- **Signature:** `record_feedback(question)`.
- **Description:** Save customer feedback or a question the supplied business sources cannot answer.
- **Input schema:** an object containing exactly one required string property, `question`. It must be nonempty and at most 4,000 characters. Additional properties are rejected.
- **Side effect:** save a session-scoped `feedback` event in the same local database. No contact details are required.
- **Expected output:** the success or error object below. Success uses `kind: "feedback"`.

## Success and error outputs

Both functions return a Python dictionary, serialized to JSON when passed back to the model.

| Outcome | Required fields and types |
|---|---|
| Success | `ok: true`, `id: integer`, `kind: "lead"` or `"feedback"`, `status: "saved"` or `"already_recorded"` |
| Error | `ok: false`, `kind: "validation_error"` or `"storage_error"`, `error: string` |

Successful enquiry example:

```json
{"ok": true, "id": 1, "kind": "lead", "status": "saved"}
```

Successful feedback example:

```json
{"ok": true, "id": 2, "kind": "feedback", "status": "saved"}
```

Validation error example:

```json
{"ok": false, "kind": "validation_error", "error": "question must be a non-empty string."}
```

## Logging and demonstration

Every successful save prints metadata such as `[tool log] feedback: record #2 (saved)` to the terminal or notebook output. Names, email addresses, and message contents are kept out of that console line. The full record is persisted locally and can be inspected in the session's casebook.

The notebook's **Exercise all three routes and short-term memory** cell invokes both tools. **Inspect tools and reflection** prints each tool's name, arguments, actual result, and whether the invocation originated from the live model or the offline demonstration.

For an unanswered question, try `Are your City Quests wheelchair accessible?`. The router selects `feedback_unanswered`; the agent records the question and explains that the sources cannot confirm the answer. In live mode, the model returns the function call, the application executes it, and its JSON observation is returned to the model. In demo mode, the local policy chooses the same function deterministically.

The machine-readable input schemas are `TOOL_SCHEMAS` in `prompts.py`. Function implementations and save/print logic are in `plottwist_agent.py`. The notebook includes the complete readable source for both files. No tool sends an email or confirms a booking.
