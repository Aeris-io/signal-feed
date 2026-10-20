# Signal Feed API reference

```
GET https://aerisvalidator.space/alerts/api/alerts_feed.json
GET https://aerisvalidator.space/alerts/api/alerts_feed.xml     (RSS 2.0)
```

Static files, rebuilt continuously. No authentication. Schema id: `aeris.celestia.alert_center.v2`.

## Top level

| Field | Type | Description |
|---|---|---|
| `schema` | string | `aeris.celestia.alert_center.v2` |
| `updated_at_utc` | string | When the feed was built |
| `sources` | object | Description of each upstream source, keyed by category |
| `counts` | object | `total` and `by_severity: {high, medium, low, info}` |
| `alerts` | array | The timeline, see below |
| `note` | string | Notes on the feed |

## `alerts[]`

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable id. Use it to deduplicate, e.g. `gov-9` |
| `category` | string | `governance`, `network_upgrade` or `bridge_health` |
| `kind` | string | What happened: `new_proposal`, `passed`, `risk_change`, … |
| `severity` | string | `high`, `medium`, `low` or `info` |
| `title` | string | One line |
| `summary` | string | One or two sentences |
| `detail` | string | What it means for an operator |
| `ts_utc` | string | When it happened, ISO 8601 UTC |
| `source_url` | string | Where to read more. May be relative to `https://aerisvalidator.space/alerts/` |
| `meta` | object | Category-specific fields, see below |
| `raw_source` | object | `endpoint` it came from and the untouched `record` |

### `meta` by category

**`governance`**

| Field | Description |
|---|---|
| `proposal_id` | On-chain proposal id |
| `status` | e.g. `PROPOSAL_STATUS_PASSED` |
| `voting_end_time` | End of the voting period |
| `proposer` | Proposer address |

`raw_source.record` keeps the full proposal, including `final_tally_result`.

**`network_upgrade`**

| Field | Description |
|---|---|
| `cip_id` | e.g. `CIP-17` |
| `audience` | Who the CIP affects, from its header |

`raw_source.record` keeps `status_from`, `status_to` and the recommended action.

**`bridge_health`**

| Field | Description |
|---|---|
| `chain_id` | Counterparty chain |
| `client_id` | IBC client whose risk level changed |

`raw_source.record` is the event exactly as Bridge & Client Watch logged it, with `risk_from` and `risk_to`.

## RSS

Each alert is one `<item>`:

- `<title>`: `[SEVERITY] title`
- `<category>`: the alert's `category`
- `<pubDate>`: `ts_utc`
- `<guid>`: stable per alert
