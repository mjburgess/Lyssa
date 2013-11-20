import re
import onto


def tokenize(cls):
    return lambda scanner, token: cls(token, True)

def ignore():
    return lambda s, t: None

def lexFile(file):
    return lex(open(file).read())

def lex(src):
    scanner = re.Scanner([
        (r"#[^\n]+\n+", ignore()),
        (r"\|", tokenize(onto.Pipe)),
        (r"`", tokenize(onto.Lambda)),
        (r"->", tokenize(onto.Quote)),
        (r"{", tokenize(onto.BlockQuote)),
        (r"}", tokenize(onto.BlockUnquote)),
        (r"#:[^\n]+", tokenize(onto.Commentation)),
        (r"-?[0-9]+\.[0-9]+([eE]-?[0-9]+)?", tokenize(onto.Float)),
        (r"-?[0-9]+", tokenize(onto.Integer)),
        (r"@\w+", tokenize(onto.Action)),
        (r"%\w+", tokenize(onto.Constant)),
        (r"[A-Z]\w+", tokenize(onto.TypeValue)),
        (r'"[^"]*"', tokenize(onto.String)),
        (r"\n\n\n+", tokenize(onto.Discard)),
        (r"\n\n?", tokenize(onto.Termination)),
        (r"\,", tokenize(onto.Termination)),
        (r";", tokenize(onto.Force)),
        (r"\.\w+", tokenize(onto.Atom)),
        (r"\.[:~]?[/*-+=><!]+", tokenize(onto.Symbol)),
        (r"\w+", tokenize(onto.Value)),
        (r"[:~]?[/*-+=><!]+", tokenize(onto.Operator)),
        (r"\$\w+", tokenize(onto.StringyValue)),
        (r"\?", tokenize(onto.Operator)),
        (r"\s+", ignore())
    ])

    return scanner.scan(src)[0]

