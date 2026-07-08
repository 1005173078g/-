# News Lianbo WeCom Daily Brief Design

## Goal

Every day after Xinwen Lianbo has aired and the official source is reasonably available, generate a mobile-friendly HTML brief and send its GitHub Pages link to the user's WeCom group.

The brief should follow the user's reference format:

- A short opening sentence that states how many market-relevant mainlines were extracted.
- One card per mainline, using `消息面`, `逻辑`, and `观察`.
- A final `观察顺序`, `跟踪要点`, and `边际信号` section.

The number of mainlines is dynamic. The system summarizes however many clear mainlines appear in that day's program; it does not force exactly six.

## Inputs

- Primary news source: official CCTV/CCTV.com Xinwen Lianbo text or video page.
- Scheduled run time: 21:30 Beijing time every day.
- WeCom delivery: group robot webhook supplied by the user.
- Web publishing target: GitHub Pages for `https://github.com/1005173078g/-.git`.

## Output

For each date, the workflow produces:

- A static HTML page named by date, for example `2026-07-09.html`.
- A WeCom markdown message containing:
  - Date and title.
  - Extracted mainline count.
  - Observation order.
  - GitHub Pages URL.

The HTML is optimized for phone reading. It uses a concise card layout similar to the provided screenshots, with readable Chinese typography, soft section colors, and no reliance on JavaScript.

## Content Rules

Each mainline should be derived from the day's Xinwen Lianbo content and converted into a market observation chain:

1. `消息面`: What happened in the broadcast.
2. `逻辑`: Why it matters for policy direction, industry trend, or capital attention.
3. `观察`: Up to three relevant A-share or Hong Kong-listed companies when a reasonably direct mapping exists.

The workflow should avoid pretending every news item has a tradable mapping. If a segment is politically or diplomatically important but not useful as an industry observation, it can be summarized in narrative form or excluded from the market-mainline list.

Investment language stays conservative:

- Use `观察`, not `推荐`, `买入`, or `确定性机会`.
- Include a short disclaimer that the page is an information summary, not investment advice.
- Prefer liquid, recognizable leaders or direct beneficiaries over obscure targets.

## Publishing Flow

1. Fetch official Xinwen Lianbo source after 21:30.
2. Extract and summarize the day's program.
3. Generate structured JSON for the brief.
4. Render the JSON into a static HTML file.
5. Commit and push the HTML to the GitHub Pages repository.
6. Send the public page URL to the WeCom robot.

## Failure Handling

If the official source is not available:

- Retry during the run if practical.
- If still unavailable, send a WeCom notice saying the official source is not yet available and no summary was published.

If GitHub publishing fails:

- Keep the generated HTML locally in `outputs`.
- Send a WeCom notice that generation succeeded but publishing failed.

If WeCom sending fails:

- Leave the generated and published HTML intact.
- Record the failure in the run output so it can be retried manually.

## Configuration

Sensitive values should not be committed into the public repository. The WeCom webhook should be stored in automation configuration or environment variables.

The repository URL and GitHub Pages base URL can be non-secret configuration.

## Open Implementation Decisions

- Whether GitHub Pages is already enabled for the repository or must be enabled once in GitHub settings.
- Whether the automation environment already has credentials that can push to `1005173078g/-.git`.
- The exact official CCTV page parsing route may need verification during implementation because CCTV page structure can change.
