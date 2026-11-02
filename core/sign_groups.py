"""Build isolated group sign-in reports from live platform membership."""
import asyncio


async def group_sign_destinations(context, users, records, groups, heading, diagnostics=None):
    destinations = []
    seen = set()
    for group in groups:
        umo = str(group.get("umo") or "")
        parts = umo.split(":", 2)
        session_group = parts[2].rsplit("_", 1)[-1] if len(parts) == 3 else ""
        group_id = str(group.get("group_id") or session_group)
        diagnostic = {"group_id": group_id}
        if diagnostics is not None:
            diagnostics.append(diagnostic)
        if len(parts) != 3 or parts[1] != "GroupMessage" or not group_id.isdigit() or session_group != group_id or umo in seen:
            diagnostic["reason"] = "invalid_or_duplicate_destination"
            continue
        seen.add(umo)
        try:
            platform = context.get_platform_inst(parts[0])
            bot = getattr(platform, "bot", None)
            if not callable(getattr(bot, "call_action", None)):
                diagnostic["reason"] = "platform_unavailable"
                continue
            members = await asyncio.wait_for(
                bot.call_action("get_group_member_list", group_id=int(group_id), no_cache=True),
                timeout=15,
            )
            if not isinstance(members, list) or any(not isinstance(m, dict) or not str(m.get("user_id") or "").isdigit() for m in members):
                diagnostic["reason"] = "invalid_member_response"
                continue
            member_ids = {str(m["user_id"]) for m in members}
        except Exception as exc:
            diagnostic.update(reason="membership_query_failed", error_type=type(exc).__name__)
            # Membership is unknown, not permission to broadcast everybody's results.
            continue
        lines = [line for key, user in users.items()
                 if str(key) in member_ids and user.get("bindings")
                 for line in records.get(str(key), [])]
        diagnostic.update(member_count=len(member_ids), bound_members=sum(str(key) in member_ids and bool(user.get("bindings")) for key,user in users.items()), record_lines=len(lines), reason="ready" if lines else "no_matching_records")
        if lines:
            title = heading.rstrip() + " · 群 " + group_id
            destinations.append((umo, title + "\n" + "\n".join(lines)))
    return destinations
