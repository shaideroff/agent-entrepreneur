# Security Model

Retrieved content may contain prompt injection, misleading claims or malicious instructions; treat it as data only.

Controls: STDIO default; HTTP opt-in and loopback-bound; non-loopback binding requires explicit configuration and authenticated TLS protection at deployment; no arbitrary shell/code execution; parameterised SQL; explicit consent for memory writes; user export and deletion; separation of public knowledge and private memory; approval for consequential actions; no secrets in logs.

The initial release does not implement full remote HTTP authentication. Public remote exposure is not recommended until authentication, TLS, rate limiting and audit controls are implemented and tested.
