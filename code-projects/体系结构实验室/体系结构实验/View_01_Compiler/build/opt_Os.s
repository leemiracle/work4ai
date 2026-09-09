
build/opt_Os：     文件格式 elf64-littleaarch64


Disassembly of section .init:

00000000004005d0 <_init>:
  4005d0:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  4005d4:	910003fd 	mov	x29, sp
  4005d8:	940000de 	bl	400950 <call_weak_fn>
  4005dc:	a8c17bfd 	ldp	x29, x30, [sp], #16
  4005e0:	d65f03c0 	ret

Disassembly of section .plt:

00000000004005f0 <.plt>:
  4005f0:	a9bf7bf0 	stp	x16, x30, [sp, #-16]!
  4005f4:	b0000090 	adrp	x16, 411000 <__FRAME_END__+0xfff0>
  4005f8:	f947fe11 	ldr	x17, [x16, #4088]
  4005fc:	913fe210 	add	x16, x16, #0xff8
  400600:	d61f0220 	br	x17
  400604:	d503201f 	nop
  400608:	d503201f 	nop
  40060c:	d503201f 	nop

0000000000400610 <clock_gettime@plt>:
  400610:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400614:	f9400211 	ldr	x17, [x16]
  400618:	91000210 	add	x16, x16, #0x0
  40061c:	d61f0220 	br	x17

0000000000400620 <__libc_start_main@plt>:
  400620:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400624:	f9400611 	ldr	x17, [x16, #8]
  400628:	91002210 	add	x16, x16, #0x8
  40062c:	d61f0220 	br	x17

0000000000400630 <rand@plt>:
  400630:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400634:	f9400a11 	ldr	x17, [x16, #16]
  400638:	91004210 	add	x16, x16, #0x10
  40063c:	d61f0220 	br	x17

0000000000400640 <__gmon_start__@plt>:
  400640:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400644:	f9400e11 	ldr	x17, [x16, #24]
  400648:	91006210 	add	x16, x16, #0x18
  40064c:	d61f0220 	br	x17

0000000000400650 <abort@plt>:
  400650:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400654:	f9401211 	ldr	x17, [x16, #32]
  400658:	91008210 	add	x16, x16, #0x20
  40065c:	d61f0220 	br	x17

0000000000400660 <puts@plt>:
  400660:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400664:	f9401611 	ldr	x17, [x16, #40]
  400668:	9100a210 	add	x16, x16, #0x28
  40066c:	d61f0220 	br	x17

0000000000400670 <srand@plt>:
  400670:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400674:	f9401a11 	ldr	x17, [x16, #48]
  400678:	9100c210 	add	x16, x16, #0x30
  40067c:	d61f0220 	br	x17

0000000000400680 <printf@plt>:
  400680:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400684:	f9401e11 	ldr	x17, [x16, #56]
  400688:	9100e210 	add	x16, x16, #0x38
  40068c:	d61f0220 	br	x17

0000000000400690 <putchar@plt>:
  400690:	d0000090 	adrp	x16, 412000 <clock_gettime@GLIBC_2.17>
  400694:	f9402211 	ldr	x17, [x16, #64]
  400698:	91010210 	add	x16, x16, #0x40
  40069c:	d61f0220 	br	x17

Disassembly of section .text:

00000000004006a0 <main>:
  4006a0:	d288120c 	mov	x12, #0x4090                	// #16528
  4006a4:	cb2c63ff 	sub	sp, sp, x12
  4006a8:	52800540 	mov	w0, #0x2a                  	// #42
  4006ac:	a9007bfd 	stp	x29, x30, [sp]
  4006b0:	910003fd 	mov	x29, sp
  4006b4:	a90153f3 	stp	x19, x20, [sp, #16]
  4006b8:	d00000b3 	adrp	x19, 416000 <B+0x3fa4>
  4006bc:	d0000094 	adrp	x20, 412000 <clock_gettime@GLIBC_2.17>
  4006c0:	f90013f5 	str	x21, [sp, #32]
  4006c4:	91017273 	add	x19, x19, #0x5c
  4006c8:	6d0327e8 	stp	d8, d9, [sp, #48]
  4006cc:	91017294 	add	x20, x20, #0x5c
  4006d0:	d2800015 	mov	x21, #0x0                   	// #0
  4006d4:	6d042fea 	stp	d10, d11, [sp, #64]
  4006d8:	97ffffe6 	bl	400670 <srand@plt>
  4006dc:	0f016608 	movi	v8.2s, #0x30, lsl #24
  4006e0:	97ffffd4 	bl	400630 <rand@plt>
  4006e4:	1e220000 	scvtf	s0, w0
  4006e8:	1e280800 	fmul	s0, s0, s8
  4006ec:	bc336aa0 	str	s0, [x21, x19]
  4006f0:	97ffffd0 	bl	400630 <rand@plt>
  4006f4:	1e220000 	scvtf	s0, w0
  4006f8:	1e280800 	fmul	s0, s0, s8
  4006fc:	bc346aa0 	str	s0, [x21, x20]
  400700:	910012b5 	add	x21, x21, #0x4
  400704:	f14012bf 	cmp	x21, #0x4, lsl #12
  400708:	54fffec1 	b.ne	4006e0 <main+0x40>  // b.any
  40070c:	aa1303e0 	mov	x0, x19
  400710:	52820002 	mov	w2, #0x1000                	// #4096
  400714:	aa1403e1 	mov	x1, x20
  400718:	940000bf 	bl	400a14 <dot_product>
  40071c:	1e20400b 	fmov	s11, s0
  400720:	1e2c1000 	fmov	s0, #5.000000000000000000e-01
  400724:	52820001 	mov	w1, #0x1000                	// #4096
  400728:	940000c5 	bl	400a3c <conditional_sum>
  40072c:	1e20400a 	fmov	s10, s0
  400730:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400734:	91380000 	add	x0, x0, #0xe00
  400738:	1e201000 	fmov	s0, #2.000000000000000000e+00
  40073c:	528000a1 	mov	w1, #0x5                   	// #5
  400740:	a9400c02 	ldp	x2, x3, [x0]
  400744:	a9078fe2 	stp	x2, x3, [sp, #120]
  400748:	b9401000 	ldr	w0, [x0, #16]
  40074c:	b9008be0 	str	w0, [sp, #136]
  400750:	9101e3e0 	add	x0, sp, #0x78
  400754:	940000c6 	bl	400a6c <poly_eval>
  400758:	1e204009 	fmov	s9, s0
  40075c:	52970a40 	mov	w0, #0xb852                	// #47186
  400760:	52820002 	mov	w2, #0x1000                	// #4096
  400764:	72a812c0 	movk	w0, #0x4096, lsl #16
  400768:	aa1303e1 	mov	x1, x19
  40076c:	b90057e0 	str	w0, [sp, #84]
  400770:	910243e0 	add	x0, sp, #0x90
  400774:	940000d0 	bl	400ab4 <manual_unroll>
  400778:	910163e1 	add	x1, sp, #0x58
  40077c:	52800020 	mov	w0, #0x1                   	// #1
  400780:	97ffffa4 	bl	400610 <clock_gettime@plt>
  400784:	b90053ff 	str	wzr, [sp, #80]
  400788:	52807d04 	mov	w4, #0x3e8                 	// #1000
  40078c:	aa1403e1 	mov	x1, x20
  400790:	aa1303e0 	mov	x0, x19
  400794:	52820002 	mov	w2, #0x1000                	// #4096
  400798:	9400009f 	bl	400a14 <dot_product>
  40079c:	bd4053e1 	ldr	s1, [sp, #80]
  4007a0:	71000484 	subs	w4, w4, #0x1
  4007a4:	1e202821 	fadd	s1, s1, s0
  4007a8:	bd0053e1 	str	s1, [sp, #80]
  4007ac:	54ffff01 	b.ne	40078c <main+0xec>  // b.any
  4007b0:	9101a3e1 	add	x1, sp, #0x68
  4007b4:	52800020 	mov	w0, #0x1                   	// #1
  4007b8:	97ffff96 	bl	400610 <clock_gettime@plt>
  4007bc:	f9402fe1 	ldr	x1, [sp, #88]
  4007c0:	f94037e0 	ldr	x0, [sp, #104]
  4007c4:	cb010000 	sub	x0, x0, x1
  4007c8:	f94033e1 	ldr	x1, [sp, #96]
  4007cc:	9e620001 	scvtf	d1, x0
  4007d0:	f9403be0 	ldr	x0, [sp, #112]
  4007d4:	cb010000 	sub	x0, x0, x1
  4007d8:	9e620008 	scvtf	d8, x0
  4007dc:	d2d09000 	mov	x0, #0x848000000000        	// #145685290680320
  4007e0:	f2e825c0 	movk	x0, #0x412e, lsl #48
  4007e4:	9e670000 	fmov	d0, x0
  4007e8:	d2c80000 	mov	x0, #0x400000000000        	// #70368744177664
  4007ec:	f2e811e0 	movk	x0, #0x408f, lsl #48
  4007f0:	1e601908 	fdiv	d8, d8, d0
  4007f4:	9e670000 	fmov	d0, x0
  4007f8:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4007fc:	91304000 	add	x0, x0, #0xc10
  400800:	1f402028 	fmadd	d8, d1, d0, d8
  400804:	97ffff97 	bl	400660 <puts@plt>
  400808:	1e22c160 	fcvt	d0, s11
  40080c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400810:	91313c00 	add	x0, x0, #0xc4f
  400814:	97ffff9b 	bl	400680 <printf@plt>
  400818:	1e22c140 	fcvt	d0, s10
  40081c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400820:	91319400 	add	x0, x0, #0xc65
  400824:	97ffff97 	bl	400680 <printf@plt>
  400828:	1e22c120 	fcvt	d0, s9
  40082c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400830:	9131ec00 	add	x0, x0, #0xc7b
  400834:	97ffff93 	bl	400680 <printf@plt>
  400838:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  40083c:	fd46fc00 	ldr	d0, [x0, #3576]
  400840:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400844:	91324400 	add	x0, x0, #0xc91
  400848:	97ffff8e 	bl	400680 <printf@plt>
  40084c:	2d5207e0 	ldp	s0, s1, [sp, #144]
  400850:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400854:	2d530fe2 	ldp	s2, s3, [sp, #152]
  400858:	91329c00 	add	x0, x0, #0xca7
  40085c:	1e22c021 	fcvt	d1, s1
  400860:	1e22c000 	fcvt	d0, s0
  400864:	1e22c063 	fcvt	d3, s3
  400868:	1e22c042 	fcvt	d2, s2
  40086c:	97ffff85 	bl	400680 <printf@plt>
  400870:	52800140 	mov	w0, #0xa                   	// #10
  400874:	97ffff87 	bl	400690 <putchar@plt>
  400878:	1e604100 	fmov	d0, d8
  40087c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400880:	91335800 	add	x0, x0, #0xcd6
  400884:	97ffff7f 	bl	400680 <printf@plt>
  400888:	52800140 	mov	w0, #0xa                   	// #10
  40088c:	97ffff81 	bl	400690 <putchar@plt>
  400890:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400894:	9133f000 	add	x0, x0, #0xcfc
  400898:	97ffff72 	bl	400660 <puts@plt>
  40089c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008a0:	91344800 	add	x0, x0, #0xd12
  4008a4:	97ffff6f 	bl	400660 <puts@plt>
  4008a8:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008ac:	91352400 	add	x0, x0, #0xd49
  4008b0:	97ffff6c 	bl	400660 <puts@plt>
  4008b4:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008b8:	9135e400 	add	x0, x0, #0xd79
  4008bc:	97ffff69 	bl	400660 <puts@plt>
  4008c0:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008c4:	91367c00 	add	x0, x0, #0xd9f
  4008c8:	97ffff66 	bl	400660 <puts@plt>
  4008cc:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008d0:	91372000 	add	x0, x0, #0xdc8
  4008d4:	97ffff63 	bl	400660 <puts@plt>
  4008d8:	52800000 	mov	w0, #0x0                   	// #0
  4008dc:	d288120c 	mov	x12, #0x4090                	// #16528
  4008e0:	a9407bfd 	ldp	x29, x30, [sp]
  4008e4:	a94153f3 	ldp	x19, x20, [sp, #16]
  4008e8:	f94013f5 	ldr	x21, [sp, #32]
  4008ec:	6d4327e8 	ldp	d8, d9, [sp, #48]
  4008f0:	6d442fea 	ldp	d10, d11, [sp, #64]
  4008f4:	bd4053e0 	ldr	s0, [sp, #80]
  4008f8:	8b2c63ff 	add	sp, sp, x12
  4008fc:	d65f03c0 	ret

0000000000400900 <_start>:
  400900:	d280001d 	mov	x29, #0x0                   	// #0
  400904:	d280001e 	mov	x30, #0x0                   	// #0
  400908:	aa0003e5 	mov	x5, x0
  40090c:	f94003e1 	ldr	x1, [sp]
  400910:	910023e2 	add	x2, sp, #0x8
  400914:	910003e6 	mov	x6, sp
  400918:	d2e00000 	movz	x0, #0x0, lsl #48
  40091c:	f2c00000 	movk	x0, #0x0, lsl #32
  400920:	f2a00800 	movk	x0, #0x40, lsl #16
  400924:	f280d400 	movk	x0, #0x6a0
  400928:	d2e00003 	movz	x3, #0x0, lsl #48
  40092c:	f2c00003 	movk	x3, #0x0, lsl #32
  400930:	f2a00803 	movk	x3, #0x40, lsl #16
  400934:	f2816c03 	movk	x3, #0xb60
  400938:	d2e00004 	movz	x4, #0x0, lsl #48
  40093c:	f2c00004 	movk	x4, #0x0, lsl #32
  400940:	f2a00804 	movk	x4, #0x40, lsl #16
  400944:	f2817c04 	movk	x4, #0xbe0
  400948:	97ffff36 	bl	400620 <__libc_start_main@plt>
  40094c:	97ffff41 	bl	400650 <abort@plt>

0000000000400950 <call_weak_fn>:
  400950:	b0000080 	adrp	x0, 411000 <__FRAME_END__+0xfff0>
  400954:	f947f000 	ldr	x0, [x0, #4064]
  400958:	b4000040 	cbz	x0, 400960 <call_weak_fn+0x10>
  40095c:	17ffff39 	b	400640 <__gmon_start__@plt>
  400960:	d65f03c0 	ret
  400964:	d503201f 	nop
  400968:	d503201f 	nop
  40096c:	d503201f 	nop

0000000000400970 <deregister_tm_clones>:
  400970:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400974:	91016000 	add	x0, x0, #0x58
  400978:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  40097c:	91016021 	add	x1, x1, #0x58
  400980:	eb00003f 	cmp	x1, x0
  400984:	540000c0 	b.eq	40099c <deregister_tm_clones+0x2c>  // b.none
  400988:	90000001 	adrp	x1, 400000 <_init-0x5d0>
  40098c:	f9460021 	ldr	x1, [x1, #3072]
  400990:	b4000061 	cbz	x1, 40099c <deregister_tm_clones+0x2c>
  400994:	aa0103f0 	mov	x16, x1
  400998:	d61f0200 	br	x16
  40099c:	d65f03c0 	ret

00000000004009a0 <register_tm_clones>:
  4009a0:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  4009a4:	91016000 	add	x0, x0, #0x58
  4009a8:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  4009ac:	91016021 	add	x1, x1, #0x58
  4009b0:	cb000021 	sub	x1, x1, x0
  4009b4:	d37ffc22 	lsr	x2, x1, #63
  4009b8:	8b810c41 	add	x1, x2, x1, asr #3
  4009bc:	eb8107ff 	cmp	xzr, x1, asr #1
  4009c0:	9341fc21 	asr	x1, x1, #1
  4009c4:	540000c0 	b.eq	4009dc <register_tm_clones+0x3c>  // b.none
  4009c8:	90000002 	adrp	x2, 400000 <_init-0x5d0>
  4009cc:	f9460442 	ldr	x2, [x2, #3080]
  4009d0:	b4000062 	cbz	x2, 4009dc <register_tm_clones+0x3c>
  4009d4:	aa0203f0 	mov	x16, x2
  4009d8:	d61f0200 	br	x16
  4009dc:	d65f03c0 	ret

00000000004009e0 <__do_global_dtors_aux>:
  4009e0:	a9be7bfd 	stp	x29, x30, [sp, #-32]!
  4009e4:	910003fd 	mov	x29, sp
  4009e8:	f9000bf3 	str	x19, [sp, #16]
  4009ec:	d0000093 	adrp	x19, 412000 <clock_gettime@GLIBC_2.17>
  4009f0:	39416260 	ldrb	w0, [x19, #88]
  4009f4:	35000080 	cbnz	w0, 400a04 <__do_global_dtors_aux+0x24>
  4009f8:	97ffffde 	bl	400970 <deregister_tm_clones>
  4009fc:	52800020 	mov	w0, #0x1                   	// #1
  400a00:	39016260 	strb	w0, [x19, #88]
  400a04:	f9400bf3 	ldr	x19, [sp, #16]
  400a08:	a8c27bfd 	ldp	x29, x30, [sp], #32
  400a0c:	d65f03c0 	ret

0000000000400a10 <frame_dummy>:
  400a10:	17ffffe4 	b	4009a0 <register_tm_clones>

0000000000400a14 <dot_product>:
  400a14:	0f000400 	movi	v0.2s, #0x0
  400a18:	d2800003 	mov	x3, #0x0                   	// #0
  400a1c:	6b03005f 	cmp	w2, w3
  400a20:	5400004c 	b.gt	400a28 <dot_product+0x14>
  400a24:	d65f03c0 	ret
  400a28:	bc637802 	ldr	s2, [x0, x3, lsl #2]
  400a2c:	bc637821 	ldr	s1, [x1, x3, lsl #2]
  400a30:	91000463 	add	x3, x3, #0x1
  400a34:	1f010040 	fmadd	s0, s2, s1, s0
  400a38:	17fffff9 	b	400a1c <dot_product+0x8>

0000000000400a3c <conditional_sum>:
  400a3c:	1e204001 	fmov	s1, s0
  400a40:	0f000400 	movi	v0.2s, #0x0
  400a44:	d2800002 	mov	x2, #0x0                   	// #0
  400a48:	6b02003f 	cmp	w1, w2
  400a4c:	5400004c 	b.gt	400a54 <conditional_sum+0x18>
  400a50:	d65f03c0 	ret
  400a54:	bc627802 	ldr	s2, [x0, x2, lsl #2]
  400a58:	1e212050 	fcmpe	s2, s1
  400a5c:	5400004d 	b.le	400a64 <conditional_sum+0x28>
  400a60:	1e222800 	fadd	s0, s0, s2
  400a64:	91000442 	add	x2, x2, #0x1
  400a68:	17fffff8 	b	400a48 <conditional_sum+0xc>

0000000000400a6c <poly_eval>:
  400a6c:	51000421 	sub	w1, w1, #0x1
  400a70:	1e204001 	fmov	s1, s0
  400a74:	0f000400 	movi	v0.2s, #0x0
  400a78:	93407c21 	sxtw	x1, w1
  400a7c:	36f80041 	tbz	w1, #31, 400a84 <poly_eval+0x18>
  400a80:	d65f03c0 	ret
  400a84:	bc617802 	ldr	s2, [x0, x1, lsl #2]
  400a88:	d1000421 	sub	x1, x1, #0x1
  400a8c:	1f010800 	fmadd	s0, s0, s1, s2
  400a90:	17fffffb 	b	400a7c <poly_eval+0x10>

0000000000400a94 <dead_code_test>:
  400a94:	529eb860 	mov	w0, #0xf5c3                	// #62915
  400a98:	d10043ff 	sub	sp, sp, #0x10
  400a9c:	72a80900 	movk	w0, #0x4048, lsl #16
  400aa0:	1e270001 	fmov	s1, w0
  400aa4:	1e210800 	fmul	s0, s0, s1
  400aa8:	bd000fe0 	str	s0, [sp, #12]
  400aac:	910043ff 	add	sp, sp, #0x10
  400ab0:	d65f03c0 	ret

0000000000400ab4 <manual_unroll>:
  400ab4:	aa0103e3 	mov	x3, x1
  400ab8:	aa0003e4 	mov	x4, x0
  400abc:	52800065 	mov	w5, #0x3                   	// #3
  400ac0:	6b05005f 	cmp	w2, w5
  400ac4:	5400010c 	b.gt	400ae4 <manual_unroll+0x30>
  400ac8:	121e7443 	and	w3, w2, #0xfffffffc
  400acc:	7100005f 	cmp	w2, #0x0
  400ad0:	1a9fa063 	csel	w3, w3, wzr, ge  // ge = tcont
  400ad4:	93407c63 	sxtw	x3, w3
  400ad8:	6b03005f 	cmp	w2, w3
  400adc:	5400024c 	b.gt	400b24 <manual_unroll+0x70>
  400ae0:	d65f03c0 	ret
  400ae4:	bd400060 	ldr	s0, [x3]
  400ae8:	110010a5 	add	w5, w5, #0x4
  400aec:	91004063 	add	x3, x3, #0x10
  400af0:	91004084 	add	x4, x4, #0x10
  400af4:	1e202800 	fadd	s0, s0, s0
  400af8:	bc1f0080 	stur	s0, [x4, #-16]
  400afc:	bc5f4060 	ldur	s0, [x3, #-12]
  400b00:	1e202800 	fadd	s0, s0, s0
  400b04:	bc1f4080 	stur	s0, [x4, #-12]
  400b08:	bc5f8060 	ldur	s0, [x3, #-8]
  400b0c:	1e202800 	fadd	s0, s0, s0
  400b10:	bc1f8080 	stur	s0, [x4, #-8]
  400b14:	bc5fc060 	ldur	s0, [x3, #-4]
  400b18:	1e202800 	fadd	s0, s0, s0
  400b1c:	bc1fc080 	stur	s0, [x4, #-4]
  400b20:	17ffffe8 	b	400ac0 <manual_unroll+0xc>
  400b24:	bc637820 	ldr	s0, [x1, x3, lsl #2]
  400b28:	1e202800 	fadd	s0, s0, s0
  400b2c:	bc237800 	str	s0, [x0, x3, lsl #2]
  400b30:	91000463 	add	x3, x3, #0x1
  400b34:	17ffffe9 	b	400ad8 <manual_unroll+0x24>

0000000000400b38 <bad_loop>:
  400b38:	2a0003e2 	mov	w2, w0
  400b3c:	52800001 	mov	w1, #0x0                   	// #0
  400b40:	52800000 	mov	w0, #0x0                   	// #0
  400b44:	6b02003f 	cmp	w1, w2
  400b48:	5400004b 	b.lt	400b50 <bad_loop+0x18>  // b.tstop
  400b4c:	d65f03c0 	ret
  400b50:	0b010000 	add	w0, w0, w1
  400b54:	11000421 	add	w1, w1, #0x1
  400b58:	17fffffb 	b	400b44 <bad_loop+0xc>
  400b5c:	d503201f 	nop

0000000000400b60 <__libc_csu_init>:
  400b60:	a9bc7bfd 	stp	x29, x30, [sp, #-64]!
  400b64:	910003fd 	mov	x29, sp
  400b68:	a90153f3 	stp	x19, x20, [sp, #16]
  400b6c:	b0000094 	adrp	x20, 411000 <__FRAME_END__+0xfff0>
  400b70:	91378294 	add	x20, x20, #0xde0
  400b74:	a9025bf5 	stp	x21, x22, [sp, #32]
  400b78:	b0000095 	adrp	x21, 411000 <__FRAME_END__+0xfff0>
  400b7c:	913762b5 	add	x21, x21, #0xdd8
  400b80:	cb150294 	sub	x20, x20, x21
  400b84:	2a0003f6 	mov	w22, w0
  400b88:	a90363f7 	stp	x23, x24, [sp, #48]
  400b8c:	aa0103f7 	mov	x23, x1
  400b90:	aa0203f8 	mov	x24, x2
  400b94:	97fffe8f 	bl	4005d0 <_init>
  400b98:	eb940fff 	cmp	xzr, x20, asr #3
  400b9c:	54000160 	b.eq	400bc8 <__libc_csu_init+0x68>  // b.none
  400ba0:	9343fe94 	asr	x20, x20, #3
  400ba4:	d2800013 	mov	x19, #0x0                   	// #0
  400ba8:	f8737aa3 	ldr	x3, [x21, x19, lsl #3]
  400bac:	aa1803e2 	mov	x2, x24
  400bb0:	91000673 	add	x19, x19, #0x1
  400bb4:	aa1703e1 	mov	x1, x23
  400bb8:	2a1603e0 	mov	w0, w22
  400bbc:	d63f0060 	blr	x3
  400bc0:	eb13029f 	cmp	x20, x19
  400bc4:	54ffff21 	b.ne	400ba8 <__libc_csu_init+0x48>  // b.any
  400bc8:	a94153f3 	ldp	x19, x20, [sp, #16]
  400bcc:	a9425bf5 	ldp	x21, x22, [sp, #32]
  400bd0:	a94363f7 	ldp	x23, x24, [sp, #48]
  400bd4:	a8c47bfd 	ldp	x29, x30, [sp], #64
  400bd8:	d65f03c0 	ret
  400bdc:	d503201f 	nop

0000000000400be0 <__libc_csu_fini>:
  400be0:	d65f03c0 	ret

Disassembly of section .fini:

0000000000400be4 <_fini>:
  400be4:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  400be8:	910003fd 	mov	x29, sp
  400bec:	a8c17bfd 	ldp	x29, x30, [sp], #16
  400bf0:	d65f03c0 	ret
