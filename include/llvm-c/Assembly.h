/*===-- llvm-c/Assembly.h - Assembly parser C interface --------*- C++ -*-===*\
|*                                                                            *|
|*                     The LLVM Compiler Infrastructure                       *|
|*                                                                            *|
|* This file is distributed under the University of Illinois Open Source      *|
|* License. See LICENSE.TXT for details.                                      *|
|*                                                                            *|
|*===----------------------------------------------------------------------===*|
|*                                                                            *|
|* This header defines the C interface to the assembly parser.                *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifndef LLVM_C_EXECUTIONENGINE_H
#define LLVM_C_EXECUTIONENGINE_H

#include "llvm-c/Core.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Parse an ASCII file that contains LLVM Assembly code into a Module.
 *
 * This reads the full contents of the file specified and parses LLVM Assembly
 * into a new Module instance.
 *
 * Note that the Assembly is not verified as part of the parse. For that, you
 * will need to launch a verifier.
 *
 * Returns false (0) on successful parse or true (1) otherwise.
 *
 * @see llvm::ParseAssemblyFile()
 *
 * @param context Context to use.
 * @param filename The path to the file to parse.
 * @param module Memory address that will contain the parsed Module on success.
 * @param error Memory address that will contain error on failure.
 * @return False on success, true on error.
 */
LLVMBool LLVMAssemblyParseFileInContext(LLVMContextRef context,
                                   const char *filename,
                                   LLVMModuleRef *module,
                                   char **error);

/**
 * Parse a file containing LLVM Assembly using the global context.
 *
 * This is the same as LLVMAssemblyParseFileInContext() except it uses the
 * global Context.
 *
 * @see LLVMAssemblyParseFileInContext()
 * @see llvm::ParseAssemblyFile()
 */
LLVMBool LLVMAssemblyParseFile(const char *filename,
                               LLVMModuleRef *module,
                               char **error);

/**
 * Parse a string containing LLVM Assembly into a Module.
 *
 * The passed string is assumed to contain ASCII LLVM Assembly.
 *
 * Note that the value of the memory passed in via the module parameter
 * dictates whether a new Module is created or whether to parse into an
 * existing Module. See LLVMAssemblyParseMemoryBuffer() for full details.
 *
 * @see llvm::ParseAssemblyString()
 *
 * @param context Context to parse in.
 * @param assembly ASCII string containing LLVM Assembly code.
 * @param module Memory address to receive parsed Module on success.
 * @param error Memory address to receive error message on failure.
 * @return False on success or true on failure.
 */
LLVMBool LLVMAssemblyParseStringInContext(LLVMContextRef context,
                                          const char *assembly,
                                          LLVMModuleRef *module,
                                          char **error);

/**
 * Parse a string containing assembly into a Module using the global context.
 *
 * This is the same as LLVMAssemblyParseStringInContext except the global
 * context is used.
 *
 * @see LLVMAssemblyParseStringInContext()
 * @see llvm::ParseAssemblyString()
 */
LLVMBool LLVMAssemblyParseString(const char *assembly,
                                 LLVMModuleRef *module,
                                 char **error);

/**
 * Parse a memory buffer containing LLVM Assembly into a Module.
 *
 * This is an interface to the low-level parser API. Other APIs (e.g. file
 * and string parsing) are wrappers around this one. It is encouraged to use
 * one of those APIs if possible.
 *
 * Note that this does not verify that the generated Module is valid. To ensure
 * validity, run the verifier after parsing.
 *
 * The caller has the choice of whether the parse assembly into a new Module or
 * to add it to an existing Module. If the memory address passed via the module
 * parameter contains a non-NULL value, this means to parse into an existing
 * Module (which is assumed to exist at the memory address specified). If the
 * memory is NULL, a new Module will be created and the memory address will
 * point to it.
 *
 * If an error occurred (and true is returned), error will point to an error
 * message describing what went wrong.
 *
 * When called, ownership of the passed MemoryBuffer is always transferred
 * to the function. Callers should not attempt to dispose of the memory buffer
 * after calling.
 *
 * @see llvm::ParseAssembly()
 *
 * @param context Context to parse in.
 * @param memory MemoryBuffer to read LLVM Assembly from.
 * @param module Memory address to receive parsed Module instance on success.
 * @param error Memory address to receive error message on failure.
 * @return False on success, true on failure.
 */
LLVMBool LLVMAssemblyParseMemoryBufferInContext(LLVMContextRef context,
                                                LLVMMemoryBufferRef memory,
                                                LLVMModuleRef *module,
                                                char **error);

/**
 * Parse a MemoryBuffer containing LLVM Assembly into a Module using the global
 * Context.
 *
 * This is identical to LLVMAssemblyParseMemoryBufferInContext() except it uses
 * the global Context.
 *
 * @see LLVMAssemblyParseMemoryBufferInContext()
 * @see llvm::ParseAssembly()
 */
LLVMBool LLVMAssemblyParseMemoryBuffer(LLVMMemoryBufferRef memory,
                                       LLVMModuleRef *module,
                                       char **error);

#ifdef __cplusplus
}
#endif

#endif
