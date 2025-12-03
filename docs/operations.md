# Operations & Troubleshooting

## Endpoints
- Dashboard: http://localhost:3000
- API: http://localhost:5000
- Prometheus: http://localhost:9090

## Common issues
- Port conflicts: ensure 3000/5000/9090 are free
- Database not ready: wait 10–20s; backend retries
- Health check failing: check `ar_app` logs; verify `.env`

## Updating configuration
Use API to update thresholds without redeploying.
```json
PUT /api/config
{
  "key": "error_rate_threshold",
  "value": 0.10
}
```