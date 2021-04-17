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

tokens = RuleBuilder().add_all().build()
alltokens = Tokens().extend(tokens)
lexx = Lexer(alltokens, debug=not True, debugtime=True)


inp_text = """1 0 - + 7 seven - 1 4 + 5 + 6 six"""
# inp_text = """+ 1 0 - + 7 seven """

stream = lexx.tokenize(inp_text)
lxtok = LexerTokens(lexx.tokens)

stream = list(Sanitizer().whitespace(stream, keep=[]))

pars = Parser()
pars.set_input(stream)

# p_assign = pars.Production("assignment", Terminal(":=="))

p_minus = pars.Production("minus", Terminal("-"))
p_plus = pars.Production("plus", Terminal(typ=lxtok.PLUS))

p_zahl_ohne_null_5 = pars.Production(
    "zahl_ohne_null", Or([Terminal(str(x)) for x in range(1, 5)]), alias="lower_5"
)

p_zahl_ohne_null_10 = pars.Production(
    "zahl_ohne_null", Or([Terminal(str(x)) for x in range(5, 10)]), alias="higher_5"
)

p_zahl = pars.Production(
    "zahl",
    Or(
        [
            Terminal(str(0)),
            pars.Call(p_zahl_ohne_null_5),
        ]
    ),
)

p_int = pars.Production(
    "int",
    And(
        [
            Optional(
                Or(
                    [
                        pars.Call(p_minus),
                        pars.Call(p_plus),
                    ]
                )
            ),
            # Repeat(Terminal(typ=lxtok.UINT), min_val=1),
            Repeat(pars.Call("zahl_ohne_null"), min_val=1),
            # pars.Call("zahl_ohne_null"),
            # pars.Call("int")
        ]
    ),
)

p_number_word = pars.Production(
    "number_word",
    And(
        [
            Optional(Or([Terminal(typ=lxtok.PLUS), Terminal(typ=lxtok.MINUS)])),
            Repeat(pars.Call("zahl_ohne_null"), min_val=1),
            # pars.Call("zahl_ohne_null"),
            Terminal(typ=lxtok.WORD),
            # pars.Call("int")
        ]
    ),
)


class ParserProduction(ParserCallback):
    def prod_lower_5(self):
        print("prod_lower_5 alias for prod_zahl_ohne_null", self.tokens())
        self.h("prod_lower_5")
        self.col()

    def prod_zahl_ohne_null(self):
        print("prod_zahl_ohne_null", self.tokens())
        self.h("prod_zahl_ohne_null")
        self.col()

    def prod_zahl(self):
        print("prod_zahl", self.tokens())
        self.h("prod_zahl")
        self.col()

    def prod_int(self):
        print("prod_int", self.tokens())
        self.h("prod_int")
        self.coll()

    def prod_number_word(self):
        print("prod_number_word", self.tokens())
        self.h("number_word")
        self.coll()

    def prod_minus(self):
        print("prod_int", self.tokens())
        self.h("prod_minus")
        self.col()


#

pars.callb = ParserProduction()

print()
Writer().write(pars.rules)

root = pars.run()

print(root)
