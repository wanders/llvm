from .base import TestBase
from llvm.core.module import Module
from llvm.core.types import TypeFactory
from llvm.core.builder import Builder
from llvm.core.value import Constant

class comesbefore:
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2

    def eval(self, haystack):
        return self.s1.pos_in(haystack) < self.s2.pos_in(haystack)

    def _in(self, t):
        return self.eval(t)

class literal:
    def __init__(self, s):
        self.s = s
    def comes_before(self, s):
        return comesbefore(self, s)
    def pos_in(self, haystack):
        return haystack.index(self.s)
    def not_in(self, haystack):
        return self.s not in haystack
    def _in(self, haystack):
        return self.s in haystack

class TestBuilder(TestBase):

    def setUp(self):
        self.tfact = TypeFactory()
        self.m = Module('test')

        Ti = self.tfact.int()
        Tf = self.tfact.function(Ti, [Ti, Ti])

        self.f = self.m.add_function(Tf, "borken")
        self.f.args[0].name = "first"
        self.f.args[1].name = "second"

        self.bb = self.f.append_basic_block("entry")
        self.builder = Builder(self.bb)

    def tearDown(self):
        self.tfact = None
        self.m = None
        self.f = None
        self.bb = None
        self.builder = None

    def test_position_before(self):

        r = self.builder.add(self.f.args[0], self.f.args[1])
        self.builder.ret(r)

        self.builder.position_before(r)
        r = self.builder.add(self.f.args[1], self.f.args[0])

        s = self.m.to_assembly()

        # the reversed add should come before:
        assert s.index("%second, %first") < s.index("%first, %second")

        assert literal("%second, %first").comes_before(literal("%first, %second"))._in(s)

    def test_position_at_end(self):
        r = self.builder.add(self.f.args[0], self.f.args[1])

        self.builder.position_before(r)
        r = self.builder.add(self.f.args[1], self.f.args[0])

        self.builder.position_at_end(self.bb)
        self.builder.ret(r)

        s = self.m.to_assembly()

        assert literal("%second, %first").comes_before(literal("ret i32"))._in(s)
        assert literal("%first, %second").comes_before(literal("ret i32"))._in(s)

    def test_position_clear_position(self):
        a = self.builder.add(self.f.args[0], self.f.args[1])

        self.builder.clear_position()
        a2 = self.builder.add(self.f.args[1], self.f.args[0])
        assert a2.basic_block is None

        self.builder.position_at_end(self.bb)
        r = self.builder.ret(a)

        s = self.m.to_assembly()

        assert literal("%second, %first").not_in(s)

        # insert a2 into the builder so we don't leave dangling values..
        self.builder.position_before(r)
        self.builder.insert(a2)

        s = self.m.to_assembly()

        assert literal("%second, %first")._in(s)





    def test_parent_basic_block(self):
        assert self.builder.basic_block is self.bb


    def test_dispose(self):
        builder = Builder(self.bb)

        del builder

        # a bit hard to assert on anything here :(

    def test_insert(self):
        self.builder.clear_position()

        a = self.builder.add(self.f.args[1], self.f.args[0])

        assert a.basic_block is None

        self.builder.position_at_end(self.bb)
        self.builder.insert(a)
        assert a.basic_block is self.bb
        self.builder.ret(a)

        s = self.m.to_assembly()

        assert literal("%second, %first")._in(s)


    def test_instructions(self):
        a = self.builder.add(self.f.args[1], self.f.args[0])
        r = self.builder.ret(a)

        inst = list(self.bb.instructions)
        assert len(inst) == 2
        assert inst[0] is a
        assert inst[1] is r

    def test_phi_simple(self):
        loopbb = self.f.append_basic_block("loop")

        entrybb = self.f.entry

        self.builder.br(loopbb)

        self.builder.position_at_end(loopbb)
        p = self.builder.phi(self.f.args[0].type)
        acc = self.builder.add(p, self.f.args[1], name="acc")
        self.builder.br(loopbb)

        p.add_incoming((self.f.args[0], entrybb),
                       (acc, loopbb))

        assert len(list(p.incoming)) == 2
        assert (acc, loopbb) in p.incoming
        assert (self.f.args[0], entrybb) in p.incoming


    def test_switch(self):
        a = self.builder.add(self.f.args[1], self.f.args[0])

        defbb = self.f.append_basic_block("default")

        sw = self.builder.switch(a, defbb)

        Ti = self.tfact.int()

        self.builder.position_at_end(defbb)
        self.builder.ret(Constant(Ti,10))

        cas1bb = self.f.append_basic_block("case1")
        self.builder.position_at_end(cas1bb)
        self.builder.ret(Constant(Ti,20))

        sw.add_case(Constant(Ti,1), cas1bb)

        s = self.m.to_assembly()
        assert "i32 1, label %case1" in s
        assert "label %default" in s

    def test_tailcall(self):
        a = self.builder.add(self.f.args[1], self.f.args[0], "sum0")

        c = self.builder.call(self.f, [self.f.args[1], a], "selfcall")

        s = self.m.to_assembly()
        assert "%selfcall = call i32 @borken(i32 %second, i32 %sum0)" in s
        assert not c.tailcall

        c.tailcall = True

        s = self.m.to_assembly()
        assert "%selfcall = tail call i32 @borken(i32 %second, i32 %sum0)" in s
        assert c.tailcall

    def test_terminator(self):
        a = self.builder.add(self.f.args[1], self.f.args[0], "sum0")

        assert self.bb.terminator is None

        r = self.builder.ret(a)

        assert self.bb.terminator is r

