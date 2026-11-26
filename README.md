# rlv-test-opencollar

Automatic tests of the RLV code in [OpenCollar](https://github.com/OpenCollarTeam/OpenCollar), run without Second Life.

The scenarios drive OpenCollar's own scripts in the Script Lab sandbox of [PinglyMotion](https://github.com/pingledingle-tech/PinglyMotion) and check which RLV restrictions end up in force. Every run fetches OpenCollar at the commit pinned in `.github/workflows/scenarios.yml`; no OpenCollar file is stored here. OpenCollar's scripts are GPL v2 (see their LICENSE); the files in this repository are MIT.

- `scenarios/opencollar.rlvtest`: the test scenario.
- `driver/driver.lsl`: a test-only script that sends linked messages on request.
- `tools/assemble.sh`: builds the scenario object from an OpenCollar checkout.
- `docs/rlv-testing.md`: how to write and run scenarios, for people and AI assistants.

A pass is a sandbox result, never a Second Life result.

To test a newer OpenCollar, change `OPENCOLLAR_REF` in the workflow and the run shows whether the scenarios still hold.
