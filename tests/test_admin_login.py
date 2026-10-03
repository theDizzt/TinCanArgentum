"""Offline regression checks; no Discord connection or real credentials needed."""

import ast
import json
import logging
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from fcts import admin_config


class AdminLoginTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "admin.json"
        patcher = patch.object(admin_config, "ADMIN_CONFIG_PATH", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)
        # Execute the actual command bodies without importing database/image cogs.
        source = Path(__file__).resolve().parents[1] / "cogs" / "Admins.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        cog = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Admins")
        methods = [n for n in cog.body if isinstance(n, ast.AsyncFunctionDef)
                   and n.name in {"login", "logout"}]
        for method in methods:
            method.decorator_list = []
        self.session = []
        self.ns = {
            "load_admins": admin_config.load_admins,
            "ADMIN_CONFIG_PATH": self.path,
            "logger": logging.getLogger("admin_login_test"),
            "admin_login": self.session,
            "discord": SimpleNamespace(HTTPException=RuntimeError),
            "i18n": SimpleNamespace(t=lambda user, key, **kwargs: key),
        }
        exec(compile(ast.Module(body=methods, type_ignores=[]), str(source), "exec"), self.ns)
        self.ctx = SimpleNamespace(author=SimpleNamespace(id=123), prefix=";",
                                   message=SimpleNamespace(delete=AsyncMock()), send=AsyncMock())

    def configure(self, password="002"):
        self.path.write_text(json.dumps({"UID123": {"id": "001", "pw": password}}),
                             encoding="utf-8-sig")

    async def login(self, sid="001", spw="002"):
        await self.ns["login"](None, self.ctx, sid, spw)

    async def test_file_added_after_missing_and_updated_without_restart(self):
        with self.assertLogs("admin_login_test", level="WARNING"):
            await self.login()
        self.assertEqual(self.session, [])
        self.configure()
        await self.login()
        self.assertEqual(self.session, [123])
        self.session.clear()
        self.configure("new-password")
        await self.login()
        self.assertEqual(self.session, [])
        await self.login(spw="new-password")
        self.assertEqual(self.session, [123])

    async def test_repeat_login_and_logout(self):
        self.configure()
        await self.login()
        await self.login()
        self.assertEqual(self.session, [123])
        await self.ns["logout"](None, self.ctx)
        self.assertEqual(self.session, [])

    async def test_unknown_user_wrong_password_and_missing_arguments(self):
        self.configure()
        await self.login(spw="wrong")
        self.ctx.send.assert_awaited_with("cmd.89.error")
        self.ctx.author.id = 456
        await self.login()
        self.ctx.send.assert_awaited_with("cmd.89.reject")
        await self.login(sid=None, spw=None)
        self.assertIn(";login", self.ctx.send.call_args.args[0])
        self.assertEqual(self.session, [])

    async def test_invalid_files_fail_closed_without_logging_credentials(self):
        for content in ('{secret', '[]', '{"UID123":{"id":1,"pw":"secret"}}'):
            self.path.write_text(content, encoding="utf-8")
            with self.assertLogs("admin_login_test", level="WARNING") as logs:
                await self.login()
            self.assertNotIn("secret", " ".join(logs.output))
            self.assertEqual(self.session, [])

    async def test_message_delete_failure_does_not_block_login(self):
        self.configure()
        self.ctx.message.delete.side_effect = RuntimeError
        await self.login()
        self.assertEqual(self.session, [123])


if __name__ == "__main__":
    unittest.main()
