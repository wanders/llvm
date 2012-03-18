//===- ParserBindings.cpp - C bindings for parser library -----------------===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//
//
// This file defines the C bindings for the Assembly Parser library.
//
//===----------------------------------------------------------------------===//

#include "llvm-c/Assembly.h"
#include "llvm/Assembly/Parser.h"
#include "llvm/Module.h"
#include "llvm/Support/SourceMgr.h"
using namespace llvm;

LLVMBool LLVMAssemblyParseFileInContext(LLVMContextRef context,
                                        const char *filename,
                                        LLVMModuleRef *module,
                                        char **error) {
  SMDiagnostic Diagnostic;
  Module *M = ParseAssemblyFile(filename, Diagnostic, *unwrap(context));

  if (!M) {
    if (error)
      *error = strdup(Diagnostic.getMessage().c_str());
    return 1;
  }

  if (module)
    *module = wrap(M);

  return 0;
}

LLVMBool LLVMAssemblyParseFile(const char *filename,
                               LLVMModuleRef *module,
                               char **error) {
  return LLVMAssemblyParseFileInContext(LLVMGetGlobalContext(), filename,
                                        module, error);
}

LLVMBool LLVMAssemblyParseStringInContext(LLVMContextRef context,
                                          const char *assembly,
                                          LLVMModuleRef *module,
                                          char **error) {
  SMDiagnostic Diagnostic;
  Module *InputModule = NULL;
  if (module && *module) {
    InputModule = unwrap(*module);
  }

  Module *M = ParseAssemblyString(assembly, InputModule, Diagnostic,
                                  *unwrap(context));

  if (!M) {
    if (error)
      *error = strdup(Diagnostic.getMessage().c_str());

    return 1;
  }

  if (module)
    *module = wrap(M);

  return 0;
}

LLVMBool LLVMAssemblyParseString(const char *assembly,
                                 LLVMModuleRef *module,
                                 char **error) {
  return LLVMAssemblyParseStringInContext(LLVMGetGlobalContext(), assembly,
                                          module, error);
}

LLVMBool LLVMAssemblyParseMemoryBufferInContext(LLVMContextRef context,
                                                LLVMMemoryBufferRef memory,
                                                LLVMModuleRef *module,
                                                char **error) {
  SMDiagnostic Diagnostic;
  Module *InputModule = NULL;
  if (*module) {
    InputModule = unwrap(*module);
  }

  Module *M = ParseAssembly(unwrap(memory), InputModule, Diagnostic,
                            *unwrap(context));

  if (!M) {
    if (error)
      *error = strdup(Diagnostic.getMessage().c_str());

    return 1;
  }

  if (module)
    *module = wrap(M);

  return 0;
}

LLVMBool LLVMAssemblyParseMemoryBuffer(LLVMMemoryBufferRef memory,
                                       LLVMModuleRef *module,
                                       char **error) {
  return LLVMAssemblyParseMemoryBufferInContext(LLVMGetGlobalContext(),
                                                memory, module, error);
}