# So-What Metrics

Gold metrics are designed for creator operations, community management, and moderation outcomes.

## Metrics

- Chat engagement rate.
- Messages per active chatter.
- Sentiment trend by stream segment.
- Spam/toxicity risk rate (proxy).
- Emote intensity per minute.
- Moderation alert rate.
- New vs returning chatter mix (planned, requires user history table).

## Business Questions Supported

- Is chat quality improving during key stream segments?
- Are message bursts driven by engaged users or low-signal spam?
- When should moderators be proactively staffed?
- Which content moments drive healthy participation vs reactive negativity?

## dbt Artifact

Primary v2 stakeholder model: `fct_stakeholder_engagement_metrics`.
