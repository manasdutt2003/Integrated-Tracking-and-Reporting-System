# n8n automation

`bus-assistant-webhook.json` exposes the bus assistant as a webhook, so chat tools, forms or other n8n workflows can ask route questions without calling the Flask app directly.

```
POST /webhook/bus-assistant {"message": "Which bus goes to Redhills?"}
  -> Config -> POST {appUrl}/api/chat -> {"reply": "..."}
```

## Use it

1. Run the Flask app (`flask --app app run`, with `GEMINI_API_KEY` set) and start n8n (`docker run -it --rm -p 5678:5678 n8nio/n8n`).
2. Import `bus-assistant-webhook.json` in n8n and set `appUrl` in the **Config** node (use `http://host.docker.internal:5000` if n8n runs in Docker and the app on the host).
3. Activate the workflow and call it:

```bash
curl -X POST http://localhost:5678/webhook/bus-assistant \
  -H "Content-Type: application/json" -d '{"message":"Which bus goes to Redhills?"}'
```

If the app is down or the key is missing, the workflow answers with a fallback message instead of an error. Not yet run in a live n8n instance; verify node settings after importing.
