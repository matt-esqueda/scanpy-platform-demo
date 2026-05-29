# Security Policy

---

## Development vs. Production

This repository contains a demo application with development defaults.

### Development (Default)

- Uses placeholder credentials (`scanpy_pass`)
- Suitable for local testing only
- **NOT for production use**

### Production Deployment

**Required changes:**

**1. Generate strong passwords**

```bash
# Example: Generate random password
openssl rand -base64 32
```

**2. Use environment variables**

```bash
export POSTGRES_PASSWORD="<strong-random-password>"
docker-compose up -d
```

**3. Enable authentication** (when implemented)
- Set `SECRET_KEY` and `JWT_SECRET`
- Configure user authentication

**4. Secure network access**
- Don't expose database ports publicly
- Use firewall rules
- Consider VPN or private networks