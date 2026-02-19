## ADDED Requirements

### Requirement: URL content can be fetched and stored as article
The system SHALL support fetching a URL's content via HTTP, stripping HTML tags and script/style elements to extract readable plain text, and storing the result using the same two-pass approach as `n6 m article` (facts extraction + verbatim). The source URL SHALL be stored in the memory metadata as `source`.

#### Scenario: Successful URL fetch and storage
- **WHEN** a valid URL is provided and the page is reachable
- **THEN** the page HTML is fetched, stripped to plain text, and stored in mem0 with `type=article`, `source=<url>`, and both `storage=facts` (infer=True) and `storage=verbatim` (infer=False) passes

#### Scenario: URL fetch fails due to network error
- **WHEN** the URL is unreachable or returns a non-200 status code
- **THEN** the system raises an error with a message indicating the fetch failed; nothing is stored

#### Scenario: Fetched content is very short
- **WHEN** the stripped text is fewer than 50 characters
- **THEN** the system raises an error indicating the page yielded no usable content
