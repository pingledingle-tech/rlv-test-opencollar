// Test driver: chat on channel -88 from the wearer, "<number>|<id>|<message>", is sent as a linked message.
// "@me" in the id or message becomes the wearer's key. Every NOTIFY text the collar sends is said to the wearer.
string withOwner(string text)
{
    return llDumpList2String(llParseStringKeepNulls(text, ["@me"], []), (string)llGetOwner());
}

default
{
    state_entry()
    {
        llListen(-88, "", llGetOwner(), "");
    }

    listen(integer channel, string name, key id, string message)
    {
        list fields = llParseStringKeepNulls(message, ["|"], []);
        llMessageLinked(LINK_SET, (integer)llList2String(fields, 0), withOwner(llDumpList2String(llList2List(fields, 2, -1), "|")), (key)withOwner(llList2String(fields, 1)));
    }

    link_message(integer sender, integer number, string message, key id)
    {
        if (number == 1002)
        {
            llOwnerSay(message);
        }
    }
}
