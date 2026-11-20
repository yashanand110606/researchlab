# Security Considerations

## Threat Model

### Input Validation
All user input is validated through Pydantic v2 schemas:
- String length limits enforced
- UUID format validation
- Enum constraints on categorical fields
- Type coercion with clear error messages

### SQL Injection Prevention
- SQLAlchemy ORM parameterization prevents injection
- Raw SQL avoided; when necessary, use `text()` with parameters
- No string concatenation in queries

### File Upload Security
- Size limits enforced (configurable via MAX_UPLOAD_SIZE_MB)
- Filename sanitization (path traversal prevention)
- Checksum verification (SHA-256)
- Format whitelist by extension/mime type

### Configuration Safety
- Safe YAML loading (no arbitrary object instantiation)
- Configuration hashing for immutability tracking
- No eval/exec of user-provided code
- Only registered experiment classes can be executed

### CORS Configuration
- Origins configurable via environment variable
- Credentials allowed only for trusted origins
- Methods and headers restricted to required set

## Secrets Management

Environment variables only — no hardcoded credentials:

```bash
# Required
POSTGRES_HOST=localhost
POSTGRES_USER=researchlab
POSTGRES_PASSWORD=<secure-password>
POSTGRES_DB=researchlab

# Optional
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0
```

Never commit `.env` files or secrets to version control.

## Dependency Security

Regular audits recommended:

```bash
# Python dependencies
pip audit

# JavaScript dependencies
npm audit
npx npm-audit-fix
```

Current critical/high vulnerabilities should be addressed before production deployment.

## Audit Logging

All experiment executions are logged:
- Configuration snapshots preserved
- Random seeds tracked for reproducibility
- Worker assignments recorded
- Error messages captured for debugging

## Production Hardening Checklist

- [ ] Enable HTTPS/TLS termination
- [ ] Configure rate limiting
- [ ] Set up request timeouts
- [ ] Implement authentication/authorization
- [ ] Enable database encryption at rest
- [ ] Rotate secrets regularly
- [ ] Monitor for unusual access patterns
- [ ] Keep dependencies updated
- [ ] Run security scanning in CI/CD
