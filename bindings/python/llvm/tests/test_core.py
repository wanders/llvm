from .base import TestBase
from llvm.core import OpCode
from llvm.core.memorybuffer import MemoryBuffer
from llvm.core import PassRegistry
from llvm.core import Context
from llvm.core import Module

class TestCore(TestBase):
    def test_opcode(self):
        self.assertTrue(hasattr(OpCode, 'Ret'))
        self.assertTrue(isinstance(OpCode.Ret, OpCode))
        self.assertEqual(OpCode.Ret, 1)

        op = OpCode(1)
        self.assertTrue(isinstance(op, OpCode))
        self.assertEqual(op, OpCode.Ret)
        self.assertEqual(str(op), 'OpCode.Ret(1)')

    def test_memory_buffer_create_from_file(self):
        source = self.get_test_file()

        MemoryBuffer(filename=source)

    def test_memory_buffer_failing(self):
        with self.assertRaises(Exception):
            MemoryBuffer(filename="/hopefully/this/path/doesnt/exist")

    def test_memory_buffer_len(self):
        source = self.get_test_file()
        m = MemoryBuffer(filename=source)
        self.assertEqual(len(m), 50)

    def test_create_passregistry(self):
        PassRegistry()

    def test_create_context(self):
        Context.GetGlobalContext()

    def test_create_module_with_name(self):
        # Make sure we can not create a module without a LLVMModuleRef.
        with self.assertRaises(TypeError):
            m = Module()
        m = Module.CreateWithName("test-module")

    def test_module_getset_datalayout(self):
        m = Module.CreateWithName("test-module")
        dl = "e-p:32:32:32-i1:8:32-i8:8:32-i16:16:32-i32:32:32-i64:32:64-f32:32:32-f64:32:64-v64:32:64-v128:32:128-a0:0:32-n32-S32"
        m.datalayout = dl
        self.assertEqual(m.datalayout, dl)

    def test_module_getset_target(self):
        m = Module.CreateWithName("test-module")
        target = "thumbv7-apple-ios5.0.0"
        m.target = target
        self.assertEqual(m.target, target)

    def test_module_print_module_to_file(self):
        m = Module.CreateWithName("test")
        dl = "e-p:32:32:32-i1:8:32-i8:8:32-i16:16:32-i32:32:32-i64:32:64-f32:32:32-f64:32:64-v64:32:64-v128:32:128-a0:0:32-n32-S32"
        m.datalayout = dl
        target = "thumbv7-apple-ios5.0.0"
        m.target = target
        m.print_module_to_file("test2.ll")
    
    def test_module_function_iteration(self):
        m = Module.from_bitcode_buffer(MemoryBuffer(filename=self.get_test_bc()))
        i = 0
        functions = ["f", "f2", "f3", "f4", "f5", "f6", "g1", "g2", "h1", "h2",
                     "h3"]
        # Forward
        for f in m:
            self.assertEqual(f.name, functions[i])
            f.dump()
            i += 1
        # Backwards
        for f in reversed(m):
            i -= 1
            self.assertEqual(f.name, functions[i])
            f.dump()

    def test_function_basicblock_iteration(self):
        m = Module.from_bitcode_buffer(MemoryBuffer(filename=self.get_test_bc()))
        i = 0
        
        bb_list = ['b1', 'b2', 'end']
        
        f = m.first
        while f.name != "f6":
            f = f.next
        
        # Forward
        for bb in f:
            self.assertEqual(bb.name, bb_list[i])
            bb.dump()
            i += 1
        
        # Backwards
        for bb in reversed(f):
            i -= 1
            self.assertEqual(bb.name, bb_list[i])
            bb.dump()

    def test_basicblock_instruction_iteration(self):
        m = Module.from_bitcode_buffer(MemoryBuffer(filename=self.get_test_bc()))
        i = 0
        
        inst_list = [('arg1', OpCode.ExtractValue),
                     ('arg2', OpCode.ExtractValue),
                     ('', OpCode.Call),
                     ('', OpCode.Ret)]
        
        bb = m.first.first

        # Forward
        for inst in bb:
            self.assertEqual(inst.name, inst_list[i][0])
            self.assertEqual(inst.opcode, inst_list[i][1])
            for op in range(len(inst)):
                o = inst.get_operand(op)
                print o.name
                o.dump()
            inst.dump()
            i += 1

        # Backwards
        for inst in reversed(bb):
            i -= 1
            self.assertEqual(inst.name, inst_list[i][0])
            self.assertEqual(inst.opcode, inst_list[i][1])
            inst.dump()
