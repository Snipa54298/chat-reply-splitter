import unittest
from chat_reply_splitter.experimental.router import split_reply, LanguageRules, register_language

class LanguagesTests(unittest.TestCase):
    def test_english(self):
        self.assertEqual(split_reply("You did a great job! Take a well deserved break.", True, language="en-US"), ["You did a great job!", "Take a well deserved break."])
    def test_japanese(self):
        self.assertEqual(split_reply("今日は本当にお疲れ様！ゆっくり休んでください", True, language="ja"), ["今日は本当にお疲れ様！", "ゆっくり休んでください"])
    def test_arabic_question(self):
        self.assertEqual(split_reply("هل أنت بخير؟ أتمنى لك يوما سعيدا", True, language="ar"), ["هل أنت بخير؟", "أتمنى لك يوما سعيدا"])
    def test_dots(self):
        for text in ["Please ask Dr. Smith about this", "The value is 3.14 and remains unchanged", "Well... perhaps we can wait a little", "Please ask A. Smith about this"]:
            self.assertEqual(split_reply(text, True, language="en"), [text])
    def test_comma_not_forced(self):
        text="If it rains, we can stay indoors, and wait for tomorrow"
        self.assertEqual(split_reply(text, True, language="en"), [text])
    def test_plugin(self):
        rules=LanguageRules("custom", commas="،", periods="۔", questions="؟", short_chars=0)
        register_language(rules)
        text="abcdef ghi۔ jklmnop qrs"
        self.assertEqual(split_reply(text, True, language="custom"), ["abcdef ghi۔", "jklmnop qrs"])
        with self.assertRaises(ValueError): register_language(rules)
    def test_locale_and_no_cross_user_state(self):
        for code in ["en_US", "ja-JP", "ar-EG", "zh-CN"]:
            self.assertEqual(len(split_reply("hello", True, language=code)), 1)
        self.assertEqual(split_reply("晚安，做个好梦。", True), ["晚安，做个好梦"])
    def test_unknown(self):
        with self.assertRaises(ValueError): split_reply("hello", True, language="unknown")
    def test_language_object(self):
        rules=LanguageRules("local", questions="؟", short_chars=0)
        self.assertEqual(split_reply("abcdef؟ ghijkl", True, language=rules), ["abcdef؟", "ghijkl"])
    def test_non_casual_and_long(self):
        text="Hello there! Have a good day."
        self.assertEqual(split_reply(text, language="en"), [text])
        long="Hello there! "*30
        self.assertEqual(split_reply(long, True, language="en"), [long.strip()])

class IsolationTests(unittest.TestCase):
    def test_chinese_same_behavior(self):
        from chat_reply_splitter import split_reply as core
        for text in ["今天真的很开心。谢谢你一直陪我聊天。", "我先去洗澡，晚点再聊，你也早点休息", "他说“明天见”。我也准备早点回家休息了。"]:
            self.assertEqual(split_reply(text, True), core(text, True))
    def test_default_import_does_not_load_experimental(self):
        import subprocess, sys
        subprocess.run([sys.executable, "-c", "import sys; from chat_reply_splitter import split_reply; assert not any(k.startswith('chat_reply_splitter.experimental') for k in sys.modules)"], check=True)
    def test_cannot_override_chinese(self):
        with self.assertRaises(ValueError): register_language(LanguageRules("zh"))
    def test_custom_hook(self):
        class Custom(LanguageRules):
            def split(self, text, casual=False, *, starters=None):
                return [text.upper()]
        self.assertEqual(split_reply("hello", True, language=Custom("demo")), ["HELLO"])
