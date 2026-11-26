# Testing RLV and LSL code with scenarios

A scenario is a text file that drives scripts in a simulated object and states what must be true afterwards. The runner `pinglymotion_rlvtest` (PinglyMotion's Script Lab) plays it with no window. A pass is a sandbox result; the final test is always in Second Life.

## Layout

```
scripts/<object>/<Prim>/*.lsl      one folder per object, one subfolder per prim (Root is the root prim)
scenarios/<object>.rlvtest         the scenario; its name must equal the object folder name
```

One object has one scenario file; use sections inside it. A scenario with no object folder runs against an empty object.

## Scenario lines

| Line | Meaning |
|---|---|
| `# text` | note |
| `say <channel> <text>` | the wearer's chat line on that channel (negative channels work) |
| `touch <prim>` | the wearer touches a prim |
| `menu <button>` | the wearer presses a button in the open dialog (the check-box glyph may be left out) |
| `send @command` | an RLV line from the object of the last `object <name>` line |
| `wait <seconds>` | simulated seconds |
| `expect [not] <key> [text]` | what must be true after the step before it |

Fact keys: `lock:<object>` (holds `@detach`), `blocked:<action>` (`sendim`, `startim`, `recvim`, `buy`, `pay`, `fly`, ...), `said:<prim>` (the last line that prim said), `colour:<prim>`, `menu`, `run` (only present when the object does not run), `stopped`, `step:<n>` (step n could not be done). Text after the key must be contained in the fact, in any case. Names cannot contain spaces. `expect not run` proves the object started.

## The driver

Menus close after one press, and a dialog opened in the same instant as the press that caused it counts as closed. To test protocol messages directly, add a test-only script in its own prim (`scripts/<object>/Driver/`) that listens on a private channel to the wearer and turns chat lines into linked messages, for example `say -88 6000|<source id>|sendim=n` becomes `llMessageLinked(LINK_SET, 6000, "sendim=n", <source id>)`. Make it say the results the scripts send, so `expect said:Driver ...` checks refusals. Fake avatar keys such as `00000000-0000-4000-8000-0000000000aa` are enough for other avatars. See `driver/driver.lsl`.

## Writing a scenario

1. Name the behaviour from the code or its specification that the scenario proves.
2. Drive it with the driver or with `touch` and `menu`; check it with `expect` lines on `blocked:`, `lock:` and `said:`.
3. Check both directions: the restriction appears, and it goes away again.
4. Run it, then break the script on purpose (flip one condition) and confirm the scenario fails. A scenario that cannot fail proves nothing.

Use only fake keys and no real account or money; scenarios never contain personal data.

## Running locally

```
sudo apt-get install -y qt6-base-dev qt6-base-dev-tools qt6-tools-dev qt6-l10n-tools libqt6opengl6-dev libgl-dev glslang-tools ninja-build cmake g++
git clone https://github.com/pingledingle-tech/PinglyMotion engine && git -C engine checkout 9d50ec0b060b0be98c9051039337ab70a1e481ca
cmake -S engine -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_NUMBER=0 -DPINGLYMOTION_TESTS=ON
cmake --build build --target pinglymotion_rlvtest
git clone https://github.com/OpenCollarTeam/OpenCollar oc && git -C oc checkout 2500e6a8ebef8b0931cd62fe5daaff321290158d
tools/assemble.sh oc
build/tests/rlvtest/pinglymotion_rlvtest --objects scripts scenarios
```

The runner prints `PASS` or `FAIL` per scenario with the line of every broken expectation, and exits with 1 on any failure.
