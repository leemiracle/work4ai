# Notion API — Endpoint & Object Reference

All requests go to `https://api.notion.com/v1/` with these headers:

```
Authorization: Bearer ${NOTION_API_KEY}
Notion-Version: 2025-09-03
Content-Type: application/json          # on any request with a body
```

Official docs: `https://developers.notion.com/reference`.

## Table of contents

- [Endpoints](#endpoints)
- [Rich text objects](#rich-text-objects)
- [Block types](#block-types)
- [Property types & filter conditions](#property-types--filter-conditions)
- [Parent objects](#parent-objects)

---

## Endpoints

### Search

- **`POST /search`** — Body: `{query, filter:{property:"object", value:"page"|"data_source"}, sort:{direction, timestamp:"last_edited_time"}, start_cursor, page_size}`. Matches titles only. Omit `query` to list all accessible objects.

### Pages

- **`POST /pages`** — Create. Body: `{parent, properties, children?, icon?, cover?}`. `parent` is a `data_source_id` (row) or `page_id` (sub-page). `children` max 100 blocks.
- **`GET /pages/{id}`** — Page metadata + properties. Not the body — use block children for that. Query param: `filter_properties` (repeat to select a subset).
- **`PATCH /pages/{id}`** — Update. Body: `{properties?, archived?, icon?, cover?}`. Properties not in the body are left unchanged.
- **`GET /pages/{id}/properties/{property_id}`** — Retrieve a single property's value. Needed for large values: `rich_text`/`title` >25 items, `relation` >25 refs, `people` >25, `rollup` full results. Paginated.

### Databases & data sources

A database is a container; each of its data sources owns a schema and rows. Get the data source ID
from `GET /databases/{id}` → `data_sources[].id`.

- **`GET /databases/{id}`** — The container: `title`, `description`, `parent`, `is_inline`, `data_sources: [{id, name}]`. No schema here.
- **`POST /databases`** — Create a database. Body: `{parent:{page_id}, title, initial_data_source:{properties}}`. `properties` must include exactly one `title` type.
- **`PATCH /databases/{id}`** — Update container-level attributes: `title`, `description`, `icon`, `is_inline`, `parent`.
- **`GET /data_sources/{id}`** — Schema: `title`, `description`, `properties{}`, `parent` (the database), `database_parent`.
- **`POST /data_sources/{id}/query`** — Body: `{filter?, sorts?, start_cursor?, page_size?}`. Query param: `filter_properties` (repeatable `?filter_properties=PROPERTY_ID`). Returns page objects.
- **`POST /data_sources`** — Add another data source to an existing database. Body: `{parent:{database_id}, title?, properties}`.
- **`PATCH /data_sources/{id}`** — Update schema (`properties`), `title`, or trash status. Set a property to `null` to delete it.

### Blocks

- **`GET /blocks/{id}`** — One block.
- **`GET /blocks/{id}/children`** — List direct children. Params: `start_cursor`, `page_size` (≤100). Recurse on `has_children: true`.
- **`PATCH /blocks/{id}/children`** — Append blocks to the end. Body: `{children: [...], after?: "BLOCK_ID"}`. Max 100.
- **`PATCH /blocks/{id}`** — Update a block's content. Body: `{<type>: {...}, archived?}`. Cannot change a block's `type`.
- **`DELETE /blocks/{id}`** — Archive (soft-delete). Restore with `PATCH {"archived": false}`.

### Users

- **`GET /users`** — List all users (people + bots) in the workspace. Params: `start_cursor`, `page_size`.
- **`GET /users/{id}`** — One user.
- **`GET /users/me`** — The integration's bot user. Good for auth sanity checks.

### Comments

- **`GET /comments`** — List comments on a block. Params: `block_id` (required), `start_cursor`, `page_size`.
- **`POST /comments`** — Create. Body: `{parent:{page_id}, rich_text}` to comment on a page, or `{discussion_id, rich_text}` to reply to a thread. Requires the "comment" capability.

---

## Rich text objects

Most text in Notion — block content, page/database titles, `rich_text` properties — is an **array of
rich-text objects**. Each object has a `type`, a same-named payload, optional `annotations`,
`plain_text`, and `href`.

```json
{
  "type": "text",
  "text": {"content": "Bold link", "link": {"url": "https://example.com"}},
  "annotations": {"bold": true, "italic": false, "strikethrough": false, "underline": false, "code": false, "color": "default"},
  "plain_text": "Bold link",
  "href": "https://example.com"
}
```

Types: `text` (the common case), `mention` (user / page / database / date / link-preview),
`equation` (`{"expression": "e=mc^2"}`). `color` values: `default`, `gray`, `brown`, `orange`,
`yellow`, `green`, `blue`, `purple`, `pink`, `red`, and each with `_background` suffix.

When **writing** rich text, the minimal form is `[{"text": {"content": "..."}}]` — `type` defaults
to `text` and annotations default to off. When **reading**, use `plain_text` for display; use
`.text.content` + `.annotations` if you need structure.

Limits: each `text.content` ≤ 2000 chars, each `text.link.url` ≤ 2000 chars, each
`equation.expression` ≤ 1000 chars, and a `rich_text` array is capped at 100 items.

## Block types

Every block has `object: "block"`, `id`, `type`, `has_children`, `created_time`, `last_edited_time`,
and a key named after `type` holding the payload. Common types:

- **`paragraph`** (`{rich_text, color, children?}`)
- **`heading_1` / `heading_2` / `heading_3`** (`{rich_text, color, is_toggleable}`) — Toggleable headings can have children.
- **`bulleted_list_item` / `numbered_list_item`** (`{rich_text, color, children?}`) — Nesting makes sub-items.
- **`to_do`** (`{rich_text, checked, color, children?}`)
- **`toggle`** (`{rich_text, color, children?}`) — Children are hidden/shown.
- **`quote`** (`{rich_text, color, children?}`)
- **`callout`** (`{rich_text, icon, color, children?}`) — `icon`: `{emoji}` or `{external:{url}}`.
- **`code`** (`{rich_text, language, caption}`) — `language`: `bash`, `python`, `javascript`, `json`, `sql`, `plain text`, and ~60 more.
- **`divider`** (`{}`)
- **`table_of_contents`** (`{color}`)
- **`equation`** (`{expression}`) — KaTeX.
- **`bookmark`** (`{url, caption}`)
- **`embed`** (`{url}`)
- **`image` / `video` / `audio` / `file` / `pdf`** (`{type:"external", external:{url}, caption}` or `{type:"file", file:{url, expiry_time}}`) — Notion-hosted (`file`) URLs expire after ~1 h — re-fetch the block. When creating, only `external` is accepted.
- **`link_preview`** (`{url}`) — Read-only. Cannot be created via API.
- **`table`** (`{table_width, has_column_header, has_row_header}`) — Children are `table_row` blocks. Cannot change `table_width` after creation.
- **`table_row`** (`{cells: [[rich_text...], ...]}`) — One inner array per column, length must equal `table_width`.
- **`column_list` / `column`** (`{children?}`) — `column_list` children are `column`s; columns hold content blocks. Must create with ≥2 columns, each with ≥1 child.
- **`child_page`** (`{title}`) — Read-only marker. Create with `POST /pages` using a `page_id` parent.
- **`child_database`** (`{title}`) — Read-only marker. Create with `POST /databases`.
- **`synced_block`** (`{synced_from: null | {block_id}, children?}`) — `null` = original; `{block_id}` = reference.
- **`breadcrumb`** (`{}`)
- **`unsupported`** (`{}`) — The API can't represent this block type (some templates, buttons, AI blocks). Read-only placeholder.

When **appending** blocks, each element must have `type` and the matching payload key:
`{"type": "paragraph", "paragraph": {"rich_text": [...]}}`. When **updating**, omit `type`.

## Property types & filter conditions

A data source's `properties` maps property **name** → `{id, type, <type>: {config}}`. A page's
`properties` maps name → `{id, type, <type>: <value>}`. Filters are keyed by name and type.

- **`title`** (`{title: [rich_text...]}`) — `equals`, `does_not_equal`, `contains`, `does_not_contain`, `starts_with`, `ends_with`, `is_empty`, `is_not_empty`
- **`rich_text`** (`{rich_text: [rich_text...]}`) — same as `title`
- **`number`** (`{number: 42}`) — `equals`, `does_not_equal`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to`, `is_empty`, `is_not_empty`
- **`select`** (`{select: {name, id, color}}`) — `equals`, `does_not_equal`, `is_empty`, `is_not_empty`
- **`multi_select`** (`{multi_select: [{name, id, color}...]}`) — `contains`, `does_not_contain`, `is_empty`, `is_not_empty`
- **`status`** (`{status: {name, id, color}}`) — `equals`, `does_not_equal`, `is_empty`, `is_not_empty`
- **`date`** (`{date: {start, end?, time_zone?}}`) — `equals`, `before`, `after`, `on_or_before`, `on_or_after`, `is_empty`, `is_not_empty`, `past_week`, `past_month`, `past_year`, `this_week`, `next_week`, `next_month`, `next_year` (the relatives take `{}` as value)
- **`people`** (`{people: [{id, ...}...]}`) — `contains`, `does_not_contain`, `is_empty`, `is_not_empty`
- **`files`** (`{files: [{name, type, ...}...]}`) — `is_empty`, `is_not_empty`
- **`checkbox`** (`{checkbox: true}`) — `equals`, `does_not_equal`
- **`url`** (`{url: "https://..."}`) — text conditions
- **`email` / `phone_number`** (`{email: "..."}`) — text conditions
- **`relation`** (`{relation: [{id}...], has_more?}`) — `contains`, `does_not_contain`, `is_empty`, `is_not_empty`
- **`rollup`** (`{rollup: {type, number|date|array, function}}`) — `number`, `date`, `any`, `every`, `none` (nest the target type's condition)
- **`formula`** (`{formula: {type, string|number|boolean|date}}`) — `string`, `number`, `checkbox`, `date` (nest the matching condition)
- **`created_time` / `last_edited_time`** (`{created_time: "ISO8601"}`) — date conditions
- **`created_by` / `last_edited_by`** (`{created_by: {id, ...}}`) — `contains`, `does_not_contain`, `is_empty`, `is_not_empty`
- **`unique_id`** (`{unique_id: {prefix, number}}`) — number conditions
- **`verification`** (read-only)

Compound filters: `{"and": [c1, c2, ...]}` and `{"or": [c1, c2, ...]}`, nestable to two levels.

Sorts: `[{"property": "Name", "direction": "ascending"}]` or
`[{"timestamp": "last_edited_time", "direction": "descending"}]`.

## Parent objects

Everything has a `parent`. When creating, you set it once; it can't be changed via the API.

- **`{"type": "data_source_id", "data_source_id": "..."}`** — A page that's a database row. Use this when creating rows.
- **`{"type": "database_id", "database_id": "..."}`** — A data source's parent (the container database).
- **`{"type": "page_id", "page_id": "..."}`** — A sub-page or inline database.
- **`{"type": "block_id", "block_id": "..."}`** — A block nested under another block.
- **`{"type": "workspace", "workspace": true}`** — Top-level (read-only; can't create here via API).
