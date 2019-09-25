#!/usr/bin/python

# Copyright 2003 Dave Abrahams
# Copyright 2002, 2003, 2005, 2006 Vladimir Prus
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import BoostBuild


def test_basic():
    t = BoostBuild.Tester(["-d3", "-d+12"], pass_d0=False, use_test_config=False)

    t.write("a.cpp", """
#include <a.h>
# include "a.h"
#include <x.h>
int main() {}
""")
    t.write("a.h", "\n")
    t.write("a_c.c", """\
#include <a.h>
# include "a.h"
#include <x.h>
""")
    t.write("b.cpp", """\
#include "a.h"
int main() {}
""")
    t.write("b.h", "\n")
    t.write("c.cpp", """\
#include "x.h"
int main() {}
""")
    t.write("e.cpp", """\
#include "x.h"
int main() {}
""")
    t.write("x.foo", "")
    t.write("y.foo", "")

    t.write("src1/a.h", '#include "b.h"\n')
    t.write("src1/b.h", '#include "c.h"\n')
    t.write("src1/c.h", "\n")
    t.write("src1/z.h", """\
extern int dummy_variable_suppressing_empty_file_warning_on_hp_cxx_compiler;
""")

    t.write("src2/b.h", "\n")

    t.write("jamroot.jam", """\
import foo ;
import types/cpp ;
import types/exe ;

project test : requirements <include>src1 ;

exe a : x.foo a.cpp a_c.c ;
exe b : b.cpp ;

# Because of <define>FOO, c.cpp will be compiled to a different directory than
# everything for main target "a". Therefore, without <implicit-dependency>, C
# preprocessor processing that module will not find "x.h", which is part of
# "a"'s dependency graph.
#
# --------------------------
# More detailed explanation:
# --------------------------
#   c.cpp includes x.h which does not exist on the current include path so Boost
# Jam will try to match it to existing Jam targets to cover cases as this one
# where the file is generated by the same build.
#
#   However, as x.h is not part of "c" metatarget's dependency graph, Boost
# Build will not actualize its target by default, i.e. create its Jam target.
#
#   To get the Jam target created in time, we use the <implicit-dependency>
# feature. This tells Boost Build that it needs to actualize the dependency
# graph for metatarget "a", even though that metatarget has not been directly
# mentioned and is not a dependency for any of the metatargets mentioned in the
# current build request.
#
#   Note that Boost Build does not automatically add a dependency between the
# Jam targets in question so, if Boost Jam does not add a dependency on a target
# from that other dependency graph (x.h in our case), i.e. if c.cpp does not
# actually include x.h, us actualizing it will have no effect in the end as
# Boost Jam will not have a reason to actually build those targets in spite of
# knowing about them.
exe c : c.cpp : <define>FOO <implicit-dependency>a ;
""")

    t.write("foo.jam", """\
import generators ;
import modules ;
import os ;
import print ;
import type ;
import types/cpp ;

type.register FOO : foo ;

generators.register-standard foo.foo : FOO : CPP H ;

nl = "
" ;

rule foo ( targets * : sources * : properties * )
{
    # On NT, you need an exported symbol in order to have an import library
    # generated. We will not really use the symbol defined here, just force the
    # import library creation.
    if ( [ os.name ] = NT || [ modules.peek : OS ] in CYGWIN ) &&
        <main-target-type>LIB in $(properties)
    {
        .decl = "void __declspec(dllexport) foo() {}" ;
    }
    print.output $(<[1]) ;
    print.text $(.decl:E="//")$(nl) ;
    print.output $(<[2]) ;
    print.text "#include <z.h>"$(nl) ;
}
""")

    t.write("foo.py",
r"""import bjam
import b2.build.type as type
import b2.build.generators as generators

from b2.manager import get_manager

type.register("FOO", ["foo"])
generators.register_standard("foo.foo", ["FOO"], ["CPP", "H"])

def prepare_foo(targets, sources, properties):
    if properties.get('os') in ['windows', 'cygwin']:
        bjam.call('set-target-variable', targets, "DECL",
            "void __declspec(dllexport) foo() {}")

get_manager().engine().register_action("foo.foo",
    "echo -e $(DECL:E=//)\\n > $(<[1])\n"
    "echo -e "#include <z.h>\\n" > $(<[2])\n", function=prepare_foo)
""")

    # Check that main target 'c' was able to find 'x.h' from 'a's dependency
    # graph.
    t.run_build_system()
    t.expect_addition("bin/$toolset/debug*/c.exe")

    # Check handling of first level includes.

    # Both 'a' and 'b' include "a.h" and should be updated.
    t.touch("a.h")
    t.run_build_system()

    t.expect_touch("bin/$toolset/debug*/a.exe")
    t.expect_touch("bin/$toolset/debug*/a.obj")
    t.expect_touch("bin/$toolset/debug*/a_c.obj")
    t.expect_touch("bin/$toolset/debug*/b.exe")
    t.expect_touch("bin/$toolset/debug*/b.obj")
    t.expect_nothing_more()

    # Only source files using include <a.h> should be compiled.
    t.touch("src1/a.h")
    t.run_build_system()

    t.expect_touch("bin/$toolset/debug*/a.exe")
    t.expect_touch("bin/$toolset/debug*/a.obj")
    t.expect_touch("bin/$toolset/debug*/a_c.obj")
    t.expect_nothing_more()

    # "src/a.h" includes "b.h" (in the same dir).
    t.touch("src1/b.h")
    t.run_build_system()
    t.expect_touch("bin/$toolset/debug*/a.exe")
    t.expect_touch("bin/$toolset/debug*/a.obj")
    t.expect_touch("bin/$toolset/debug*/a_c.obj")
    t.expect_nothing_more()

    # Included by "src/b.h". We had a bug: file included using double quotes
    # (e.g. "b.h") was not scanned at all in this case.
    t.touch("src1/c.h")
    t.run_build_system()
    t.expect_touch("bin/$toolset/debug*/a.exe")

    t.touch("b.h")
    t.run_build_system()
    t.expect_nothing_more()

    # Test dependency on a generated header.
    #
    # TODO: we have also to check that generated header is found correctly if
    # it is different for different subvariants. Lacking any toolset support,
    # this check will be implemented later.
    t.touch("x.foo")
    t.run_build_system()
    t.expect_touch("bin/$toolset/debug*/a.obj")
    t.expect_touch("bin/$toolset/debug*/a_c.obj")

    # Check that generated headers are scanned for dependencies as well.
    t.touch("src1/z.h")
    t.run_build_system()
    t.expect_touch("bin/$toolset/debug*/a.obj")
    t.expect_touch("bin/$toolset/debug*/a_c.obj")

    t.cleanup()


def test_scanned_includes_with_absolute_paths():
    """
      Regression test: on Windows, <includes> with absolute paths were not
    considered when scanning dependencies.

    """
    t = BoostBuild.Tester(["-d3", "-d+12"], pass_d0=False)

    t.write("jamroot.jam", """\
path-constant TOP : . ;
exe app : main.cpp : <include>$(TOP)/include ;
""");

    t.write("main.cpp", """\
#include <dir/header.h>
int main() {}
""")

    t.write("include/dir/header.h", "\n")

    t.run_build_system()
    t.expect_addition("bin/$toolset/debug*/main.obj")

    t.touch("include/dir/header.h")
    t.run_build_system()
    t.expect_touch("bin/$toolset/debug*/main.obj")

    t.cleanup()


test_basic()
test_scanned_includes_with_absolute_paths()
