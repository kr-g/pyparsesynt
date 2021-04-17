from pylexem.lexer import (
    Tokens,
    # token_it,
    Lexer,
    # Plain,
    # NotPlain,
    # InSet,
    # NotInSet,
    # Repeat,
    # OR,
    # AND,
    # OPT,
    # Any,
)


from pylexem.utils import RuleBuilder, Sanitizer

from pyparsesynt.parser import Parser, LexerTokens
from pyparsesynt.writer import Writer

from pyparsesynt.token import Token, TokenStream
from pyparsesynt.rule import Production, Call, Terminal, And, Or, Not, Optional, Repeat


tokens = RuleBuilder().add_all().build()
alltokens = Tokens().extend(tokens)
lexx = Lexer(alltokens, debug=not True, debugtime=True)


inp_text = """
todo
"""

stream = lexx.tokenize(inp_text)
lxtok = LexerTokens(lexx.tokens)

stream = Sanitizer().whitespace(stream)

pars = Parser()
pars.set_input(stream)

p_assign = pars.Production("assignment", Terminal(":=="))


print()
Writer().write(pars.rules)
