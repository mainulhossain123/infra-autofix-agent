# API Reference

> **🎯 Interactive API Documentation**: Visit the [Swagger UI](http://localhost:5000/api/docs) for an interactive API explorer with live testing!

Base URL: `http://localhost:5000`

## 📚 Swagger/OpenAPI Documentation

The API is fully documented using OpenAPI 3.0 specification with interactive Swagger UI.

### Access Points

| Resource | URL | Description |
|----------|-----|-------------|
| **Swagger UI** | [http://localhost:5000/api/docs](http://localhost:5000/api/docs) | Interactive API documentation and testing |
| **OpenAPI Spec** | [http://localhost:5000/apispec.json](http://localhost:5000/apispec.json) | Raw OpenAPI JSON specification |

### Features

- ✅ **Try It Out**: Execute API calls directly from the browser
- ✅ **Request/Response Examples**: See sample payloads for all endpoints
- ✅ **Schema Validation**: Understand required fields and data types
- ✅ **Authentication**: Test with different auth mechanisms
- ✅ **Download Spec**: Export OpenAPI spec for client SDK generation

---

## Quick Reference

## Health & Metrics
- GET `/api/health`
- GET `/api/metrics`
- GET `/metrics`
- GET `/api/database/health`
- GET `/api/database/connections`

## Incidents
- GET `/api/incidents`
- GET `/api/incidents/{id}`

## Remediation
- GET `/api/remediation/history`
- POST `/api/remediation/manual`

Example:
```json
POST /api/remediation/manual
{
  "action_type": "restart_container",
  "target": "ar_app",
  "reason": "Manual intervention"
}
```

## Configuration
- GET `/api/config`
- GET `/api/config/{key}`
- PUT `/api/config`

Example:
```json
PUT /api/config
{
  "key": "error_rate_threshold",
  "value": 0.10
}
```