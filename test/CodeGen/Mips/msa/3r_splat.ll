; Test the MSA splat intrinsics that are encoded with the 3R instruction
; format.

; RUN: llc -march=mips -mattr=+msa < %s | FileCheck %s

@llvm_mips_splat_b_ARG1 = global <16 x i8> <i8 0, i8 1, i8 2, i8 3, i8 4, i8 5, i8 6, i8 7, i8 8, i8 9, i8 10, i8 11, i8 12, i8 13, i8 14, i8 15>, align 16
@llvm_mips_splat_b_RES  = global <16 x i8> <i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0, i8 0>, align 16

define void @llvm_mips_splat_b_test() nounwind {
entry:
  %0 = load <16 x i8>* @llvm_mips_splat_b_ARG1
  %1 = tail call <16 x i8> @llvm.mips.splat.b(<16 x i8> %0, i32 3)
  store <16 x i8> %1, <16 x i8>* @llvm_mips_splat_b_RES
  ret void
}

declare <16 x i8> @llvm.mips.splat.b(<16 x i8>, i32) nounwind

; CHECK: llvm_mips_splat_b_test:
; CHECK: ld.b
; CHECK: splat.b
; CHECK: st.b
; CHECK: .size llvm_mips_splat_b_test
;
@llvm_mips_splat_h_ARG1 = global <8 x i16> <i16 0, i16 1, i16 2, i16 3, i16 4, i16 5, i16 6, i16 7>, align 16
@llvm_mips_splat_h_RES  = global <8 x i16> <i16 0, i16 0, i16 0, i16 0, i16 0, i16 0, i16 0, i16 0>, align 16

define void @llvm_mips_splat_h_test() nounwind {
entry:
  %0 = load <8 x i16>* @llvm_mips_splat_h_ARG1
  %1 = tail call <8 x i16> @llvm.mips.splat.h(<8 x i16> %0, i32 3)
  store <8 x i16> %1, <8 x i16>* @llvm_mips_splat_h_RES
  ret void
}

declare <8 x i16> @llvm.mips.splat.h(<8 x i16>, i32) nounwind

; CHECK: llvm_mips_splat_h_test:
; CHECK: ld.h
; CHECK: splat.h
; CHECK: st.h
; CHECK: .size llvm_mips_splat_h_test
;
@llvm_mips_splat_w_ARG1 = global <4 x i32> <i32 0, i32 1, i32 2, i32 3>, align 16
@llvm_mips_splat_w_RES  = global <4 x i32> <i32 0, i32 0, i32 0, i32 0>, align 16

define void @llvm_mips_splat_w_test() nounwind {
entry:
  %0 = load <4 x i32>* @llvm_mips_splat_w_ARG1
  %1 = tail call <4 x i32> @llvm.mips.splat.w(<4 x i32> %0, i32 3)
  store <4 x i32> %1, <4 x i32>* @llvm_mips_splat_w_RES
  ret void
}

declare <4 x i32> @llvm.mips.splat.w(<4 x i32>, i32) nounwind

; CHECK: llvm_mips_splat_w_test:
; CHECK: ld.w
; CHECK: splat.w
; CHECK: st.w
; CHECK: .size llvm_mips_splat_w_test
;
@llvm_mips_splat_d_ARG1 = global <2 x i64> <i64 0, i64 1>, align 16
@llvm_mips_splat_d_RES  = global <2 x i64> <i64 0, i64 0>, align 16

define void @llvm_mips_splat_d_test() nounwind {
entry:
  %0 = load <2 x i64>* @llvm_mips_splat_d_ARG1
  %1 = tail call <2 x i64> @llvm.mips.splat.d(<2 x i64> %0, i32 3)
  store <2 x i64> %1, <2 x i64>* @llvm_mips_splat_d_RES
  ret void
}

declare <2 x i64> @llvm.mips.splat.d(<2 x i64>, i32) nounwind

; CHECK: llvm_mips_splat_d_test:
; CHECK: ld.d
; CHECK: splat.d
; CHECK: st.d
; CHECK: .size llvm_mips_splat_d_test
;
