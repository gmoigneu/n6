## ADDED Requirements

### Requirement: `n6 m fact` stores a short fact
The system SHALL provide a command `n6 m fact <text>` that stores the given text as a memory of type `fact`. The text SHALL be passed as a positional CLI argument.

#### Scenario: Storing a fact prints confirmation
- **WHEN** the user runs `n6 m fact "I prefer Python over JavaScript"`
- **THEN** the memory is stored in Qdrant and a confirmation message is printed to stderr

#### Scenario: Missing text argument shows usage error
- **WHEN** the user runs `n6 m fact` with no argument
- **THEN** Typer prints a usage error and exits with a non-zero code

### Requirement: `n6 m note` stores a free-form note
The system SHALL provide a command `n6 m note <text>` that stores the given text as a memory of type `note`. The text SHALL be passed as a positional CLI argument.

#### Scenario: Storing a note prints confirmation
- **WHEN** the user runs `n6 m note "Read about Qdrant HNSW indexing"`
- **THEN** the memory is stored and a confirmation message is printed to stderr

### Requirement: `n6 m meeting` stores a meeting transcript
The system SHALL provide a command `n6 m meeting` that reads a meeting transcript from **stdin**, passes it to mem0 as a user-role message, and stores the extracted memories with type `meeting`. The command SHALL NOT accept the transcript as a CLI argument (transcripts can be very large).

#### Scenario: Storing a meeting transcript via stdin
- **WHEN** the user pipes a transcript: `cat meeting.txt | n6 m meeting`
- **THEN** mem0 extracts memories from the transcript, stores them, and prints a confirmation with the count of memories stored

#### Scenario: No stdin input exits with an error
- **WHEN** `n6 m meeting` is run interactively with no piped input
- **THEN** the command prints an error message to stderr and exits with a non-zero code

### Requirement: `n6 s` searches stored memories
The system SHALL provide a command `n6 s <query>` that performs a semantic search across all stored memories for the configured `user_id`. Results SHALL be printed to stdout as a Rich table with columns: rank, score, memory text, and type tag.

#### Scenario: Search returns relevant results
- **WHEN** the user runs `n6 s "Python preferences"`
- **THEN** mem0 searches Qdrant and results are printed as a Rich table, ordered by relevance score

#### Scenario: Search with no results prints a friendly message
- **WHEN** the user runs `n6 s "something completely unknown"` and no memories match
- **THEN** the command prints "No memories found." to stdout and exits cleanly

#### Scenario: Search output is plain text when piped
- **WHEN** the output of `n6 s "query"` is piped to another command
- **THEN** the Rich table renders without color codes (Rich auto-detects non-TTY)

### Requirement: Commands are registered in main.py
The `m` command group and `s` command SHALL be registered on the main Typer app in `n6/main.py` so they are accessible as `n6 m` and `n6 s`.

#### Scenario: Help text is available
- **WHEN** the user runs `n6 m --help` or `n6 s --help`
- **THEN** Typer prints usage information for the respective command(s)
