# rply_utils

This is a library which essentially wraps [rply](https://rply.readthedocs.io/en/latest/) to make it slightly easier to 
use and write nice code in.

## Usage

`Lexer` and `Parser` are drop-in replacements for the combination of `LexerGenerator`+`Lexer`, and `ParserGenerator`
+`LRParser` (rply's internal class name for a built parser).

### Lexing

If you have the following rply code:

```python
from rply import LexerGenerator

lexer = LexerGenerator()
lexer.add('INT', r'\d+')
lexer.ignore(r'\s')
lexer.build().lex('3')
```

You can change it into the following non-rply code:

```python
from rply_utils import Lexer

lexer = Lexer()
lexer.add('INT', r'\d+')
lexer.ignore(r'\s')
tokens = lexer.build().lex('3')
```

The build call is not necessary, and exists purely to provide the illusion that this is a drop-in replacement. This code
is also equivalent:

```python
from rply_utils import Lexer

lexer = Lexer()
lexer.add('INT', r'\d+')
lexer.ignore(r'\s')
tokens = lexer.lex('3')
```

Another useful method is `add_identity`, which adds a token whose rule is the same as its name.

### Parsing (...after Lexing)

Typically, it is useful to use `lg.rules` or some other data source to get a list of possible tokens. Instead, the
`Lexer` automatically tracks a set of all added tokens, and can be accessed via `lexer.possible_tokens`:

```python
from rply_utils import Lexer, Parser

lexer = Lexer()
lexer.add('INT', r'\d+')
lexer.ignore(r'\s')
tokens = lexer.lex('3')
parser = Parser(lexer.possible_tokens)
```

The parser works exactly the same as it does in rply, with a few added features:

- `parser.empty_production(rule)`, which creates a production that has no function body. It will always return `None`.
    - You can pass just the name of your symbol instead of the entire rule, and it will be added automatically
    - Using this as a function decorator is not supported at this time
- Exceptions are caught and turned into slightly more useful ones. 
    - `ParserTokensExhaustedException` fires when you have run out of tokens before your production rules can match an
        entire string. This can occur if your production rules are simply wrong, your lexer is missing tokens that you
        were expecting, or perhaps you accidentally iterated over the lexer result before turning it into a list or 
        sending it to the parser, 
    - `ParserException` raises when your (optionally-defined) `@parser.error` handler does not raise an exception. It
        simply prints the token which caused the exception, and generally means that the token does not fit into any
        entire production rule.
    - `LexerException` raises when your lexer fails to lex -- this is almost always because you ran into an unexpected
        character, meaning your regex is incorrect and didn't match that character, or perhaps the input string is
        invalid and you don't have a catch-all token in your lexer (which is fine, but be aware it will raise this 
        exception in that case).
        
## Installation

This isn't an officially supported package, it's pretty much just a project for making my compilers class easier.

As a result, you'll need to drop this package into wherever you want to use it. `__init__.py` also needs to be populated