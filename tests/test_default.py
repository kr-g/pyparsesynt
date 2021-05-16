import unittest
import random

from pylexem.lexer import (
    Tokens,
    token_it,
    Lexer,
    Plain,
    NotPlain,
    InSet,
    NotInSet,
    Repeat,
    OR,
    AND,
    OPT,
    Any,
)
from pylexem.utils import RuleBuilder, Sanitizer

from pyparsesynt.parser import Parser, LexerTokens, NoSolution
from pyparsesynt.writer import Writer
from pyparsesynt.repr import ReprBase

from pyparsesynt.token import Token, TokenStream
from pyparsesynt.rule import Production, Call, Terminal, And, Or, Not, Optional, Repeat
from pyparsesynt.syn import Element


class ParserDefaultTestCase(unittest.TestCase):
    def setUp(self):
        tokens = RuleBuilder().add_all().build()
        alltokens = Tokens().extend(tokens)
        self.lexx = Lexer(alltokens, debug=False, debugtime=False)
        self.lxtok = LexerTokens(self.lexx.tokens)

    def tearDown(self):
        pass

    def test_default(self):
        self.assertTrue(True)

    def token_parse_text(self, inp_text):
        stream = self.lexx.tokenize(inp_text)
        self.lxtok = LexerTokens(self.lexx.tokens)
        stream = list(Sanitizer().whitespace(stream, keep=[]))
        pars = Parser()
        pars.set_input(stream)
        return pars

    def flatten(self, elem):
        if type(elem) == Element:
            if val := elem.get_head():
                yield val
            for chld in elem.get_tail():
                yield from self.flatten(chld)
        else:
            yield elem

    def get_flat(self, elem):
        # todo ?
        # rework as hierarchy test
        return list(self.flatten(elem))

    def test_number(self):
        pars = self.token_parse_text("1")

        p_number = pars.Production(
            "number", Or([Terminal(str(x)) for x in range(0, 10)])
        )

        root = pars.run()
        self.assertIsNotNone(root)

    def test_no_number(self):
        pars = self.token_parse_text("1a")

        p_number = pars.Production(
            "number", Or([Terminal(str(x)) for x in range(0, 10)])
        )

        self.assertRaises(NoSolution, pars.run)

    def test_many_number(self):
        pars = self.token_parse_text("1 2 3 4")

        p_number = pars.Production(
            "number", Or([Terminal(str(x)) for x in range(0, 10)])
        )

        root = pars.run()
        self.assertIsNotNone(root)

        for e in root.get_tail():
            self.assertEqual(e.get_head(), "number")

    def test_simple_sequence(self):
        pars = self.token_parse_text("this is 1 first test 2 3 4")

        p_number = pars.Production(
            "number", Or([Terminal(str(x)) for x in range(0, 10)])
        )

        p_words = pars.Production("words", Repeat(Terminal(typ=self.lxtok.WORD)))

        root = pars.run()
        self.assertIsNotNone(root)

        self.assertEqual(
            self.get_flat(root),
            [
                "---root---",
                "words",
                ("this", "WORD"),
                ("is", "WORD"),
                "number",
                ("1", "UINT"),
                "words",
                ("first", "WORD"),
                ("test", "WORD"),
                "number",
                ("2", "UINT"),
                "number",
                ("3", "UINT"),
                "number",
                ("4", "UINT"),
            ],
        )

    def test_simple_repeat_sequence(self):
        pars = self.token_parse_text("this is 1 first test 2 3 4 only three words")

        p_number = pars.Production(
            "number", Or([Terminal(str(x)) for x in range(0, 10)])
        )

        p_words = pars.Production("words", Repeat(Terminal(typ=self.lxtok.WORD)))

        p_words_numbers = pars.Production(
            "words_numbers",
            And([pars.Call(p_words), Repeat(pars.Call(p_number))]),
        )

        root = pars.run()
        self.assertIsNotNone(root)

        self.assertEqual(
            self.get_flat(root),
            [
                "---root---",
                "words_numbers",
                "words",
                ("this", "WORD"),
                ("is", "WORD"),
                "*number",
                "number",
                ("1", "UINT"),
                "words_numbers",
                "words",
                ("first", "WORD"),
                ("test", "WORD"),
                "*number",
                "number",
                ("2", "UINT"),
                "number",
                ("3", "UINT"),
                "number",
                ("4", "UINT"),
                "words",
                ("only", "WORD"),
                ("three", "WORD"),
                ("words", "WORD"),
            ],
        )

    def test_opt_minus_number(self):
        pars = self.token_parse_text("1 - 2 3 4")

        p_minus = pars.Production("minus", Terminal(typ=self.lxtok.MINUS))

        p_number = pars.Production(
            "number", Or([Terminal(str(x)) for x in range(0, 10)])
        )

        p_opt_minus_number = pars.Production(
            "opt_minus_number", And([Optional(p_minus), pars.Call(p_number)])
        )

        root = pars.run()
        self.assertIsNotNone(root)

        self.assertEqual(
            self.get_flat(root),
            [
                "---root---",
                "number",
                ("1", "UINT"),
                "opt_minus_number",
                "minus",
                ("-", "MINUS"),
                "number",
                ("2", "UINT"),
                "number",
                ("3", "UINT"),
                "number",
                ("4", "UINT"),
            ],
        )

    def test_opt_minus_or_plus_number(self):
        pars = self.token_parse_text("1 - 2 3 + 4 5")

        p_minus = pars.Production("minus", Terminal(typ=self.lxtok.MINUS))
        p_plus = pars.Production("plus", Terminal(typ=self.lxtok.PLUS))

        p_number = pars.Production(
            "number", Or([Terminal(str(x)) for x in range(0, 10)])
        )

        p_opt_minus_number = pars.Production(
            "opt_minus_plus_number",
            And([Optional(Or([p_minus, p_plus])), pars.Call(p_number)]),
        )

        root = pars.run()
        self.assertIsNotNone(root)

        self.assertEqual(
            self.get_flat(root),
            [
                "---root---",
                "number",
                ("1", "UINT"),
                "opt_minus_plus_number",
                "minus",
                ("-", "MINUS"),
                "number",
                ("2", "UINT"),
                "number",
                ("3", "UINT"),
                "opt_minus_plus_number",
                "plus",
                ("+", "PLUS"),
                "number",
                ("4", "UINT"),
                "number",
                ("5", "UINT"),
            ],
        )

    def test_opt_repeat_minus_or_plus_number(self):
        pars = self.token_parse_text("1 - 2 3 + - 4 5")

        p_minus = pars.Production("minus", Terminal(typ=self.lxtok.MINUS))
        p_plus = pars.Production("plus", Terminal(typ=self.lxtok.PLUS))

        p_number = pars.Production(
            "number", Or([Terminal(str(x)) for x in range(0, 10)])
        )

        p_opt_minus_number = pars.Production(
            "opt_repeat_minus_plus_number",
            And(
                [
                    Optional(Repeat(Or([p_minus, p_plus]), name="opt_sign")),
                    pars.Call(p_number),
                ]
            ),
        )

        root = pars.run()
        self.assertIsNotNone(root)

        self.assertEqual(
            self.get_flat(root),
            [
                "---root---",
                "number",
                ("1", "UINT"),
                "opt_repeat_minus_plus_number",
                "*opt_sign",
                "minus",
                ("-", "MINUS"),
                "number",
                ("2", "UINT"),
                "number",
                ("3", "UINT"),
                "opt_repeat_minus_plus_number",
                "*opt_sign",
                "plus",
                ("+", "PLUS"),
                "minus",
                ("-", "MINUS"),
                "number",
                ("4", "UINT"),
                "number",
                ("5", "UINT"),
            ],
        )
