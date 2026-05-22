---
name: aui-builder
description: Generate inline AUI blocks for chat using json-render and shadcn components.
---

# AUI Builder

Use this skill when the user asks for a UI, panel, form, dashboard, structured workspace, table, chart-like response, or richer report surface.
Use it proactively even when the user does not explicitly mention this skill by name.
If you are about to emit an `aui` or `aui-stream` fenced block, you should be following this skill rather than inventing the structure from memory.

Important scope boundary:
- This skill defines the contract for inline chat `aui` and `aui-stream` blocks.
- It does not define the MCP dashboard-app tool contract.
- If the task is using MCP tools such as `get_dashboard_protocol`, `open_dashboard_app`, `patch_dashboard_app`, or `replace_dashboard_app`, follow the dashboard-app protocol instead of this skill.
- Do not assume every component or shape in this skill is valid for dashboard-app.

Before emitting any AUI response, use this skill as the authoritative contract for:
- which code fence language to use
- which JSON shape is valid
- which component names are allowed
- when to use full-spec mode vs streaming mode

Do not invent ad hoc UI schemas, custom component names, or alternate fence formats when this skill already covers the task.
If there is any uncertainty, choose compliance with this skill over creativity.

## Output contract

There are two supported chat output modes.

### Mode 1: Full spec block

- Write brief prose first, then emit a fenced `aui` code block.
- The `aui` fence must contain JSON only.
- Use this mode only for small, stable UI payloads that can be emitted confidently in one pass.
- Supported shapes:
  1. A plain flat json-render spec: `{ "root": "root", "elements": { ... } }`
  2. A wrapped payload with state: `{ "ui": { "root": "root", "elements": { ... } }, "state": { ... } }`

Important:
- The wrapped `{ "ui": ..., "state": ... }` shape is for inline chat AUI only.
- It is not the correct input shape for dashboard-app MCP tools.
- For dashboard-app tools, pass the flat spec directly in `spec`: `{ "root": "root", "elements": { ... } }`

### Mode 2: Streaming spec block

- For larger applications, dashboards, workspaces, and multi-section report surfaces, prefer a fenced `aui-stream` code block.
- The `aui-stream` fence must contain newline-delimited JSON only.
- Each line must be a valid RFC 6902 patch operation that progressively builds the flat json-render spec.
- Prefer targeted `add`, `replace`, and `remove` operations over broad rewrites.
- Start by establishing `/root`, then add `/elements/<key>` entries.
- When any later element depends on stateful visibility or selection, emit the required `/state/...` patches before those elements.
- For `Tabs`, initialize the selected tab state before adding the `Tabs` element or any tab panels.
- This is the default mode for complex UI output. If you are unsure which mode to choose, choose `aui-stream`.

Example:

```aui-stream
{"op":"add","path":"/root","value":"root"}
{"op":"add","path":"/elements/root","value":{"type":"Card","props":{"title":"Dashboard"},"children":["metric-1","metric-2"]}}
{"op":"add","path":"/elements/metric-1","value":{"type":"Metric","props":{"label":"Revenue"}}}
{"op":"add","path":"/elements/metric-2","value":{"type":"Metric","props":{"label":"Users"}}}
```

Important: every `type` must be a real runtime component. Do not invent component names such as `TabsContent`, `TabsList`, `TabsTrigger`, `CardHeader`, or other React/shadcn subcomponents unless this skill explicitly lists them.
Also do not assume inline-only helpers such as `Container`, `CodeBlock`, or `ButtonGroup` are valid in dashboard-app.

## When to choose each mode

- Use `aui` only when the UI is truly small and stable:
  - a single card
  - a short form
  - a tiny settings panel
  - a simple two-to-three section layout with no expectation of progressive build
- Use `aui-stream` when:
  - the UI is large or app-like
  - the response benefits from progressive reveal
  - you are constructing a dashboard, workspace, report, or multi-panel application
  - the structure will likely be built in multiple steps
  - the UI contains tabs, multiple tables, multiple cards, charts, or many nested sections
- Prefer `aui-stream` whenever the output contains:
  - tabs
  - more than one table
  - more than one chart
  - more than one major card or panel
  - long instructional or report-style content that is easier to construct incrementally
- If the response is structurally complex, prefer `aui-stream` over a single `aui` block.
- For dashboards, workspaces, tabbed layouts, and report-style interfaces, `aui-stream` is the expected default.

In normal chat, prose may appear before either mode. Both modes are valid inline with ordinary assistant text.

## UI model

- Use native `@json-render/shadcn` component names.
- Prefer compact, app-like layouts over long prose.
- Prefer flat specs with:
  - top-level `root` string
  - top-level `elements` map
  - per-element `type`
  - per-element `props`
  - per-element `children` as child keys

## Preferred components

- Layout and structure:
  - `Stack`
  - `Card`
  - `Container`
  - `Grid`
  - `Separator`
  - `Tabs`
  - `Accordion`
  - `Collapsible`
  - `Dialog`
  - `Drawer`
  - `Carousel`
- Display:
  - `Heading`
  - `Text`
  - `Badge`
  - `Alert`
  - `Avatar`
  - `Progress`
  - `Tooltip`
  - `HoverCard`
  - `Popover`
  - `CodeBlock`
  - `Icon`
  - `Table`
  - `Chart`
- Inputs and actions:
  - `Input`
  - `Textarea`
  - `Select`
  - `Checkbox`
  - `Radio`
  - `Switch`
  - `Slider`
  - `Button`
  - `Link`
  - `DropdownMenu`
  - `Toggle`
  - `ToggleGroup`
  - `ButtonGroup`
  - `Pagination`
- Loading:
  - `Skeleton`
  - `Spinner`

## Extended components available in this runtime

These extended components are specific to the inline AUI chat runtime. Do not reuse them in dashboard-app unless the dashboard-app protocol explicitly allows them.

- `Icon`
  - props: `name`, optional `size`, optional `strokeWidth`
  - uses Lucide icon names
- `CodeBlock`
  - props: `text`, optional `language`
- `Container`
  - props:
    - `layout?` = `horizontal | vertical`
    - `gap?` = number
    - `align?` = `start | center | end | stretch | baseline`
    - `justify?` = `start | center | end | between | around | evenly`
    - `wrap?` = boolean
    - `padding?` = number
- `Grid`
  - props:
    - `columns?` = 1..6
    - `gap?` = `sm | md | lg` or number
- `Tabs`
  - use a single `Tabs` component
  - props:
    - `tabs` = `[{ label, value }]`
    - `defaultValue?` = string
    - `value?` = string
  - behavior:
    - the current runtime uses `Tabs` for the tab bar and selected value only
    - do not assume `Tabs.children` will automatically become tab panels
    - always provide `defaultValue`
    - prefer binding `props.value` to state, for example `{ "$bindState": "/activeTab" }`
    - when binding to state, explicitly initialize that state, for example `"state": { "activeTab": "daily" }` or `{"op":"add","path":"/state/activeTab","value":"daily"}`
    - in `aui-stream`, emit the tab state patch before the `Tabs` element and before any tab panels
    - render each tab body as a normal sibling element and control visibility from state
    - prefer `visible` conditions such as `{ "$state": "/activeTab", "eq": "writing" }`
  - do not emit separate `TabsContent`, `TabsList`, or `TabsTrigger` elements
- `Table`
  - props:
    - `caption?`
    - `columns?` = string[] or `[{ key?, label?, width? }]`
    - `rows?` = string[][] or record[]
- `Chart`
  - props:
    - `title?`
    - `chartType?` = `bar | line | pie | scatter | radar`
    - `data?` = `[{ label, value }]`
    - `series?` = `[{ name, data: number[] }]`
    - `categories?` = `string[]`
    - `height?`
    - `echartsOption?`
  - behavior:
    - if `echartsOption` is provided, it wins
    - otherwise `data` or `series + categories` drives the chart

## Chart examples

Simple bar chart:

```json
{
  "type": "Chart",
  "props": {
    "title": "Weekly traffic",
    "chartType": "bar",
    "height": 280,
    "data": [
      { "label": "Mon", "value": 120 },
      { "label": "Tue", "value": 180 },
      { "label": "Wed", "value": 160 }
    ]
  },
  "children": []
}
```

Multi-series line chart:

```json
{
  "type": "Chart",
  "props": {
    "title": "Keyword trend",
    "chartType": "line",
    "height": 300,
    "categories": ["Week 1", "Week 2", "Week 3"],
    "series": [
      { "name": "Brand", "data": [32, 44, 51] },
      { "name": "Non-brand", "data": [18, 27, 35] }
    ]
  },
  "children": []
}
```

## Tabs example

Use `Tabs` as a single runtime component with `props.tabs`, and bind the active tab to state. Do not model tabs as separate shadcn subcomponents, and do not rely on `Tabs.children` to become panels automatically.
In streaming mode, establish `activeTab` first so one panel is visible immediately.

```json
{
  "root": "tabs-shell",
  "state": {
    "activeTab": "daily"
  },
  "elements": {
    "tabs-shell": {
      "type": "Stack",
      "props": {
        "direction": "vertical",
        "gap": "md"
      },
      "children": ["tabs", "daily-panel", "plan-panel"]
    },
    "tabs": {
      "type": "Tabs",
      "props": {
        "defaultValue": "daily",
        "value": { "$bindState": "/activeTab" },
        "tabs": [
          { "label": "Writing", "value": "daily" },
          { "label": "Planning", "value": "plan" }
        ]
      },
      "children": []
    },
    "daily-panel": {
      "type": "Card",
      "props": {
        "title": "Writing"
      },
      "visible": { "$state": "/activeTab", "eq": "daily" },
      "children": ["daily-table"]
    },
    "daily-table": {
      "type": "Table",
      "props": {
        "columns": ["Command", "Purpose"],
        "rows": [["/write", "Run the writing pipeline"]]
      },
      "children": []
    },
    "plan-panel": {
      "type": "Card",
      "props": {
        "title": "Planning"
      },
      "visible": { "$state": "/activeTab", "eq": "plan" },
      "children": ["plan-text"]
    },
    "plan-text": {
      "type": "Text",
      "props": {
        "text": "Use planning commands to shape the next batch."
      },
      "children": []
    }
  }
}
```

## State and actions

- When the UI needs stateful inputs or dynamic lists, prefer the wrapped payload:
  - `{ "ui": { ... }, "state": { ... } }`
- Again: this wrapped payload is for inline AUI only, not dashboard-app MCP tools.
- Use `$state`, `$bindState`, `$bindItem`, `$template`, `visible`, and repeat where appropriate.
- Use `dispatchAction` when the next interaction should come back into the conversation.
- If you want to help the user send a suggested next prompt, you may use `dispatchAction` with `name: "prefill_chat_input"`.
  - payload:
    - `text` = required string to place into the chat input
    - `append?` = optional boolean to append instead of replace
    - `focus?` = optional boolean, defaults to true
  - this fills the chat composer for the user; it does not auto-send

Example:

```json
{
  "type": "Button",
  "props": {
    "label": "Use this prompt"
  },
  "on": {
    "press": {
      "action": "dispatchAction",
      "params": {
        "name": "prefill_chat_input",
        "payload": {
          "text": "Please turn this outline into a polished task plan."
        }
      }
    }
  },
  "children": []
}
```

## Minimal example

```aui
{
  "ui": {
    "root": "root",
    "elements": {
      "root": {
        "type": "Card",
        "props": {
          "title": "Overview",
          "description": "Structured summary"
        },
        "children": ["body"]
      },
      "body": {
        "type": "Stack",
        "props": {
          "direction": "vertical",
          "gap": "md"
        },
        "children": ["intro", "action"]
      },
      "intro": {
        "type": "Text",
        "props": {
          "text": "This is a minimal AUI response."
        },
        "children": []
      },
      "action": {
        "type": "Button",
        "props": {
          "label": "Continue"
        },
        "on": {
          "press": {
            "action": "dispatchAction",
            "params": {
              "name": "continue"
            }
          }
        },
        "children": []
      }
    }
  },
  "state": {}
}
```

