
build/opt_O2：     文件格式 elf64-littleaarch64


Disassembly of section .init:

00000000004005d0 <_init>:
  4005d0:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  4005d4:	910003fd 	mov	x29, sp
  4005d8:	940000e4 	bl	400968 <call_weak_fn>
  4005dc:	a8c17bfd 	ldp	x29, x30, [sp], #16
  4005e0:	d65f03c0 	ret

Disassembly of section .plt:

00000000004005f0 <.plt>:
  4005f0:	a9bf7bf0 	stp	x16, x30, [sp, #-16]!
  4005f4:	b0000090 	adrp	x16, 411000 <__FRAME_END__+0xff80>
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
  4006a0:	d2880e0c 	mov	x12, #0x4070                	// #16496
  4006a4:	cb2c63ff 	sub	sp, sp, x12
  4006a8:	52800540 	mov	w0, #0x2a                  	// #42
  4006ac:	a9007bfd 	stp	x29, x30, [sp]
  4006b0:	910003fd 	mov	x29, sp
  4006b4:	6d0327e8 	stp	d8, d9, [sp, #48]
  4006b8:	0f016608 	movi	v8.2s, #0x30, lsl #24
  4006bc:	a90153f3 	stp	x19, x20, [sp, #16]
  4006c0:	d00000b3 	adrp	x19, 416000 <B+0x3fa0>
  4006c4:	d0000094 	adrp	x20, 412000 <clock_gettime@GLIBC_2.17>
  4006c8:	91018273 	add	x19, x19, #0x60
  4006cc:	91018294 	add	x20, x20, #0x60
  4006d0:	f90013f5 	str	x21, [sp, #32]
  4006d4:	d2800015 	mov	x21, #0x0                   	// #0
  4006d8:	fd0017ea 	str	d10, [sp, #40]
  4006dc:	97ffffe5 	bl	400670 <srand@plt>
  4006e0:	97ffffd4 	bl	400630 <rand@plt>
  4006e4:	1e220000 	scvtf	s0, w0
  4006e8:	1e280800 	fmul	s0, s0, s8
  4006ec:	bc356a60 	str	s0, [x19, x21]
  4006f0:	97ffffd0 	bl	400630 <rand@plt>
  4006f4:	1e220000 	scvtf	s0, w0
  4006f8:	1e280800 	fmul	s0, s0, s8
  4006fc:	bc356a80 	str	s0, [x20, x21]
  400700:	910012b5 	add	x21, x21, #0x4
  400704:	f14012bf 	cmp	x21, #0x4, lsl #12
  400708:	54fffec1 	b.ne	4006e0 <main+0x40>  // b.any
  40070c:	0f000408 	movi	v8.2s, #0x0
  400710:	d2800000 	mov	x0, #0x0                   	// #0
  400714:	bc606a61 	ldr	s1, [x19, x0]
  400718:	bc606a80 	ldr	s0, [x20, x0]
  40071c:	91001000 	add	x0, x0, #0x4
  400720:	f140101f 	cmp	x0, #0x4, lsl #12
  400724:	1f002028 	fmadd	s8, s1, s0, s8
  400728:	54ffff61 	b.ne	400714 <main+0x74>  // b.any
  40072c:	0f00040a 	movi	v10.2s, #0x0
  400730:	aa1303e0 	mov	x0, x19
  400734:	91401261 	add	x1, x19, #0x4, lsl #12
  400738:	1e2c1000 	fmov	s0, #5.000000000000000000e-01
  40073c:	bd400001 	ldr	s1, [x0]
  400740:	91001000 	add	x0, x0, #0x4
  400744:	1e202030 	fcmpe	s1, s0
  400748:	5400004d 	b.le	400750 <main+0xb0>
  40074c:	1e21294a 	fadd	s10, s10, s1
  400750:	eb01001f 	cmp	x0, x1
  400754:	54ffff41 	b.ne	40073c <main+0x9c>  // b.any
  400758:	52970a40 	mov	w0, #0xb852                	// #47186
  40075c:	52820002 	mov	w2, #0x1000                	// #4096
  400760:	72a812c0 	movk	w0, #0x4096, lsl #16
  400764:	1e270000 	fmov	s0, w0
  400768:	aa1303e1 	mov	x1, x19
  40076c:	9101c3e0 	add	x0, sp, #0x70
  400770:	bd004fe0 	str	s0, [sp, #76]
  400774:	940000df 	bl	400af0 <manual_unroll>
  400778:	910143e1 	add	x1, sp, #0x50
  40077c:	52800020 	mov	w0, #0x1                   	// #1
  400780:	97ffffa4 	bl	400610 <clock_gettime@plt>
  400784:	b9004bff 	str	wzr, [sp, #72]
  400788:	52807d01 	mov	w1, #0x3e8                 	// #1000
  40078c:	d503201f 	nop
  400790:	0f000401 	movi	v1.2s, #0x0
  400794:	d2800000 	mov	x0, #0x0                   	// #0
  400798:	bc606a63 	ldr	s3, [x19, x0]
  40079c:	bc606a82 	ldr	s2, [x20, x0]
  4007a0:	91001000 	add	x0, x0, #0x4
  4007a4:	f140101f 	cmp	x0, #0x4, lsl #12
  4007a8:	1f020461 	fmadd	s1, s3, s2, s1
  4007ac:	54ffff61 	b.ne	400798 <main+0xf8>  // b.any
  4007b0:	bd404be2 	ldr	s2, [sp, #72]
  4007b4:	71000421 	subs	w1, w1, #0x1
  4007b8:	1e212841 	fadd	s1, s2, s1
  4007bc:	bd004be1 	str	s1, [sp, #72]
  4007c0:	54fffe81 	b.ne	400790 <main+0xf0>  // b.any
  4007c4:	910183e1 	add	x1, sp, #0x60
  4007c8:	52800020 	mov	w0, #0x1                   	// #1
  4007cc:	97ffff91 	bl	400610 <clock_gettime@plt>
  4007d0:	a94507e3 	ldp	x3, x1, [sp, #80]
  4007d4:	d2d09000 	mov	x0, #0x848000000000        	// #145685290680320
  4007d8:	f2e825c0 	movk	x0, #0x412e, lsl #48
  4007dc:	9e670000 	fmov	d0, x0
  4007e0:	f94037e0 	ldr	x0, [sp, #104]
  4007e4:	d2c80002 	mov	x2, #0x400000000000        	// #70368744177664
  4007e8:	f2e811e2 	movk	x2, #0x408f, lsl #48
  4007ec:	9e670041 	fmov	d1, x2
  4007f0:	cb010000 	sub	x0, x0, x1
  4007f4:	f94033e1 	ldr	x1, [sp, #96]
  4007f8:	9e620009 	scvtf	d9, x0
  4007fc:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400800:	9131e000 	add	x0, x0, #0xc78
  400804:	cb030021 	sub	x1, x1, x3
  400808:	1e601929 	fdiv	d9, d9, d0
  40080c:	9e620020 	scvtf	d0, x1
  400810:	1f412409 	fmadd	d9, d0, d1, d9
  400814:	97ffff93 	bl	400660 <puts@plt>
  400818:	1e22c100 	fcvt	d0, s8
  40081c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400820:	9132e000 	add	x0, x0, #0xcb8
  400824:	97ffff97 	bl	400680 <printf@plt>
  400828:	1e22c140 	fcvt	d0, s10
  40082c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400830:	91334000 	add	x0, x0, #0xcd0
  400834:	97ffff93 	bl	400680 <printf@plt>
  400838:	d2c40000 	mov	x0, #0x200000000000        	// #35184372088832
  40083c:	f2e80c00 	movk	x0, #0x4060, lsl #48
  400840:	9e670000 	fmov	d0, x0
  400844:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400848:	9133a000 	add	x0, x0, #0xce8
  40084c:	97ffff8d 	bl	400680 <printf@plt>
  400850:	90000001 	adrp	x1, 400000 <_init-0x5d0>
  400854:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400858:	91340000 	add	x0, x0, #0xd00
  40085c:	fd473c20 	ldr	d0, [x1, #3704]
  400860:	97ffff88 	bl	400680 <printf@plt>
  400864:	2d4e07e0 	ldp	s0, s1, [sp, #112]
  400868:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  40086c:	2d4f0fe2 	ldp	s2, s3, [sp, #120]
  400870:	91346000 	add	x0, x0, #0xd18
  400874:	1e22c021 	fcvt	d1, s1
  400878:	1e22c000 	fcvt	d0, s0
  40087c:	1e22c042 	fcvt	d2, s2
  400880:	1e22c063 	fcvt	d3, s3
  400884:	97ffff7f 	bl	400680 <printf@plt>
  400888:	52800140 	mov	w0, #0xa                   	// #10
  40088c:	97ffff81 	bl	400690 <putchar@plt>
  400890:	1e604120 	fmov	d0, d9
  400894:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400898:	91352000 	add	x0, x0, #0xd48
  40089c:	97ffff79 	bl	400680 <printf@plt>
  4008a0:	52800140 	mov	w0, #0xa                   	// #10
  4008a4:	97ffff7b 	bl	400690 <putchar@plt>
  4008a8:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008ac:	9135c000 	add	x0, x0, #0xd70
  4008b0:	97ffff6c 	bl	400660 <puts@plt>
  4008b4:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008b8:	91362000 	add	x0, x0, #0xd88
  4008bc:	97ffff69 	bl	400660 <puts@plt>
  4008c0:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008c4:	91370000 	add	x0, x0, #0xdc0
  4008c8:	97ffff66 	bl	400660 <puts@plt>
  4008cc:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008d0:	9137c000 	add	x0, x0, #0xdf0
  4008d4:	97ffff63 	bl	400660 <puts@plt>
  4008d8:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008dc:	91386000 	add	x0, x0, #0xe18
  4008e0:	97ffff60 	bl	400660 <puts@plt>
  4008e4:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008e8:	91392000 	add	x0, x0, #0xe48
  4008ec:	97ffff5d 	bl	400660 <puts@plt>
  4008f0:	52800000 	mov	w0, #0x0                   	// #0
  4008f4:	d2880e0c 	mov	x12, #0x4070                	// #16496
  4008f8:	a9407bfd 	ldp	x29, x30, [sp]
  4008fc:	a94153f3 	ldp	x19, x20, [sp, #16]
  400900:	f94013f5 	ldr	x21, [sp, #32]
  400904:	fd4017ea 	ldr	d10, [sp, #40]
  400908:	6d4327e8 	ldp	d8, d9, [sp, #48]
  40090c:	bd404be0 	ldr	s0, [sp, #72]
  400910:	8b2c63ff 	add	sp, sp, x12
  400914:	d65f03c0 	ret

0000000000400918 <_start>:
  400918:	d280001d 	mov	x29, #0x0                   	// #0
  40091c:	d280001e 	mov	x30, #0x0                   	// #0
  400920:	aa0003e5 	mov	x5, x0
  400924:	f94003e1 	ldr	x1, [sp]
  400928:	910023e2 	add	x2, sp, #0x8
  40092c:	910003e6 	mov	x6, sp
  400930:	d2e00000 	movz	x0, #0x0, lsl #48
  400934:	f2c00000 	movk	x0, #0x0, lsl #32
  400938:	f2a00800 	movk	x0, #0x40, lsl #16
  40093c:	f280d400 	movk	x0, #0x6a0
  400940:	d2e00003 	movz	x3, #0x0, lsl #48
  400944:	f2c00003 	movk	x3, #0x0, lsl #32
  400948:	f2a00803 	movk	x3, #0x40, lsl #16
  40094c:	f2817903 	movk	x3, #0xbc8
  400950:	d2e00004 	movz	x4, #0x0, lsl #48
  400954:	f2c00004 	movk	x4, #0x0, lsl #32
  400958:	f2a00804 	movk	x4, #0x40, lsl #16
  40095c:	f2818904 	movk	x4, #0xc48
  400960:	97ffff30 	bl	400620 <__libc_start_main@plt>
  400964:	97ffff3b 	bl	400650 <abort@plt>

0000000000400968 <call_weak_fn>:
  400968:	b0000080 	adrp	x0, 411000 <__FRAME_END__+0xff80>
  40096c:	f947f000 	ldr	x0, [x0, #4064]
  400970:	b4000040 	cbz	x0, 400978 <call_weak_fn+0x10>
  400974:	17ffff33 	b	400640 <__gmon_start__@plt>
  400978:	d65f03c0 	ret
  40097c:	d503201f 	nop

0000000000400980 <deregister_tm_clones>:
  400980:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400984:	91016000 	add	x0, x0, #0x58
  400988:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  40098c:	91016021 	add	x1, x1, #0x58
  400990:	eb00003f 	cmp	x1, x0
  400994:	540000c0 	b.eq	4009ac <deregister_tm_clones+0x2c>  // b.none
  400998:	90000001 	adrp	x1, 400000 <_init-0x5d0>
  40099c:	f9463421 	ldr	x1, [x1, #3176]
  4009a0:	b4000061 	cbz	x1, 4009ac <deregister_tm_clones+0x2c>
  4009a4:	aa0103f0 	mov	x16, x1
  4009a8:	d61f0200 	br	x16
  4009ac:	d65f03c0 	ret

00000000004009b0 <register_tm_clones>:
  4009b0:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  4009b4:	91016000 	add	x0, x0, #0x58
  4009b8:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  4009bc:	91016021 	add	x1, x1, #0x58
  4009c0:	cb000021 	sub	x1, x1, x0
  4009c4:	d37ffc22 	lsr	x2, x1, #63
  4009c8:	8b810c41 	add	x1, x2, x1, asr #3
  4009cc:	eb8107ff 	cmp	xzr, x1, asr #1
  4009d0:	9341fc21 	asr	x1, x1, #1
  4009d4:	540000c0 	b.eq	4009ec <register_tm_clones+0x3c>  // b.none
  4009d8:	90000002 	adrp	x2, 400000 <_init-0x5d0>
  4009dc:	f9463842 	ldr	x2, [x2, #3184]
  4009e0:	b4000062 	cbz	x2, 4009ec <register_tm_clones+0x3c>
  4009e4:	aa0203f0 	mov	x16, x2
  4009e8:	d61f0200 	br	x16
  4009ec:	d65f03c0 	ret

00000000004009f0 <__do_global_dtors_aux>:
  4009f0:	a9be7bfd 	stp	x29, x30, [sp, #-32]!
  4009f4:	910003fd 	mov	x29, sp
  4009f8:	f9000bf3 	str	x19, [sp, #16]
  4009fc:	d0000093 	adrp	x19, 412000 <clock_gettime@GLIBC_2.17>
  400a00:	39416260 	ldrb	w0, [x19, #88]
  400a04:	35000080 	cbnz	w0, 400a14 <__do_global_dtors_aux+0x24>
  400a08:	97ffffde 	bl	400980 <deregister_tm_clones>
  400a0c:	52800020 	mov	w0, #0x1                   	// #1
  400a10:	39016260 	strb	w0, [x19, #88]
  400a14:	f9400bf3 	ldr	x19, [sp, #16]
  400a18:	a8c27bfd 	ldp	x29, x30, [sp], #32
  400a1c:	d65f03c0 	ret

0000000000400a20 <frame_dummy>:
  400a20:	17ffffe4 	b	4009b0 <register_tm_clones>
  400a24:	d503201f 	nop
  400a28:	d503201f 	nop
  400a2c:	d503201f 	nop

0000000000400a30 <dot_product>:
  400a30:	0f000400 	movi	v0.2s, #0x0
  400a34:	7100005f 	cmp	w2, #0x0
  400a38:	5400010d 	b.le	400a58 <dot_product+0x28>
  400a3c:	d2800003 	mov	x3, #0x0                   	// #0
  400a40:	bc637802 	ldr	s2, [x0, x3, lsl #2]
  400a44:	bc637821 	ldr	s1, [x1, x3, lsl #2]
  400a48:	91000463 	add	x3, x3, #0x1
  400a4c:	6b03005f 	cmp	w2, w3
  400a50:	1f010040 	fmadd	s0, s2, s1, s0
  400a54:	54ffff6c 	b.gt	400a40 <dot_product+0x10>
  400a58:	d65f03c0 	ret
  400a5c:	d503201f 	nop

0000000000400a60 <conditional_sum>:
  400a60:	1e204002 	fmov	s2, s0
  400a64:	7100003f 	cmp	w1, #0x0
  400a68:	0f000400 	movi	v0.2s, #0x0
  400a6c:	5400014d 	b.le	400a94 <conditional_sum+0x34>
  400a70:	d2800002 	mov	x2, #0x0                   	// #0
  400a74:	d503201f 	nop
  400a78:	bc627801 	ldr	s1, [x0, x2, lsl #2]
  400a7c:	91000442 	add	x2, x2, #0x1
  400a80:	1e222030 	fcmpe	s1, s2
  400a84:	5400004d 	b.le	400a8c <conditional_sum+0x2c>
  400a88:	1e212800 	fadd	s0, s0, s1
  400a8c:	6b02003f 	cmp	w1, w2
  400a90:	54ffff4c 	b.gt	400a78 <conditional_sum+0x18>
  400a94:	d65f03c0 	ret
  400a98:	d503201f 	nop
  400a9c:	d503201f 	nop

0000000000400aa0 <poly_eval>:
  400aa0:	1e204002 	fmov	s2, s0
  400aa4:	71000421 	subs	w1, w1, #0x1
  400aa8:	0f000400 	movi	v0.2s, #0x0
  400aac:	540000e4 	b.mi	400ac8 <poly_eval+0x28>  // b.first
  400ab0:	93407c21 	sxtw	x1, w1
  400ab4:	d503201f 	nop
  400ab8:	bc617801 	ldr	s1, [x0, x1, lsl #2]
  400abc:	d1000421 	sub	x1, x1, #0x1
  400ac0:	1f000440 	fmadd	s0, s2, s0, s1
  400ac4:	36ffffa1 	tbz	w1, #31, 400ab8 <poly_eval+0x18>
  400ac8:	d65f03c0 	ret
  400acc:	d503201f 	nop

0000000000400ad0 <dead_code_test>:
  400ad0:	529eb860 	mov	w0, #0xf5c3                	// #62915
  400ad4:	d10043ff 	sub	sp, sp, #0x10
  400ad8:	72a80900 	movk	w0, #0x4048, lsl #16
  400adc:	1e270001 	fmov	s1, w0
  400ae0:	1e210800 	fmul	s0, s0, s1
  400ae4:	bd000fe0 	str	s0, [sp, #12]
  400ae8:	910043ff 	add	sp, sp, #0x10
  400aec:	d65f03c0 	ret

0000000000400af0 <manual_unroll>:
  400af0:	71000c5f 	cmp	w2, #0x3
  400af4:	5400046d 	b.le	400b80 <manual_unroll+0x90>
  400af8:	51001045 	sub	w5, w2, #0x4
  400afc:	91004026 	add	x6, x1, #0x10
  400b00:	aa0103e3 	mov	x3, x1
  400b04:	aa0003e4 	mov	x4, x0
  400b08:	53027ca5 	lsr	w5, w5, #2
  400b0c:	8b2550c6 	add	x6, x6, w5, uxtw #4
  400b10:	bd400060 	ldr	s0, [x3]
  400b14:	91004063 	add	x3, x3, #0x10
  400b18:	91004084 	add	x4, x4, #0x10
  400b1c:	1e202800 	fadd	s0, s0, s0
  400b20:	bc1f0080 	stur	s0, [x4, #-16]
  400b24:	bc5f4060 	ldur	s0, [x3, #-12]
  400b28:	1e202800 	fadd	s0, s0, s0
  400b2c:	bc1f4080 	stur	s0, [x4, #-12]
  400b30:	bc5f8060 	ldur	s0, [x3, #-8]
  400b34:	1e202800 	fadd	s0, s0, s0
  400b38:	bc1f8080 	stur	s0, [x4, #-8]
  400b3c:	bc5fc060 	ldur	s0, [x3, #-4]
  400b40:	eb06007f 	cmp	x3, x6
  400b44:	1e202800 	fadd	s0, s0, s0
  400b48:	bc1fc080 	stur	s0, [x4, #-4]
  400b4c:	54fffe21 	b.ne	400b10 <manual_unroll+0x20>  // b.any
  400b50:	110004a3 	add	w3, w5, #0x1
  400b54:	531e7463 	lsl	w3, w3, #2
  400b58:	6b03005f 	cmp	w2, w3
  400b5c:	5400010d 	b.le	400b7c <manual_unroll+0x8c>
  400b60:	93407c63 	sxtw	x3, w3
  400b64:	bc637820 	ldr	s0, [x1, x3, lsl #2]
  400b68:	1e202800 	fadd	s0, s0, s0
  400b6c:	bc237800 	str	s0, [x0, x3, lsl #2]
  400b70:	91000463 	add	x3, x3, #0x1
  400b74:	6b03005f 	cmp	w2, w3
  400b78:	54ffff6c 	b.gt	400b64 <manual_unroll+0x74>
  400b7c:	d65f03c0 	ret
  400b80:	52800003 	mov	w3, #0x0                   	// #0
  400b84:	17fffff5 	b	400b58 <manual_unroll+0x68>
  400b88:	d503201f 	nop
  400b8c:	d503201f 	nop

0000000000400b90 <bad_loop>:
  400b90:	2a0003e2 	mov	w2, w0
  400b94:	7100001f 	cmp	w0, #0x0
  400b98:	5400012d 	b.le	400bbc <bad_loop+0x2c>
  400b9c:	52800001 	mov	w1, #0x0                   	// #0
  400ba0:	52800000 	mov	w0, #0x0                   	// #0
  400ba4:	d503201f 	nop
  400ba8:	0b010000 	add	w0, w0, w1
  400bac:	11000421 	add	w1, w1, #0x1
  400bb0:	6b01005f 	cmp	w2, w1
  400bb4:	54ffffa1 	b.ne	400ba8 <bad_loop+0x18>  // b.any
  400bb8:	d65f03c0 	ret
  400bbc:	52800000 	mov	w0, #0x0                   	// #0
  400bc0:	d65f03c0 	ret
  400bc4:	d503201f 	nop

0000000000400bc8 <__libc_csu_init>:
  400bc8:	a9bc7bfd 	stp	x29, x30, [sp, #-64]!
  400bcc:	910003fd 	mov	x29, sp
  400bd0:	a90153f3 	stp	x19, x20, [sp, #16]
  400bd4:	b0000094 	adrp	x20, 411000 <__FRAME_END__+0xff80>
  400bd8:	91378294 	add	x20, x20, #0xde0
  400bdc:	a9025bf5 	stp	x21, x22, [sp, #32]
  400be0:	b0000095 	adrp	x21, 411000 <__FRAME_END__+0xff80>
  400be4:	913762b5 	add	x21, x21, #0xdd8
  400be8:	cb150294 	sub	x20, x20, x21
  400bec:	2a0003f6 	mov	w22, w0
  400bf0:	a90363f7 	stp	x23, x24, [sp, #48]
  400bf4:	aa0103f7 	mov	x23, x1
  400bf8:	aa0203f8 	mov	x24, x2
  400bfc:	97fffe75 	bl	4005d0 <_init>
  400c00:	eb940fff 	cmp	xzr, x20, asr #3
  400c04:	54000160 	b.eq	400c30 <__libc_csu_init+0x68>  // b.none
  400c08:	9343fe94 	asr	x20, x20, #3
  400c0c:	d2800013 	mov	x19, #0x0                   	// #0
  400c10:	f8737aa3 	ldr	x3, [x21, x19, lsl #3]
  400c14:	aa1803e2 	mov	x2, x24
  400c18:	91000673 	add	x19, x19, #0x1
  400c1c:	aa1703e1 	mov	x1, x23
  400c20:	2a1603e0 	mov	w0, w22
  400c24:	d63f0060 	blr	x3
  400c28:	eb13029f 	cmp	x20, x19
  400c2c:	54ffff21 	b.ne	400c10 <__libc_csu_init+0x48>  // b.any
  400c30:	a94153f3 	ldp	x19, x20, [sp, #16]
  400c34:	a9425bf5 	ldp	x21, x22, [sp, #32]
  400c38:	a94363f7 	ldp	x23, x24, [sp, #48]
  400c3c:	a8c47bfd 	ldp	x29, x30, [sp], #64
  400c40:	d65f03c0 	ret
  400c44:	d503201f 	nop

0000000000400c48 <__libc_csu_fini>:
  400c48:	d65f03c0 	ret

Disassembly of section .fini:

0000000000400c4c <_fini>:
  400c4c:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  400c50:	910003fd 	mov	x29, sp
  400c54:	a8c17bfd 	ldp	x29, x30, [sp], #16
  400c58:	d65f03c0 	ret
