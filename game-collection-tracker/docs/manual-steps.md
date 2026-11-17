# Manual steps

The public Airtable REST API cannot create forms, interfaces or automations, so those are built in the Airtable UI, in the **Game Collection Tracker** base only. Free plan limits apply (1,000 records per base, 100 automation runs per month).

## A. Create the table (scripted)

1. Create an Airtable personal access token at <https://airtable.com/create/tokens> with scopes `data.records:read`, `data.records:write`, `schema.bases:read`, `schema.bases:write`, and access to this one base only.
2. Put it in `.env` as `AIRTABLE_TOKEN=...` along with `AIRTABLE_BASE_ID=app...` (no trailing comments on those lines).
3. Run `uv run setup-base`. It creates `Games` with colored select options and prints the table and field IDs. Paste them into the README under "Airtable".
4. In the base, delete the empty default "Table 1".

## B. Form (roadmap step 2)

1. In `Games`, click **+** next to the views list, choose **Form**, name it "Add a game".
2. Show: Title (required), Platform, Genre, Completion Status, Rating. Hide: Cover Art URL, Cover Art Attachment, Review Status.
3. Optional: set Completion Status default to "Backlog" via the field's "prefill" in the form editor.

## C. Automations (steps 4 and 5)

1. **Automations** tab, **Create automation**, name "Tag new games".
   - Trigger: **When record created**, table `Games`.
   - Action: **Update record**, record = the trigger record, field `Review Status` = `Unreviewed`.
   - Turn it on.
2. Create "Notify on new game".
   - Trigger: **When record created**, table `Games`.
   - Action: **Send email** to yourself (subject "New game: {Title}"). On Free you can only send to collaborators on the base; notifying friends needs a paid plan or a Slack/other integration.
   - Turn it on.
3. Test both by adding a record from the form, then check "Run history".

## D. Interface: dashboard and gallery (steps 3 and 11)

1. **Interfaces** tab, **Create interface**, name "Game Collection", layout **Dashboard** or blank.
2. Dashboard page: add number elements for **Total games** (count), **% completed** (needs a helper: add a formula checkbox field or a number element filtered to `Completion Status = Completed`; divide in a rollup/formula field, or show "Completed" and "Total" side by side), and **Average rating** (average of `Rating`).
3. Add a second page, type **Gallery** (or a record gallery), cover field = `Cover Art Attachment` (the Lambda writes `Cover Art URL`, which is a plain link; Airtable galleries only render attachments). Workaround: add a formula field `Cover` = `{Cover Art URL}` and use it in a **Grid with image** element, or open the URL from the record. Decide after the first backfill.
4. Add filter controls for Platform, Genre and Completion Status.
5. Publish the interface.

## E. Sharing with friends (step 12)

1. Open the form view, **Share form**, copy the public link and send it to friends. They can submit without an account.
2. To let friends view the collection, share the interface (**Publish**, then **Share**, choose "Anyone with the link can view").
3. Do not share the base itself.

## F. AWS (needs you)

1. Credentials: `aws configure sso --profile giancarlo` (or `aws configure --profile giancarlo`). Only a `default` profile exists right now. Check with `aws sts get-caller-identity --profile giancarlo`.
2. `cp infra/terraform.tfvars.example infra/terraform.tfvars` and set `airtable_base_id`, `aws_profile = "giancarlo"`.
3. `make plan` and review. `make deploy` only when you are ready.
4. After apply, set the secrets yourself (see README, "Deploy").
