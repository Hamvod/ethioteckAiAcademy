import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import learning_bot


class LearningBotTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_database_path = os.environ.get("LANGUAGE_DB_PATH")
        os.environ["LANGUAGE_DB_PATH"] = os.path.join(self.temp_dir.name, "languages.sqlite3")

    async def asyncTearDown(self):
        if self.previous_database_path is None:
            os.environ.pop("LANGUAGE_DB_PATH", None)
        else:
            os.environ["LANGUAGE_DB_PATH"] = self.previous_database_path
        self.temp_dir.cleanup()

    async def test_new_user_start_shows_language_selection_only(self):
        message = SimpleNamespace(reply_text=AsyncMock())
        update = SimpleNamespace(
            effective_user=SimpleNamespace(id=101),
            effective_message=message,
        )
        context = SimpleNamespace(user_data={})

        await learning_bot.start(update, context)

        args, kwargs = message.reply_text.await_args
        self.assertIn("Choose a language", args[0])
        self.assertEqual(len(kwargs["reply_markup"].inline_keyboard), 2)
        self.assertTrue(all("course:" not in row[0].callback_data for row in kwargs["reply_markup"].inline_keyboard))

    async def test_language_selection_persists_and_returning_start_opens_menu(self):
        query = SimpleNamespace(
            data="language:am",
            answer=AsyncMock(),
            edit_message_text=AsyncMock(),
        )
        user = SimpleNamespace(id=202)
        update = SimpleNamespace(callback_query=query, effective_user=user)
        context = SimpleNamespace(user_data={})

        await learning_bot.handle_callback_query(update, context)

        self.assertEqual(learning_bot.get_user_language(user.id), "am")
        self.assertIn("ኮርስ ይምረጡ", query.edit_message_text.await_args.args[0])

        returning_message = SimpleNamespace(reply_text=AsyncMock())
        returning_update = SimpleNamespace(effective_user=user, effective_message=returning_message)
        await learning_bot.start(returning_update, context)

        menu_args, menu_kwargs = returning_message.reply_text.await_args
        self.assertIn("ኮርስ ይምረጡ", menu_args[0])
        self.assertTrue(any(
            button.callback_data == "ai:ask"
            for row in menu_kwargs["reply_markup"].inline_keyboard
            for button in row
        ))

    async def test_ask_ai_callback_receives_question_and_returns_answer(self):
        query = SimpleNamespace(
            data="ai:ask",
            answer=AsyncMock(),
            edit_message_text=AsyncMock(),
        )
        update = SimpleNamespace(
            callback_query=query,
            effective_user=SimpleNamespace(id=303),
        )
        context = SimpleNamespace(user_data={"language": "am"})

        await learning_bot.handle_callback_query(update, context)
        self.assertTrue(context.user_data["awaiting_ai"])

        message = SimpleNamespace(text="ስለ ኔትወርክ ንገረኝ", reply_text=AsyncMock())
        message_update = SimpleNamespace(
            effective_message=message,
            effective_user=update.effective_user,
        )
        with patch.object(learning_bot, "get_ai_response", new=AsyncMock(return_value="ይህ የAI መልስ ነው።")) as ai_call:
            await learning_bot.handle_text_message(message_update, context)

        ai_call.assert_awaited_once_with("ስለ ኔትወርክ ንገረኝ", "am", [])
        self.assertEqual(message.reply_text.await_args.args[0], "ይህ የAI መልስ ነው።")
        self.assertFalse(context.user_data["awaiting_ai"])

    async def test_cancel_exits_ask_ai_mode(self):
        query = SimpleNamespace(
            data="ai:cancel",
            answer=AsyncMock(),
            edit_message_text=AsyncMock(),
        )
        context = SimpleNamespace(user_data={"language": "en", "awaiting_ai": True})
        update = SimpleNamespace(
            callback_query=query,
            effective_user=SimpleNamespace(id=404),
        )

        await learning_bot.handle_callback_query(update, context)

        self.assertFalse(context.user_data["awaiting_ai"])
        self.assertIn("cancelled", query.edit_message_text.await_args.args[0].lower())

    async def test_callback_is_acknowledged_before_data_is_read(self):
        class CallbackQuery:
            def __init__(self):
                self.acknowledged = False
                self.edit_message_text = AsyncMock()

            async def answer(self):
                self.acknowledged = True

            @property
            def data(self):
                if not self.acknowledged:
                    raise AssertionError("callback data read before acknowledgment")
                return "menu:main"

        query = CallbackQuery()
        update = SimpleNamespace(callback_query=query)
        context = SimpleNamespace(user_data={})

        await learning_bot.handle_callback_query(update, context)

        self.assertTrue(query.acknowledged)
        query.edit_message_text.assert_awaited_once()

    async def test_missing_gemini_key_returns_localized_error(self):
        context = SimpleNamespace(user_data={"language": "am", "awaiting_ai": True})
        message = SimpleNamespace(text="ጥያቄ", reply_text=AsyncMock())
        update = SimpleNamespace(
            effective_message=message,
            effective_user=SimpleNamespace(id=505),
        )

        with patch.object(learning_bot, "GEMINI_API_KEY", None):
            await learning_bot.handle_text_message(update, context)

        self.assertIn("ስላልተዋቀረ", message.reply_text.await_args.args[0])
        self.assertNotIn("key", message.reply_text.await_args.args[0].lower())

    async def test_gemini_client_uses_native_sdk_and_selected_language(self):
        response = SimpleNamespace(text="ሰላም")
        client = SimpleNamespace(
            aio=SimpleNamespace(
                models=SimpleNamespace(generate_content=AsyncMock(return_value=response))
            ),
        )
        with patch.object(learning_bot, "GEMINI_API_KEY", "test-key"), patch.object(
            learning_bot.genai, "Client", return_value=client
        ) as client_factory:
            answer = await learning_bot.get_ai_response("ሰላም", "am")

        self.assertEqual(answer, "ሰላም")
        request = client.aio.models.generate_content.await_args.kwargs
        self.assertEqual(request["model"], "gemini-3.8-flash")
        self.assertIn("Amharic", request["config"].system_instruction)
        self.assertEqual(request["contents"][0].role, "user")
        self.assertEqual(request["contents"][0].parts[0].text, "ሰላም")
        client_factory.assert_called_once_with(api_key="test-key")

    def test_main_registers_callback_and_text_handlers(self):
        app = SimpleNamespace(add_handler=Mock(), add_error_handler=Mock(), run_polling=Mock())
        builder = SimpleNamespace(token=Mock(return_value=None), build=Mock(return_value=app))
        builder.token.return_value = builder
        with patch.object(learning_bot, "BOT_TOKEN", "test-token"), patch.object(
            learning_bot, "ApplicationBuilder", return_value=builder
        ):
            learning_bot.main()

        registered_handlers = [call.args[0] for call in app.add_handler.call_args_list]
        self.assertTrue(any(isinstance(handler, learning_bot.CallbackQueryHandler) for handler in registered_handlers))
        self.assertTrue(any(isinstance(handler, learning_bot.MessageHandler) for handler in registered_handlers))
        self.assertEqual(len([handler for handler in registered_handlers if isinstance(handler, learning_bot.CommandHandler)]), 2)
        app.add_error_handler.assert_called_once_with(learning_bot.error_handler)


if __name__ == "__main__":
    unittest.main()