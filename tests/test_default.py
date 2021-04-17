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

from pyparsesynt.parser import Parser, LexerTokens, ParserCallback
from pyparsesynt.writer import Writer
from pyparsesynt.repr import ReprBase

from pyparsesynt.token import Token, TokenStream
from pyparsesynt.rule import Production, Call, Terminal, And, Or, Not, Optional, Repeat


class ParserDefaultTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default(self):
        self.assertTrue(True)
