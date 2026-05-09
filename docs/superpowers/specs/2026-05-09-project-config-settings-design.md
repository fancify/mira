# Project Config Settings Enhancement

## Overview

Enhance the Settings page's "项目配置" tab to show and edit ALL project configuration — vibe.yaml full content, .env files, and other config files — not just the limited fixed fields currently supported.

## Structure

Left-right split layout (existing). Left: project list with search. Right: config editor with **sub-tabs**:

### Sub-tab 1: 基础配置 (vibe.yaml)

**Form area** (top):
- name (text input)
- description (textarea)
- domain (text input)
- status (text input)
- service.port, service.health_path, service.health_token (inline group)
- 绑定密钥 (bound_keys chips + picker, existing)

**Advanced area** (bottom, collapsible):
- Full YAML raw editor (monospace textarea)
- Shows complete vibe.yaml content including aliases, tech_stack, deploy, etc.
- Editing raw YAML overrides form fields on save
- Save button writes back to `{project}/vibe.yaml`
- When form fields are saved, they merge into existing YAML (preserving unknown fields)

### Sub-tab 2: 环境变量 (.env)

- Scan project root for: `.env`, `.env.local`, `.env.production`, `.env.development`, `.env.staging`
- Each file = collapsible section with filename as header
- Each line rendered as key=value row:
  - Key: read-only label
  - Value: masked by default (`••••••`), click to reveal
  - Delete button (×) per row
- "Add" button at bottom of each file section
- Empty state: "No .env files found"
- Save writes back to original file path

### Sub-tab 3: 配置文件

- Scan project root (1 level deep) for: `config.json`, `config.yaml`, `config.toml`, `settings.json`, `*.config.js`, `*.config.ts`
- Exclude: `node_modules/`, `.venv/`, `__pycache__/`, `package.json`, `tsconfig.json`, `pyproject.toml` (build configs, not app configs)
- Each file = collapsible section with raw text editor (monospace textarea)
- Save writes back to original file
- Empty state: "No config files found"

## API Changes

### New Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/settings/projects/{id}/env-files` | GET | List .env files with key-value pairs (values masked unless `?reveal=true`) |
| `/api/settings/projects/{id}/env-files` | PUT | Save .env file content: `{filename: ".env", entries: [{key, value}]}` |
| `/api/settings/projects/{id}/config-files` | GET | List config files with content |
| `/api/settings/projects/{id}/config-files` | PUT | Save config file content: `{filename: "config.json", content: "..."}` |

### Modified Endpoints

| Endpoint | Change |
|----------|--------|
| `GET /api/settings/projects/{id}/config` | Add `raw_yaml` field containing full vibe.yaml text |
| `PUT /api/settings/projects/{id}/config` | Accept `raw_yaml` field; if present, write it directly (overrides form fields) |

### Existing Endpoints (unchanged)

- `GET/POST /api/settings/keys` — key vault
- `GET/PUT /api/settings/projects/{id}/config` — form fields (name, description, etc.)

## Security

- All endpoints require admin auth (`_is_admin` check)
- .env values masked by default in GET responses; `?reveal=true` returns real values
- File write paths validated: must be within the project directory (no `..` traversal)
- Config file scanning limited to project root + 1 level of depth
- Filenames validated against allowlist patterns

## UI Details

### Sub-tab bar
- Slim tab bar below the project name, styled like the detail page subnav
- Tabs: 基础配置 | 环境变量 | 配置文件
- Active tab has accent underline

### .env editor
- Table-like layout: key column (fixed width) + value column (flex) + action column
- Value field: password-type input, toggle eye icon to reveal
- Add row: inline form at bottom (key input + value input + add button)
- Delete: × button per row, confirm before removing

### Config file editor
- Monospace textarea, min-height 200px, auto-resize to content
- Filename as section header with file size badge
- Syntax hint based on extension (JSON / YAML / TOML)

### Save behavior
- Each sub-tab has its own save button
- Toast notification on success/failure
- No auto-save — explicit save only

## File Scanning Rules

### .env files
Pattern: `{project_root}/.env*`
Include: `.env`, `.env.local`, `.env.production`, `.env.development`, `.env.staging`, `.env.test`
Exclude: `.env.example`, `.env.sample`, `.env.template`

### Config files
Scan: `{project_root}/` and `{project_root}/*/` (1 level deep)
Include patterns: `config.{json,yaml,yml,toml}`, `settings.{json,yaml,yml}`, `*.config.{js,ts,mjs}` (read-only for JS/TS)
Exclude dirs: `node_modules`, `.venv`, `__pycache__`, `.git`, `dist`, `build`
Exclude files: `package.json`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml` (build tooling, not app config)
