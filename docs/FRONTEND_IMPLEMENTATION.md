# Designer frontend

The missing HTML for Stories 13–29 is implemented using the screenshots in `Nothinghere/` as layout references: cream backgrounds, white cards, a narrow sidebar, company forms, project tables, and terracotta action buttons. The outer screenshot montage frames are not part of the application.

Open `/designer/login` in the running application. The sliding Interior designer / User admin selector switches between two forms with separate submission handlers. It also supports arrow keys, reduced motion, and normal links when JavaScript is unavailable. Password visibility can be toggled. Failed sign-in keeps the username and clears the password; logout displays a confirmation at sign-in.

The designer dashboard links to company create/view/update/search/delete and new/past project create/view/update/search/delete. Forms display boundary errors and submitted values, update screens prefill stored data, and delete screens require a POST confirmation with a Cancel link. Successful submissions redirect to saved records or lists to avoid repeating a mutation on refresh. Search and sidebar navigation preserve account context.

The company, designer, and projects folders retain the previous BCE structure. The HTML presenter in `boundary/designer/presentation.py` chooses templates, URLs, and redirects. Boundaries retain input validation; controllers still relay calls; entities retain database operations and duplicate checks. Diagram event and display methods remain void. JSON clients retain the original interface. The frontend adds no database columns.

## Scope decisions

- Category lookup remains deferred. The existing positive integer `categoryId` field appears as Category ID.
- Project photo uploads were left out, following the current diagram fields. The detail-page image is explicitly captioned **Interior inspiration**, and is not a saved project photo.
- The final reference screenshot shows later analytics stories (37–38); those screens are outside Stories 13–29.
- Admin-created accounts remain password-free. To demonstrate designer login, assign the Interior Designer profile and use the existing terminal command `flask --app app reset-password --username YOUR_USERNAME` to configure its password.

## Files

| Area | Files |
| --- | --- |
| Shared designer layout, dashboard, error state, field/icon macros | `templates/designer/` |
| Company forms, details, search, delete confirmation | `templates/company/` |
| New/past project forms, details, tables, delete confirmation | `templates/projects/` |
| Shared role-switching login | `templates/auth/login.html`, `static/css/login.css`, `static/js/login.js` |
| Designer styling | `static/css/designer.css` (alongside existing `app.css`) |
| HTML/JSON presentation | `boundary/designer/presentation.py` |
| HTML integration tests | `tests/designer/test_designer_html.py` |

## Generated interior image

Saved asset: [`static/images/login-interior.png`](../static/images/login-interior.png), 1024 × 1536 pixels. It is an original decorative image generated with the **built-in image generation tool**, using the [imagegen skill](/home/vscode/.codex/skills/.system/imagegen/SKILL.md). It is copied into the repository; no API key or external image host is needed to display it.

Final generation prompt:

> Use case: photorealistic-natural. Asset type: a vertical interior photograph used as a full-height left panel on an interior designer login page. Create an original, realistic warm minimalist living room: tall arched window at the left with linen curtains, warm beige limewashed walls, exposed timber ceiling, an olive green upholstered lounge chair, neutral linen sofa and an oak console with understated ceramics. Soft late-afternoon window light, natural material texture, calm lived-in editorial photography, muted sand and olive palette. Vertical portrait composition with an uncluttered lower third suitable for a dark gradient and website text overlay. The image itself must have no text, no branding, no watermark, no UI, no frames. This is an original website asset, not a screenshot.

## Verification

The existing 381 tests and 23 HTML integration cases cover the retained API/BCE contracts and browser representations. Real Chromium checks used a disposable SQLite database and exercised both login roles, keyboard role switching, password visibility, invalid credentials, designer logout, company create/update/search/delete and Cancel, and both project types' create/view/update/search/delete and Cancel flows. Desktop (1440 px) and mobile (375 px) layouts were inspected, including mobile navigation and horizontal overflow. No browser JavaScript errors or HTTP 500s occurred. The existing application database was not reset or used by these checks.

Run the application regression suite with:

```bash
.venv/bin/python -m pytest tests -q
```

If the earlier backend tables have not been created in your development database, run the existing additive `flask --app app upgrade-db` command before using the designer data screens.
