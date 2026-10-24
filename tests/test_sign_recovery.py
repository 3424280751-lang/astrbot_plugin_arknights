import ast
import asyncio
import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo


def load_sign_methods():
    source = Path(__file__).parents[1] / "main.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    methods = []
    wanted = {
        "_sign_journal_path",
        "_read_sign_journal",
        "_write_sign_journal",
        "_auto_sign_job",
        "_recover_sign_job",
    }
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in wanted
        ):
            methods.append(node)

    async def no_wait(_):
        return None

    namespace = {
        "Path": Path,
        "datetime": datetime,
        "ZoneInfo": ZoneInfo,
        "json": json,
        "asyncio": SimpleNamespace(sleep=no_wait),
        "random": SimpleNamespace(random=lambda: 0),
        "logger": SimpleNamespace(info=lambda *a: None, warning=lambda *a: None),
    }
    exec(
        compile(
            ast.fix_missing_locations(ast.Module(body=methods, type_ignores=[])),
            str(source),
            "exec",
        ),
        namespace,
    )
    return namespace


def test_recovery_persists_results_and_retries_only_failed_delivery(tmp_path):
    methods = load_sign_methods()

    class Harness:
        def __init__(self):
            self._sign_lock = asyncio.Lock()
            self.store = SimpleNamespace(
                _resolve_path=lambda: tmp_path / "users.json",
                all_users=self.users,
                list_sign_groups=self.groups,
            )
            self.calls = 0
            self.sent = []
            self.fail = True

        async def users(self):
            return {"owner": {"bindings": [{"nick_name": "Doctor"}]}}

        async def groups(self):
            return [{"umo": "group-a"}, {"umo": "group-b"}]

        async def _sign_in_user(self, key, user):
            self.calls += 1
            return [(user["bindings"][0], "success")]

        def _sign_line(self, binding, result):
            return "Doctor: signed"

        async def _notify(self, target, text):
            if target == "group-b" and self.fail:
                return False
            self.sent.append(target)
            return True

    for name, method in methods.items():
        if name.startswith("_sign_") or name in {
            "_read_sign_journal",
            "_write_sign_journal",
            "_auto_sign_job",
            "_recover_sign_job",
        }:
            setattr(Harness, name, method)

    async def scenario():
        first = Harness()
        await first._auto_sign_job()
        assert first.calls == 1 and first.sent == ["group-a"]
        second = Harness()
        second.fail = False
        await second._auto_sign_job()
        assert second.calls == 0 and second.sent == ["group-b"]
        await second._auto_sign_job()
        assert second.calls == 0 and second.sent == ["group-b"]

    asyncio.run(scenario())
