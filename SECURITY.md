# Security Policy

## Supported versions

Security updates and patches are provided for the following versions:

| Version | Supported |
| :--- | :---: |
| 1.0.x | Yes |
| < 1.0 | No |

---

## Reporting a vulnerability

If you discover a security vulnerability in BigBlueSync, please report it responsibly rather than opening a public issue.

### Reporting process
1. Email your report to the repository maintainers or use GitHub's private vulnerability reporting feature under the Security tab.
2. Include the following details in your report:
   - Description of the vulnerability and its potential impact.
   - Step-by-step reproduction instructions or a proof of concept.
   - Operating system and Python version used during testing.
3. You will receive an initial response within 48 hours acknowledging receipt.
4. A fix will be developed, tested, and released along with a security advisory.

---

## Security considerations and design rationale

BigBlueSync handles network requests, local file operations, and external process execution. The following security practices are implemented in the codebase:

### 1. SSL context configuration
Institutional BigBlueButton deployments occasionally use internal or non-standard certificate authorities. BigBlueSync uses an explicit SSL context configured to prevent connection aborts on valid institutional recordings while isolating the session inside a dedicated `urllib.request.build_opener` instance.

### 2. Subprocess execution
FFmpeg commands are passed as discrete argument lists rather than raw shell strings (`shell=False`), mitigating command injection risks when processing dynamic filenames or paths. On Windows systems, `0x08000000` (`CREATE_NO_WINDOW`) is passed to prevent unexpected console spawns.

### 3. Path traversal protection
Target paths for downloaded streams are constructed using `os.path.join` with sanitized meeting identifiers, preventing path traversal attacks from crafted URLs.
