# Twilio WhatsApp Integration

## Overview
This module handles incoming WhatsApp messages via Twilio webhooks and creates records in the Directus `whatsapp_messages` collection.

## Endpoints

### POST /twilio/whatsapp/incoming
Receives incoming WhatsApp messages from Twilio.

**Content-Type:** `application/x-www-form-urlencoded`

**Security:** Validates Twilio signature using `X-Twilio-Signature` header

**Flow:**
1. Validate Twilio signature (security)
2. Extract message data from webhook payload
3. Parse phone numbers (remove `whatsapp:` prefix)
4. Extract media URLs if present
5. Create record in Directus `whatsapp_messages` collection
6. Return success response to Twilio

### GET /twilio/whatsapp/health
Health check endpoint for monitoring.

## Configuration

### Required Environment Variables
```bash
# Directus Connection
DIRECTUS_URL=https://shinobi-directus.onrender.com
DIRECTUS_ADMIN_TOKEN=your_admin_token_here

# Twilio Credentials
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
```

## Twilio Webhook Setup

### Sandbox Configuration (Testing)
1. Navigate to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Note your sandbox number (e.g., +1 415 523 8886)
3. Configure webhook:
   - **URL:** `https://shinobi-agents.onrender.com/twilio/whatsapp/incoming`
   - **Method:** POST
   - **Content-Type:** application/x-www-form-urlencoded

### Production Configuration
1. Request WhatsApp Business API access from Twilio
2. Verify your business profile
3. Configure production webhook with same URL

## Testing

### Manual Test with curl
```bash
# Simulate Twilio webhook (for local testing only - signature validation will fail)
curl -X POST http://localhost:8080/twilio/whatsapp/incoming \
  -d "MessageSid=SM1234567890" \
  -d "AccountSid=AC1234567890" \
  -d "From=whatsapp:+447123456789" \
  -d "To=whatsapp:+14155238886" \
  -d "Body=Hello from WhatsApp" \
  -d "NumMedia=0"
```

### Test with Actual WhatsApp
1. Join Twilio sandbox (send "join [code]" to sandbox number)
2. Send a test message to sandbox number
3. Check Directus `whatsapp_messages` collection for new record
4. Verify `verification_status` is "pending"

## Security

### Signature Validation
All incoming webhooks are validated using Twilio's signature validation:
- Uses `TWILIO_AUTH_TOKEN` to validate `X-Twilio-Signature` header
- Invalid signatures return 403 Forbidden
- Protects against unauthorized webhook calls

### Rate Limiting
Consider implementing rate limiting at the infrastructure level:
- Cloudflare rate limiting
- Render.com rate limiting
- Application-level rate limiting middleware

## Data Flow

```
Twilio WhatsApp → Webhook → Directus whatsapp_messages
                     ↓
            Directus Flow (Verification)
                     ↓
              CommsAgent (Response)
                     ↓
          human_prompts (Approval)
                     ↓
     Twilio API (Send Approved Response)
```

## Next Steps

After webhook is working:
1. Create Directus Flow: "WhatsApp Inbound → Verification"
2. Create Directus Flow: "WhatsApp Verification Response"
3. Create Directus Flow: "Comms Agent → WhatsApp Response"
4. Test end-to-end workflow

## Troubleshooting

### Webhook not receiving messages
- Check Twilio webhook URL is correct
- Verify webhook is using HTTPS (Twilio requires SSL)
- Check Twilio console for webhook errors
- Verify service is running on correct port (8080 on Render)

### Signature validation failing
- Ensure `TWILIO_AUTH_TOKEN` environment variable is set
- Check token matches Twilio console
- Verify webhook URL in code matches Twilio configuration exactly

### Messages not appearing in Directus
- Check agent service logs
- Verify `DIRECTUS_ADMIN_TOKEN` has write permissions
- Check `whatsapp_messages` collection exists
- Verify Directus is accessible from agent service
