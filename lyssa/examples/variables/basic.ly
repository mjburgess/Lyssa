lang = "Lyssa"

@io.p lang;

profession = "Furor"

@io.pf "%s is a %s" lang profession;

msg := "Language is "

msg += lang

test := 1.1
test += 0.9

@io.pf "Language version is %.1f" %version;

@io.p msg;
@io.p $test;

foo =| 1.0, +
foo 1

baz := 1
baz +=
baz 3

fu := 0
fu ~= .+ 10

@io.p | "Foo is " + foo;

greeting =| "Hello %s".f?

greetme  =| greeting "Michael %s"

@io.p | greetme.f "Burgess";

test =| "Testing %s"  .f  ?

test | "This " ++ "is" " a" " test"

fmt = .f
str = "Hello %s"

@io.p | str fmt "michael"