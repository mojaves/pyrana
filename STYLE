Pyrana coding style guidelines
===============================

In a nutshell:
* PEP8 guidelines applies for python code,
* PEP7 applies for C code.

A few notes about local extensions/addendum to the PEPs above follows.

PEP7 addendum
-------------

* internal (private) functions: 
  MixedCase()

* ...unless they implement operations on a type:
  MyType_DoSomething()
  But remember to OMIT the Pyr prefix!

* brace positioning:
  enum {
      FOO,
      BAR
  };

  struct FooBar {
  };

  rule of thumb to cover 90%+ of the cases: braces deserve to be on a
  separate line only in functions.

* docstrings: SomeThing__doc__ (append __doc__ suffix)
  always right above the thing they document.

* naming of variables (and parameters):
  separated_with_underscore_if_needed
  abbreviations are fine as long as they are common enough
  (fmt, buf, len, pkt, pts, kwd(s) ...)

* globals:
  avoid as much as is possible. Prefix with g_.
  Make them static. Never export a global.

* Type attribute data (as buffer, get/set list)
  they are both variables and part of a Type definition, so
  MyType_some_thing

* Type Objects:
  MyTypeObject. As done in the CPython sources.

* no vertical alignement (borrowed from PEP8)

