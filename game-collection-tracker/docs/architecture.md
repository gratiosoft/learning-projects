# Architecture: Game Collection Tracker

See the [PRD](prd.md) for requirements and [ADRs](adr/) for the reasoning behind each choice.

## 1. System context

```mermaid
flowchart LR
    owner([Owner])
    friends([Friends])
    subgraph Airtable
      base[(Games base)]
      form[Form]
      iface[Interface: dashboard + gallery]
      auto[Automations]
    end
    subgraph AWS
      lambda[Cover-art Lambda]
      s3[(S3 covers bucket)]
      cf[CloudFront + OAC]
      ssm[SSM Parameter Store]
    end
    rawg[RAWG API]

    friends -->|submit| form --> base
    owner -->|view, edit| iface --> base
    base --> auto
    owner -->|CLI: list/add/backfill| base
    owner -->|CLI: backfill invokes| lambda
    lambda -->|read secrets| ssm
    lambda -->|search game| rawg
    lambda -->|put object| s3
    lambda -->|update Cover art URL| base
    cf -->|origin read| s3
    iface -->|loads cover image| cf
```

## 2. Components

```mermaid
flowchart TB
    subgraph pkg["src/game_tracker/"]
      cli[cli.py: list-games, add-game, backfill]
      handler[handler.py: Lambda entry point]
      config[config.py: env + SSM secrets]
      at[airtable_client.py]
      rawgc[rawg_client.py]
      up[s3_uploader.py]
    end
    cli --> at
    cli -->|boto3 lambda.invoke| handler
    handler --> config
    handler --> at
    handler --> rawgc
    handler --> up
```

Each module has one external dependency, so each is unit-tested with that dependency mocked (`responses` for HTTP, `moto` for S3/SSM/Lambda).

## 3. Data flow: cover art for one game

```mermaid
sequenceDiagram
    participant C as Caller (CLI / manual invoke)
    participant L as Lambda
    participant P as SSM
    participant A as Airtable
    participant R as RAWG
    participant S as S3
    C->>L: {record_id} or {title}
    L->>P: get RAWG key + Airtable token (cached per container)
    alt record_id given
        L->>A: GET record (title, current Cover art URL)
    end
    L->>R: GET /games?search=title
    R-->>L: results (best match by normalized title)
    alt no match
        L-->>C: error "game not found"
    end
    L->>R: GET image URL
    L->>S: PutObject covers/<record_id>.jpg (ContentType)
    L->>A: PATCH record: Cover art URL = https://<cloudfront>/covers/<record_id>.jpg
    L->>A: PATCH record: Cover art attachment = [{url}] (display copy, ADR 0007)
    L-->>C: {url}
```

Idempotency: the S3 key derives from the record id, so a re-run overwrites the same object and PATCHes the same URL. If the record already has the expected URL and the object exists, the handler returns early without calling RAWG.

## 4. Deployment

```mermaid
flowchart LR
    dev[Developer machine] -->|make package| zip[build/lambda.zip]
    dev -->|terraform apply, manual approval| tf[Terraform]
    tf --> s3b[S3 bucket: private, encrypted, block public access]
    tf --> cfd[CloudFront distribution + OAC]
    tf --> fn[Lambda + log group + IAM role]
    tf --> sp[SSM SecureString placeholders]
    dev -->|aws ssm put-parameter| sp
    zip --> fn
```

- IAM role: `s3:PutObject`/`GetObject`/`HeadObject` on `covers/*` only, `ssm:GetParameter` on `/game-tracker/*`, log writes to its own log group.
- The bucket policy allows reads only from this CloudFront distribution.
- Secret values are never in Terraform: parameters are created with a placeholder and `ignore_changes` on the value; the owner sets the real value with the AWS CLI.
