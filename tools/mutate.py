#!/usr/bin/env python3
"""Mutation test for the scenarios: change one thing in a collar script, run the scenarios, and expect them to FAIL.

Usage: tools/mutate.py <OpenCollar checkout> <runner binary> [--check] [--strict]
  --check   only verify that every mutation matches exactly once in the source (no runner needed)
  --strict  exit 1 when a mutant survives (the scenarios did not notice the change)
A killed mutant is good. A surviving mutant is a hole in the scenarios, or a change that does not matter.
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# name, script, old text (must occur exactly once), new text
MUTANTS = [
    # linked message numbers
    ("rlv_cmd_number", "oc_rlvsys", "integer RLV_CMD = 6000;", "integer RLV_CMD = 6001;"),
    ("safeword_number", "oc_rlvsys", "integer CMD_SAFEWORD = 510;", "integer CMD_SAFEWORD = 511;"),
    ("override_number", "oc_rlvsys", "integer RLV_CMD_OVERRIDE=6010;", "integer RLV_CMD_OVERRIDE=6011;"),
    # sending a restriction and lifting it
    ("add_sends_release", "oc_rlvsys", 'llOwnerSay("@"+sBehav+"=n");', 'llOwnerSay("@"+sBehav+"=y");'),
    ("remove_sends_restrict", "oc_rlvsys", 'llOwnerSay("@"+sBehav+"=y"); //remove restriction', 'llOwnerSay("@"+sBehav+"=n"); //remove restriction'),
    ("other_source_ignored", "oc_rlvsys", "if (llListFindList(lSrcRestr, [sBehav])!=-1) return;", "if (llListFindList(lSrcRestr, [sBehav])!=-1) {}"),
    # permissions
    ("owner_not_allowed", "oc_rlvsys", "iNum >= CMD_OWNER) UserCommand", "iNum > CMD_OWNER) UserCommand"),
    # safeword and on/off
    ("safeword_ignored", "oc_rlvsys", 'else if (iNum == CMD_SAFEWORD) SafeWord("");', "else if (iNum == CMD_SAFEWORD) {}"),
    ("off_flag_wrong", "oc_rlvsys", "g_iRLVOff = !g_iRLVOn;", "g_iRLVOff = g_iRLVOn;"),
    ("reactivate_releases", "oc_rlvsys", 'llOwnerSay("@"+llList2String(g_lBaked,numBaked)+"=n");', 'llOwnerSay("@"+llList2String(g_lBaked,numBaked)+"=y");'),
    ("detach_relock_missing", "oc_rlvsys", 'if(sBehav=="detach" && g_iCollarLocked == TRUE) llOwnerSay("@detach=n");', "{}"),
]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args or ("--check" not in flags and len(args) < 2):
        print(__doc__)
        return 2
    oc = os.path.abspath(args[0])
    bad = 0
    for name, script, old, new in MUTANTS:
        n = read(os.path.join(oc, "src", "collar", script + ".lsl")).count(old)
        if n != 1:
            print("INVALID  %s: the old text occurs %d times, not once" % (name, n))
            bad += 1
    if "--check" in flags:
        print("%d mutations, %d invalid" % (len(MUTANTS), bad))
        return 1 if bad else 0
    if bad:
        return 2
    runner = os.path.abspath(args[1])
    survived = []
    for name, script, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "src"))
            shutil.copytree(os.path.join(oc, "src", "collar"), os.path.join(tmp, "src", "collar"))
            path = os.path.join(tmp, "src", "collar", script + ".lsl")
            with open(path, "w", encoding="utf-8") as f:
                f.write(read(path).replace(old, new))
            subprocess.run([os.path.join(HERE, "assemble.sh"), tmp], check=True, stdout=subprocess.DEVNULL)
            env = {k: v for k, v in os.environ.items() if k not in ("DISPLAY", "QT_QPA_PLATFORM", "WAYLAND_DISPLAY")}
            r = subprocess.run([runner, "--objects", os.path.join(ROOT, "scripts"), os.path.join(ROOT, "scenarios")],
                               cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if r.returncode == 0:
            print("SURVIVED %s" % name)
            survived.append(name)
        else:
            print("killed   %s" % name)
    # restore the unchanged object so a later run starts clean
    subprocess.run([os.path.join(HERE, "assemble.sh"), oc], check=True, stdout=subprocess.DEVNULL)
    print("%d of %d mutants killed" % (len(MUTANTS) - len(survived), len(MUTANTS)))
    return 1 if survived and "--strict" in flags else 0


if __name__ == "__main__":
    sys.exit(main())
