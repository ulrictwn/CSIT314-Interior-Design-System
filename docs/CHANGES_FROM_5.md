# Integrating the seven additions

This is a combined source package, not a patch to apply blindly to a teammate's newer branch. Compare against your actual checkout before copying. No files in your GitHub repository have been changed by this download.

## Added areas

- Account boundary/controller modules and their per-class import wrappers.
- Account forms, five account templates, dashboard and login/logout pages.
- UserAccount, account ID counter, login attempts and revocable login sessions.
- Account/session validation, server-side authorization, trusted bootstrap/password recovery commands.
- Tests for stories 6–12 and account security; a regression check for the approved profile-search behavior.

## Existing areas updated

- `app.py`, routes, navigation and shared base HTML now use real User Admin authentication. Production ignores the old profile preview flag. Test actors remain available only in Flask testing mode to keep the original profile tests isolated.
- Profile update guards the final administrator's role/name/permissions; profile suspension still protects all assigned accounts.
- The database upgrade preserves the earlier profile schema and creates the new tables. An unrelated or incomplete pre-existing `user_account` table requires a reviewed migration; the command stops with a message.
- The requirements add email validation. Install from `requirements-dev.txt` for application plus testing libraries.
- Current tests now live in `tests/sprint_1/` through `tests/sprint_5/`, using shared fixtures in `tests/conftest.py`. All 22 documented Sprint 1 checks, including TC08 and TC09, are present; later stories have one test each. See [the current test guide](TESTING_GUIDE.md).
- The existing `profile-ci.yml` workflow and historical test/report script filenames now cover all five sprints. Test-result artifacts use `sprint-reports-*` names.

## Keep your own local configuration

Preserve `.env`, database files, `.postgres-data`, `.venv` and the working `.devcontainer` files. They are not shipped in the package. Keep your existing secret key and database credentials. This ZIP is source code, not a database backup.

After merging source, follow README's install → upgrade-db → bootstrap-admin → start sequence. Review changed files in Source Control, run the tests, commit on your working branch and push that branch. Use your normal pull-request process to merge into main. This package does not perform a deployment.
