# #legacy_551a Legacy issue: fix(test): prevent pytest teardown from wiping realistic seed database and align default-org slug

- 2026-09-09T11:07:19Z `issue`: Legacy issue: fix(test): prevent pytest teardown from wiping realistic seed database and align default-org slug
- 2026-09-09T11:07:19Z `fix`: fix(test): prevent pytest teardown from wiping realistic seed database and align default-org slug
- 2026-09-09T17:00:04Z `attempt`: tried teardown deleting all organizations where slug != 'default-org', which wiped out seeded CA firm records on every test run [backend/tests/conftest.py] (failed)
