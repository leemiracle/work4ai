
build/opt_O1：     文件格式 elf64-littleaarch64


Disassembly of section .init:

00000000004005d0 <_init>:
  4005d0:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  4005d4:	910003fd 	mov	x29, sp
  4005d8:	94000046 	bl	4006f0 <call_weak_fn>
  4005dc:	a8c17bfd 	ldp	x29, x30, [sp], #16
  4005e0:	d65f03c0 	ret

Disassembly of section .plt:

00000000004005f0 <.plt>:
  4005f0:	a9bf7bf0 	stp	x16, x30, [sp, #-16]!
  4005f4:	b0000090 	adrp	x16, 411000 <__FRAME_END__+0xff48>
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

00000000004006a0 <_start>:
  4006a0:	d280001d 	mov	x29, #0x0                   	// #0
  4006a4:	d280001e 	mov	x30, #0x0                   	// #0
  4006a8:	aa0003e5 	mov	x5, x0
  4006ac:	f94003e1 	ldr	x1, [sp]
  4006b0:	910023e2 	add	x2, sp, #0x8
  4006b4:	910003e6 	mov	x6, sp
  4006b8:	d2e00000 	movz	x0, #0x0, lsl #48
  4006bc:	f2c00000 	movk	x0, #0x0, lsl #32
  4006c0:	f2a00800 	movk	x0, #0x40, lsl #16
  4006c4:	f2812980 	movk	x0, #0x94c
  4006c8:	d2e00003 	movz	x3, #0x0, lsl #48
  4006cc:	f2c00003 	movk	x3, #0x0, lsl #32
  4006d0:	f2a00803 	movk	x3, #0x40, lsl #16
  4006d4:	f2817e03 	movk	x3, #0xbf0
  4006d8:	d2e00004 	movz	x4, #0x0, lsl #48
  4006dc:	f2c00004 	movk	x4, #0x0, lsl #32
  4006e0:	f2a00804 	movk	x4, #0x40, lsl #16
  4006e4:	f2818e04 	movk	x4, #0xc70
  4006e8:	97ffffce 	bl	400620 <__libc_start_main@plt>
  4006ec:	97ffffd9 	bl	400650 <abort@plt>

00000000004006f0 <call_weak_fn>:
  4006f0:	b0000080 	adrp	x0, 411000 <__FRAME_END__+0xff48>
  4006f4:	f947f000 	ldr	x0, [x0, #4064]
  4006f8:	b4000040 	cbz	x0, 400700 <call_weak_fn+0x10>
  4006fc:	17ffffd1 	b	400640 <__gmon_start__@plt>
  400700:	d65f03c0 	ret
  400704:	d503201f 	nop
  400708:	d503201f 	nop
  40070c:	d503201f 	nop

0000000000400710 <deregister_tm_clones>:
  400710:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400714:	91016000 	add	x0, x0, #0x58
  400718:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  40071c:	91016021 	add	x1, x1, #0x58
  400720:	eb00003f 	cmp	x1, x0
  400724:	540000c0 	b.eq	40073c <deregister_tm_clones+0x2c>  // b.none
  400728:	90000001 	adrp	x1, 400000 <_init-0x5d0>
  40072c:	f9464821 	ldr	x1, [x1, #3216]
  400730:	b4000061 	cbz	x1, 40073c <deregister_tm_clones+0x2c>
  400734:	aa0103f0 	mov	x16, x1
  400738:	d61f0200 	br	x16
  40073c:	d65f03c0 	ret

0000000000400740 <register_tm_clones>:
  400740:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400744:	91016000 	add	x0, x0, #0x58
  400748:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  40074c:	91016021 	add	x1, x1, #0x58
  400750:	cb000021 	sub	x1, x1, x0
  400754:	d37ffc22 	lsr	x2, x1, #63
  400758:	8b810c41 	add	x1, x2, x1, asr #3
  40075c:	eb8107ff 	cmp	xzr, x1, asr #1
  400760:	9341fc21 	asr	x1, x1, #1
  400764:	540000c0 	b.eq	40077c <register_tm_clones+0x3c>  // b.none
  400768:	90000002 	adrp	x2, 400000 <_init-0x5d0>
  40076c:	f9464c42 	ldr	x2, [x2, #3224]
  400770:	b4000062 	cbz	x2, 40077c <register_tm_clones+0x3c>
  400774:	aa0203f0 	mov	x16, x2
  400778:	d61f0200 	br	x16
  40077c:	d65f03c0 	ret

0000000000400780 <__do_global_dtors_aux>:
  400780:	a9be7bfd 	stp	x29, x30, [sp, #-32]!
  400784:	910003fd 	mov	x29, sp
  400788:	f9000bf3 	str	x19, [sp, #16]
  40078c:	d0000093 	adrp	x19, 412000 <clock_gettime@GLIBC_2.17>
  400790:	39416260 	ldrb	w0, [x19, #88]
  400794:	35000080 	cbnz	w0, 4007a4 <__do_global_dtors_aux+0x24>
  400798:	97ffffde 	bl	400710 <deregister_tm_clones>
  40079c:	52800020 	mov	w0, #0x1                   	// #1
  4007a0:	39016260 	strb	w0, [x19, #88]
  4007a4:	f9400bf3 	ldr	x19, [sp, #16]
  4007a8:	a8c27bfd 	ldp	x29, x30, [sp], #32
  4007ac:	d65f03c0 	ret

00000000004007b0 <frame_dummy>:
  4007b0:	17ffffe4 	b	400740 <register_tm_clones>

00000000004007b4 <dot_product>:
  4007b4:	7100005f 	cmp	w2, #0x0
  4007b8:	5400016d 	b.le	4007e4 <dot_product+0x30>
  4007bc:	d2800003 	mov	x3, #0x0                   	// #0
  4007c0:	0f000400 	movi	v0.2s, #0x0
  4007c4:	bc637801 	ldr	s1, [x0, x3, lsl #2]
  4007c8:	bc637822 	ldr	s2, [x1, x3, lsl #2]
  4007cc:	1e220821 	fmul	s1, s1, s2
  4007d0:	1e212800 	fadd	s0, s0, s1
  4007d4:	91000463 	add	x3, x3, #0x1
  4007d8:	6b03005f 	cmp	w2, w3
  4007dc:	54ffff4c 	b.gt	4007c4 <dot_product+0x10>
  4007e0:	d65f03c0 	ret
  4007e4:	0f000400 	movi	v0.2s, #0x0
  4007e8:	17fffffe 	b	4007e0 <dot_product+0x2c>

00000000004007ec <conditional_sum>:
  4007ec:	1e204002 	fmov	s2, s0
  4007f0:	7100003f 	cmp	w1, #0x0
  4007f4:	5400018d 	b.le	400824 <conditional_sum+0x38>
  4007f8:	d2800002 	mov	x2, #0x0                   	// #0
  4007fc:	0f000400 	movi	v0.2s, #0x0
  400800:	14000004 	b	400810 <conditional_sum+0x24>
  400804:	91000442 	add	x2, x2, #0x1
  400808:	6b02003f 	cmp	w1, w2
  40080c:	540000ed 	b.le	400828 <conditional_sum+0x3c>
  400810:	bc627801 	ldr	s1, [x0, x2, lsl #2]
  400814:	1e222030 	fcmpe	s1, s2
  400818:	54ffff6d 	b.le	400804 <conditional_sum+0x18>
  40081c:	1e212800 	fadd	s0, s0, s1
  400820:	17fffff9 	b	400804 <conditional_sum+0x18>
  400824:	0f000400 	movi	v0.2s, #0x0
  400828:	d65f03c0 	ret

000000000040082c <poly_eval>:
  40082c:	1e204002 	fmov	s2, s0
  400830:	71000421 	subs	w1, w1, #0x1
  400834:	54000124 	b.mi	400858 <poly_eval+0x2c>  // b.first
  400838:	93407c21 	sxtw	x1, w1
  40083c:	0f000400 	movi	v0.2s, #0x0
  400840:	1e200840 	fmul	s0, s2, s0
  400844:	bc617801 	ldr	s1, [x0, x1, lsl #2]
  400848:	1e212800 	fadd	s0, s0, s1
  40084c:	d1000421 	sub	x1, x1, #0x1
  400850:	36ffff81 	tbz	w1, #31, 400840 <poly_eval+0x14>
  400854:	d65f03c0 	ret
  400858:	0f000400 	movi	v0.2s, #0x0
  40085c:	17fffffe 	b	400854 <poly_eval+0x28>

0000000000400860 <dead_code_test>:
  400860:	d10043ff 	sub	sp, sp, #0x10
  400864:	529eb860 	mov	w0, #0xf5c3                	// #62915
  400868:	72a80900 	movk	w0, #0x4048, lsl #16
  40086c:	1e270001 	fmov	s1, w0
  400870:	1e210800 	fmul	s0, s0, s1
  400874:	bd000fe0 	str	s0, [sp, #12]
  400878:	910043ff 	add	sp, sp, #0x10
  40087c:	d65f03c0 	ret

0000000000400880 <manual_unroll>:
  400880:	71000c5f 	cmp	w2, #0x3
  400884:	5400048d 	b.le	400914 <manual_unroll+0x94>
  400888:	aa0103e3 	mov	x3, x1
  40088c:	aa0003e4 	mov	x4, x0
  400890:	51001047 	sub	w7, w2, #0x4
  400894:	53027ce5 	lsr	w5, w7, #2
  400898:	91004026 	add	x6, x1, #0x10
  40089c:	53027ce7 	lsr	w7, w7, #2
  4008a0:	8b0710c6 	add	x6, x6, x7, lsl #4
  4008a4:	bd400060 	ldr	s0, [x3]
  4008a8:	1e202800 	fadd	s0, s0, s0
  4008ac:	bd000080 	str	s0, [x4]
  4008b0:	bd400460 	ldr	s0, [x3, #4]
  4008b4:	1e202800 	fadd	s0, s0, s0
  4008b8:	bd000480 	str	s0, [x4, #4]
  4008bc:	bd400860 	ldr	s0, [x3, #8]
  4008c0:	1e202800 	fadd	s0, s0, s0
  4008c4:	bd000880 	str	s0, [x4, #8]
  4008c8:	bd400c60 	ldr	s0, [x3, #12]
  4008cc:	1e202800 	fadd	s0, s0, s0
  4008d0:	bd000c80 	str	s0, [x4, #12]
  4008d4:	91004063 	add	x3, x3, #0x10
  4008d8:	91004084 	add	x4, x4, #0x10
  4008dc:	eb06007f 	cmp	x3, x6
  4008e0:	54fffe21 	b.ne	4008a4 <manual_unroll+0x24>  // b.any
  4008e4:	110004a3 	add	w3, w5, #0x1
  4008e8:	531e7463 	lsl	w3, w3, #2
  4008ec:	6b03005f 	cmp	w2, w3
  4008f0:	5400010d 	b.le	400910 <manual_unroll+0x90>
  4008f4:	93407c63 	sxtw	x3, w3
  4008f8:	bc637820 	ldr	s0, [x1, x3, lsl #2]
  4008fc:	1e202800 	fadd	s0, s0, s0
  400900:	bc237800 	str	s0, [x0, x3, lsl #2]
  400904:	91000463 	add	x3, x3, #0x1
  400908:	6b03005f 	cmp	w2, w3
  40090c:	54ffff6c 	b.gt	4008f8 <manual_unroll+0x78>
  400910:	d65f03c0 	ret
  400914:	52800003 	mov	w3, #0x0                   	// #0
  400918:	17fffff5 	b	4008ec <manual_unroll+0x6c>

000000000040091c <bad_loop>:
  40091c:	2a0003e2 	mov	w2, w0
  400920:	7100001f 	cmp	w0, #0x0
  400924:	5400010d 	b.le	400944 <bad_loop+0x28>
  400928:	52800001 	mov	w1, #0x0                   	// #0
  40092c:	52800000 	mov	w0, #0x0                   	// #0
  400930:	0b010000 	add	w0, w0, w1
  400934:	11000421 	add	w1, w1, #0x1
  400938:	6b01005f 	cmp	w2, w1
  40093c:	54ffffa1 	b.ne	400930 <bad_loop+0x14>  // b.any
  400940:	d65f03c0 	ret
  400944:	52800000 	mov	w0, #0x0                   	// #0
  400948:	17fffffe 	b	400940 <bad_loop+0x24>

000000000040094c <main>:
  40094c:	d288120c 	mov	x12, #0x4090                	// #16528
  400950:	cb2c63ff 	sub	sp, sp, x12
  400954:	a9007bfd 	stp	x29, x30, [sp]
  400958:	910003fd 	mov	x29, sp
  40095c:	a90153f3 	stp	x19, x20, [sp, #16]
  400960:	a9025bf5 	stp	x21, x22, [sp, #32]
  400964:	6d0327e8 	stp	d8, d9, [sp, #48]
  400968:	6d042fea 	stp	d10, d11, [sp, #64]
  40096c:	52800540 	mov	w0, #0x2a                  	// #42
  400970:	97ffff40 	bl	400670 <srand@plt>
  400974:	d2800013 	mov	x19, #0x0                   	// #0
  400978:	d00000b5 	adrp	x21, 416000 <B+0x3fa0>
  40097c:	910182b5 	add	x21, x21, #0x60
  400980:	0f016608 	movi	v8.2s, #0x30, lsl #24
  400984:	d0000094 	adrp	x20, 412000 <clock_gettime@GLIBC_2.17>
  400988:	91018294 	add	x20, x20, #0x60
  40098c:	97ffff29 	bl	400630 <rand@plt>
  400990:	1e220000 	scvtf	s0, w0
  400994:	1e280800 	fmul	s0, s0, s8
  400998:	bc356a60 	str	s0, [x19, x21]
  40099c:	97ffff25 	bl	400630 <rand@plt>
  4009a0:	1e220000 	scvtf	s0, w0
  4009a4:	1e280800 	fmul	s0, s0, s8
  4009a8:	bc346a60 	str	s0, [x19, x20]
  4009ac:	91001273 	add	x19, x19, #0x4
  4009b0:	f140127f 	cmp	x19, #0x4, lsl #12
  4009b4:	54fffec1 	b.ne	40098c <main+0x40>  // b.any
  4009b8:	d00000b3 	adrp	x19, 416000 <B+0x3fa0>
  4009bc:	91018273 	add	x19, x19, #0x60
  4009c0:	52820002 	mov	w2, #0x1000                	// #4096
  4009c4:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  4009c8:	91018021 	add	x1, x1, #0x60
  4009cc:	aa1303e0 	mov	x0, x19
  4009d0:	97ffff79 	bl	4007b4 <dot_product>
  4009d4:	1e20400b 	fmov	s11, s0
  4009d8:	1e2c1000 	fmov	s0, #5.000000000000000000e-01
  4009dc:	52820001 	mov	w1, #0x1000                	// #4096
  4009e0:	aa1303e0 	mov	x0, x19
  4009e4:	97ffff82 	bl	4007ec <conditional_sum>
  4009e8:	1e20400a 	fmov	s10, s0
  4009ec:	90000001 	adrp	x1, 400000 <_init-0x5d0>
  4009f0:	913aa021 	add	x1, x1, #0xea8
  4009f4:	914013e0 	add	x0, sp, #0x4, lsl #12
  4009f8:	9101e000 	add	x0, x0, #0x78
  4009fc:	a9400c22 	ldp	x2, x3, [x1]
  400a00:	914013e4 	add	x4, sp, #0x4, lsl #12
  400a04:	a9078c82 	stp	x2, x3, [x4, #120]
  400a08:	b9401021 	ldr	w1, [x1, #16]
  400a0c:	b9001001 	str	w1, [x0, #16]
  400a10:	1e201000 	fmov	s0, #2.000000000000000000e+00
  400a14:	528000a1 	mov	w1, #0x5                   	// #5
  400a18:	97ffff85 	bl	40082c <poly_eval>
  400a1c:	1e204009 	fmov	s9, s0
  400a20:	52970a40 	mov	w0, #0xb852                	// #47186
  400a24:	72a812c0 	movk	w0, #0x4096, lsl #16
  400a28:	b90053e0 	str	w0, [sp, #80]
  400a2c:	52820002 	mov	w2, #0x1000                	// #4096
  400a30:	aa1303e1 	mov	x1, x19
  400a34:	9101e3e0 	add	x0, sp, #0x78
  400a38:	97ffff92 	bl	400880 <manual_unroll>
  400a3c:	9101a3e1 	add	x1, sp, #0x68
  400a40:	52800020 	mov	w0, #0x1                   	// #1
  400a44:	97fffef3 	bl	400610 <clock_gettime@plt>
  400a48:	b90057ff 	str	wzr, [sp, #84]
  400a4c:	52807d13 	mov	w19, #0x3e8                 	// #1000
  400a50:	d0000095 	adrp	x21, 412000 <clock_gettime@GLIBC_2.17>
  400a54:	910182b5 	add	x21, x21, #0x60
  400a58:	d00000b4 	adrp	x20, 416000 <B+0x3fa0>
  400a5c:	91018294 	add	x20, x20, #0x60
  400a60:	52820016 	mov	w22, #0x1000                	// #4096
  400a64:	2a1603e2 	mov	w2, w22
  400a68:	aa1503e1 	mov	x1, x21
  400a6c:	aa1403e0 	mov	x0, x20
  400a70:	97ffff51 	bl	4007b4 <dot_product>
  400a74:	bd4057e1 	ldr	s1, [sp, #84]
  400a78:	1e202821 	fadd	s1, s1, s0
  400a7c:	bd0057e1 	str	s1, [sp, #84]
  400a80:	71000673 	subs	w19, w19, #0x1
  400a84:	54ffff01 	b.ne	400a64 <main+0x118>  // b.any
  400a88:	910163e1 	add	x1, sp, #0x58
  400a8c:	52800020 	mov	w0, #0x1                   	// #1
  400a90:	97fffee0 	bl	400610 <clock_gettime@plt>
  400a94:	f9402fe0 	ldr	x0, [sp, #88]
  400a98:	f94037e1 	ldr	x1, [sp, #104]
  400a9c:	cb010000 	sub	x0, x0, x1
  400aa0:	9e670008 	fmov	d8, x0
  400aa4:	5e61d908 	scvtf	d8, d8
  400aa8:	d2c80000 	mov	x0, #0x400000000000        	// #70368744177664
  400aac:	f2e811e0 	movk	x0, #0x408f, lsl #48
  400ab0:	9e670000 	fmov	d0, x0
  400ab4:	1e600908 	fmul	d8, d8, d0
  400ab8:	f94033e0 	ldr	x0, [sp, #96]
  400abc:	f9403be1 	ldr	x1, [sp, #112]
  400ac0:	cb010000 	sub	x0, x0, x1
  400ac4:	9e670000 	fmov	d0, x0
  400ac8:	5e61d800 	scvtf	d0, d0
  400acc:	d2d09000 	mov	x0, #0x848000000000        	// #145685290680320
  400ad0:	f2e825c0 	movk	x0, #0x412e, lsl #48
  400ad4:	9e670001 	fmov	d1, x0
  400ad8:	1e611800 	fdiv	d0, d0, d1
  400adc:	1e602908 	fadd	d8, d8, d0
  400ae0:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400ae4:	91328000 	add	x0, x0, #0xca0
  400ae8:	97fffede 	bl	400660 <puts@plt>
  400aec:	1e22c160 	fcvt	d0, s11
  400af0:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400af4:	91338000 	add	x0, x0, #0xce0
  400af8:	97fffee2 	bl	400680 <printf@plt>
  400afc:	1e22c140 	fcvt	d0, s10
  400b00:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b04:	9133e000 	add	x0, x0, #0xcf8
  400b08:	97fffede 	bl	400680 <printf@plt>
  400b0c:	1e22c120 	fcvt	d0, s9
  400b10:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b14:	91344000 	add	x0, x0, #0xd10
  400b18:	97fffeda 	bl	400680 <printf@plt>
  400b1c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b20:	fd475000 	ldr	d0, [x0, #3744]
  400b24:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b28:	9134a000 	add	x0, x0, #0xd28
  400b2c:	97fffed5 	bl	400680 <printf@plt>
  400b30:	bd4087e3 	ldr	s3, [sp, #132]
  400b34:	1e22c063 	fcvt	d3, s3
  400b38:	bd4083e2 	ldr	s2, [sp, #128]
  400b3c:	1e22c042 	fcvt	d2, s2
  400b40:	bd407fe1 	ldr	s1, [sp, #124]
  400b44:	1e22c021 	fcvt	d1, s1
  400b48:	bd407be0 	ldr	s0, [sp, #120]
  400b4c:	1e22c000 	fcvt	d0, s0
  400b50:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b54:	91350000 	add	x0, x0, #0xd40
  400b58:	97fffeca 	bl	400680 <printf@plt>
  400b5c:	52800140 	mov	w0, #0xa                   	// #10
  400b60:	97fffecc 	bl	400690 <putchar@plt>
  400b64:	1e604100 	fmov	d0, d8
  400b68:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b6c:	9135c000 	add	x0, x0, #0xd70
  400b70:	97fffec4 	bl	400680 <printf@plt>
  400b74:	52800140 	mov	w0, #0xa                   	// #10
  400b78:	97fffec6 	bl	400690 <putchar@plt>
  400b7c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b80:	91366000 	add	x0, x0, #0xd98
  400b84:	97fffeb7 	bl	400660 <puts@plt>
  400b88:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b8c:	9136c000 	add	x0, x0, #0xdb0
  400b90:	97fffeb4 	bl	400660 <puts@plt>
  400b94:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400b98:	9137a000 	add	x0, x0, #0xde8
  400b9c:	97fffeb1 	bl	400660 <puts@plt>
  400ba0:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400ba4:	91386000 	add	x0, x0, #0xe18
  400ba8:	97fffeae 	bl	400660 <puts@plt>
  400bac:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400bb0:	91390000 	add	x0, x0, #0xe40
  400bb4:	97fffeab 	bl	400660 <puts@plt>
  400bb8:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400bbc:	9139c000 	add	x0, x0, #0xe70
  400bc0:	97fffea8 	bl	400660 <puts@plt>
  400bc4:	bd4057e0 	ldr	s0, [sp, #84]
  400bc8:	52800000 	mov	w0, #0x0                   	// #0
  400bcc:	6d4327e8 	ldp	d8, d9, [sp, #48]
  400bd0:	6d442fea 	ldp	d10, d11, [sp, #64]
  400bd4:	a94153f3 	ldp	x19, x20, [sp, #16]
  400bd8:	a9425bf5 	ldp	x21, x22, [sp, #32]
  400bdc:	a9407bfd 	ldp	x29, x30, [sp]
  400be0:	d288120c 	mov	x12, #0x4090                	// #16528
  400be4:	8b2c63ff 	add	sp, sp, x12
  400be8:	d65f03c0 	ret
  400bec:	d503201f 	nop

0000000000400bf0 <__libc_csu_init>:
  400bf0:	a9bc7bfd 	stp	x29, x30, [sp, #-64]!
  400bf4:	910003fd 	mov	x29, sp
  400bf8:	a90153f3 	stp	x19, x20, [sp, #16]
  400bfc:	b0000094 	adrp	x20, 411000 <__FRAME_END__+0xff48>
  400c00:	91378294 	add	x20, x20, #0xde0
  400c04:	a9025bf5 	stp	x21, x22, [sp, #32]
  400c08:	b0000095 	adrp	x21, 411000 <__FRAME_END__+0xff48>
  400c0c:	913762b5 	add	x21, x21, #0xdd8
  400c10:	cb150294 	sub	x20, x20, x21
  400c14:	2a0003f6 	mov	w22, w0
  400c18:	a90363f7 	stp	x23, x24, [sp, #48]
  400c1c:	aa0103f7 	mov	x23, x1
  400c20:	aa0203f8 	mov	x24, x2
  400c24:	97fffe6b 	bl	4005d0 <_init>
  400c28:	eb940fff 	cmp	xzr, x20, asr #3
  400c2c:	54000160 	b.eq	400c58 <__libc_csu_init+0x68>  // b.none
  400c30:	9343fe94 	asr	x20, x20, #3
  400c34:	d2800013 	mov	x19, #0x0                   	// #0
  400c38:	f8737aa3 	ldr	x3, [x21, x19, lsl #3]
  400c3c:	aa1803e2 	mov	x2, x24
  400c40:	91000673 	add	x19, x19, #0x1
  400c44:	aa1703e1 	mov	x1, x23
  400c48:	2a1603e0 	mov	w0, w22
  400c4c:	d63f0060 	blr	x3
  400c50:	eb13029f 	cmp	x20, x19
  400c54:	54ffff21 	b.ne	400c38 <__libc_csu_init+0x48>  // b.any
  400c58:	a94153f3 	ldp	x19, x20, [sp, #16]
  400c5c:	a9425bf5 	ldp	x21, x22, [sp, #32]
  400c60:	a94363f7 	ldp	x23, x24, [sp, #48]
  400c64:	a8c47bfd 	ldp	x29, x30, [sp], #64
  400c68:	d65f03c0 	ret
  400c6c:	d503201f 	nop

0000000000400c70 <__libc_csu_fini>:
  400c70:	d65f03c0 	ret

Disassembly of section .fini:

0000000000400c74 <_fini>:
  400c74:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  400c78:	910003fd 	mov	x29, sp
  400c7c:	a8c17bfd 	ldp	x29, x30, [sp], #16
  400c80:	d65f03c0 	ret
