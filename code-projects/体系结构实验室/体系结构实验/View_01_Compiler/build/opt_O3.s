
build/opt_O3：     文件格式 elf64-littleaarch64


Disassembly of section .init:

00000000004005d0 <_init>:
  4005d0:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  4005d4:	910003fd 	mov	x29, sp
  4005d8:	940000f4 	bl	4009a8 <call_weak_fn>
  4005dc:	a8c17bfd 	ldp	x29, x30, [sp], #16
  4005e0:	d65f03c0 	ret

Disassembly of section .plt:

00000000004005f0 <.plt>:
  4005f0:	a9bf7bf0 	stp	x16, x30, [sp, #-16]!
  4005f4:	b0000090 	adrp	x16, 411000 <__FRAME_END__+0xfda8>
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
  4006c0:	d00000b3 	adrp	x19, 416000 <B+0x3f90>
  4006c4:	d0000094 	adrp	x20, 412000 <clock_gettime@GLIBC_2.17>
  4006c8:	9101c273 	add	x19, x19, #0x70
  4006cc:	9101c294 	add	x20, x20, #0x70
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
  400714:	3ce06a60 	ldr	q0, [x19, x0]
  400718:	3ce06a81 	ldr	q1, [x20, x0]
  40071c:	91004000 	add	x0, x0, #0x10
  400720:	f140101f 	cmp	x0, #0x4, lsl #12
  400724:	6e20dc21 	fmul	v1.4s, v1.4s, v0.4s
  400728:	5e040423 	mov	s3, v1.s[0]
  40072c:	5e0c0422 	mov	s2, v1.s[1]
  400730:	5e140424 	mov	s4, v1.s[2]
  400734:	5e1c0421 	mov	s1, v1.s[3]
  400738:	1e282860 	fadd	s0, s3, s8
  40073c:	1e202840 	fadd	s0, s2, s0
  400740:	1e242800 	fadd	s0, s0, s4
  400744:	1e212808 	fadd	s8, s0, s1
  400748:	54fffe61 	b.ne	400714 <main+0x74>  // b.any
  40074c:	0f00040a 	movi	v10.2s, #0x0
  400750:	aa1303e0 	mov	x0, x19
  400754:	91401261 	add	x1, x19, #0x4, lsl #12
  400758:	1e2c1000 	fmov	s0, #5.000000000000000000e-01
  40075c:	bd400001 	ldr	s1, [x0]
  400760:	91001000 	add	x0, x0, #0x4
  400764:	1e202030 	fcmpe	s1, s0
  400768:	5400004d 	b.le	400770 <main+0xd0>
  40076c:	1e21294a 	fadd	s10, s10, s1
  400770:	eb00003f 	cmp	x1, x0
  400774:	54ffff41 	b.ne	40075c <main+0xbc>  // b.any
  400778:	52970a40 	mov	w0, #0xb852                	// #47186
  40077c:	52820002 	mov	w2, #0x1000                	// #4096
  400780:	72a812c0 	movk	w0, #0x4096, lsl #16
  400784:	1e270000 	fmov	s0, w0
  400788:	aa1303e1 	mov	x1, x19
  40078c:	9101c3e0 	add	x0, sp, #0x70
  400790:	bd004fe0 	str	s0, [sp, #76]
  400794:	9400010f 	bl	400bd0 <manual_unroll>
  400798:	910143e1 	add	x1, sp, #0x50
  40079c:	52800020 	mov	w0, #0x1                   	// #1
  4007a0:	97ffff9c 	bl	400610 <clock_gettime@plt>
  4007a4:	b9004bff 	str	wzr, [sp, #72]
  4007a8:	52807d01 	mov	w1, #0x3e8                 	// #1000
  4007ac:	d503201f 	nop
  4007b0:	0f000405 	movi	v5.2s, #0x0
  4007b4:	d2800000 	mov	x0, #0x0                   	// #0
  4007b8:	3ce06a62 	ldr	q2, [x19, x0]
  4007bc:	3ce06a81 	ldr	q1, [x20, x0]
  4007c0:	91004000 	add	x0, x0, #0x10
  4007c4:	f140101f 	cmp	x0, #0x4, lsl #12
  4007c8:	6e22dc21 	fmul	v1.4s, v1.4s, v2.4s
  4007cc:	5e040424 	mov	s4, v1.s[0]
  4007d0:	5e0c0423 	mov	s3, v1.s[1]
  4007d4:	5e140422 	mov	s2, v1.s[2]
  4007d8:	5e1c0421 	mov	s1, v1.s[3]
  4007dc:	1e252884 	fadd	s4, s4, s5
  4007e0:	1e242863 	fadd	s3, s3, s4
  4007e4:	1e232842 	fadd	s2, s2, s3
  4007e8:	1e212845 	fadd	s5, s2, s1
  4007ec:	54fffe61 	b.ne	4007b8 <main+0x118>  // b.any
  4007f0:	bd404be2 	ldr	s2, [sp, #72]
  4007f4:	71000421 	subs	w1, w1, #0x1
  4007f8:	1e252842 	fadd	s2, s2, s5
  4007fc:	bd004be2 	str	s2, [sp, #72]
  400800:	54fffd81 	b.ne	4007b0 <main+0x110>  // b.any
  400804:	910183e1 	add	x1, sp, #0x60
  400808:	52800020 	mov	w0, #0x1                   	// #1
  40080c:	97ffff81 	bl	400610 <clock_gettime@plt>
  400810:	a94507e3 	ldp	x3, x1, [sp, #80]
  400814:	d2d09000 	mov	x0, #0x848000000000        	// #145685290680320
  400818:	f2e825c0 	movk	x0, #0x412e, lsl #48
  40081c:	9e670000 	fmov	d0, x0
  400820:	f94037e0 	ldr	x0, [sp, #104]
  400824:	d2c80002 	mov	x2, #0x400000000000        	// #70368744177664
  400828:	f2e811e2 	movk	x2, #0x408f, lsl #48
  40082c:	9e670041 	fmov	d1, x2
  400830:	cb010000 	sub	x0, x0, x1
  400834:	f94033e1 	ldr	x1, [sp, #96]
  400838:	9e620009 	scvtf	d9, x0
  40083c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400840:	9138e000 	add	x0, x0, #0xe38
  400844:	cb030021 	sub	x1, x1, x3
  400848:	1e601929 	fdiv	d9, d9, d0
  40084c:	9e620020 	scvtf	d0, x1
  400850:	1f412409 	fmadd	d9, d0, d1, d9
  400854:	97ffff83 	bl	400660 <puts@plt>
  400858:	1e22c100 	fcvt	d0, s8
  40085c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400860:	9139e000 	add	x0, x0, #0xe78
  400864:	97ffff87 	bl	400680 <printf@plt>
  400868:	1e22c140 	fcvt	d0, s10
  40086c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400870:	913a4000 	add	x0, x0, #0xe90
  400874:	97ffff83 	bl	400680 <printf@plt>
  400878:	d2c40000 	mov	x0, #0x200000000000        	// #35184372088832
  40087c:	f2e80c00 	movk	x0, #0x4060, lsl #48
  400880:	9e670000 	fmov	d0, x0
  400884:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400888:	913aa000 	add	x0, x0, #0xea8
  40088c:	97ffff7d 	bl	400680 <printf@plt>
  400890:	b0000001 	adrp	x1, 401000 <_IO_stdin_used+0x1e0>
  400894:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400898:	913b0000 	add	x0, x0, #0xec0
  40089c:	fd402820 	ldr	d0, [x1, #80]
  4008a0:	97ffff78 	bl	400680 <printf@plt>
  4008a4:	2d4e07e0 	ldp	s0, s1, [sp, #112]
  4008a8:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008ac:	2d4f0fe2 	ldp	s2, s3, [sp, #120]
  4008b0:	913b6000 	add	x0, x0, #0xed8
  4008b4:	1e22c021 	fcvt	d1, s1
  4008b8:	1e22c000 	fcvt	d0, s0
  4008bc:	1e22c042 	fcvt	d2, s2
  4008c0:	1e22c063 	fcvt	d3, s3
  4008c4:	97ffff6f 	bl	400680 <printf@plt>
  4008c8:	52800140 	mov	w0, #0xa                   	// #10
  4008cc:	97ffff71 	bl	400690 <putchar@plt>
  4008d0:	1e604120 	fmov	d0, d9
  4008d4:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008d8:	913c2000 	add	x0, x0, #0xf08
  4008dc:	97ffff69 	bl	400680 <printf@plt>
  4008e0:	52800140 	mov	w0, #0xa                   	// #10
  4008e4:	97ffff6b 	bl	400690 <putchar@plt>
  4008e8:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008ec:	913cc000 	add	x0, x0, #0xf30
  4008f0:	97ffff5c 	bl	400660 <puts@plt>
  4008f4:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008f8:	913d2000 	add	x0, x0, #0xf48
  4008fc:	97ffff59 	bl	400660 <puts@plt>
  400900:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400904:	913e0000 	add	x0, x0, #0xf80
  400908:	97ffff56 	bl	400660 <puts@plt>
  40090c:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400910:	913ec000 	add	x0, x0, #0xfb0
  400914:	97ffff53 	bl	400660 <puts@plt>
  400918:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  40091c:	913f6000 	add	x0, x0, #0xfd8
  400920:	97ffff50 	bl	400660 <puts@plt>
  400924:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x1e0>
  400928:	91002000 	add	x0, x0, #0x8
  40092c:	97ffff4d 	bl	400660 <puts@plt>
  400930:	52800000 	mov	w0, #0x0                   	// #0
  400934:	d2880e0c 	mov	x12, #0x4070                	// #16496
  400938:	a9407bfd 	ldp	x29, x30, [sp]
  40093c:	a94153f3 	ldp	x19, x20, [sp, #16]
  400940:	f94013f5 	ldr	x21, [sp, #32]
  400944:	fd4017ea 	ldr	d10, [sp, #40]
  400948:	6d4327e8 	ldp	d8, d9, [sp, #48]
  40094c:	bd404be0 	ldr	s0, [sp, #72]
  400950:	8b2c63ff 	add	sp, sp, x12
  400954:	d65f03c0 	ret

0000000000400958 <_start>:
  400958:	d280001d 	mov	x29, #0x0                   	// #0
  40095c:	d280001e 	mov	x30, #0x0                   	// #0
  400960:	aa0003e5 	mov	x5, x0
  400964:	f94003e1 	ldr	x1, [sp]
  400968:	910023e2 	add	x2, sp, #0x8
  40096c:	910003e6 	mov	x6, sp
  400970:	d2e00000 	movz	x0, #0x0, lsl #48
  400974:	f2c00000 	movk	x0, #0x0, lsl #32
  400978:	f2a00800 	movk	x0, #0x40, lsl #16
  40097c:	f280d400 	movk	x0, #0x6a0
  400980:	d2e00003 	movz	x3, #0x0, lsl #48
  400984:	f2c00003 	movk	x3, #0x0, lsl #32
  400988:	f2a00803 	movk	x3, #0x40, lsl #16
  40098c:	f281b003 	movk	x3, #0xd80
  400990:	d2e00004 	movz	x4, #0x0, lsl #48
  400994:	f2c00004 	movk	x4, #0x0, lsl #32
  400998:	f2a00804 	movk	x4, #0x40, lsl #16
  40099c:	f281c004 	movk	x4, #0xe00
  4009a0:	97ffff20 	bl	400620 <__libc_start_main@plt>
  4009a4:	97ffff2b 	bl	400650 <abort@plt>

00000000004009a8 <call_weak_fn>:
  4009a8:	b0000080 	adrp	x0, 411000 <__FRAME_END__+0xfda8>
  4009ac:	f947f000 	ldr	x0, [x0, #4064]
  4009b0:	b4000040 	cbz	x0, 4009b8 <call_weak_fn+0x10>
  4009b4:	17ffff23 	b	400640 <__gmon_start__@plt>
  4009b8:	d65f03c0 	ret
  4009bc:	d503201f 	nop

00000000004009c0 <deregister_tm_clones>:
  4009c0:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  4009c4:	91016000 	add	x0, x0, #0x58
  4009c8:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  4009cc:	91016021 	add	x1, x1, #0x58
  4009d0:	eb00003f 	cmp	x1, x0
  4009d4:	540000c0 	b.eq	4009ec <deregister_tm_clones+0x2c>  // b.none
  4009d8:	90000001 	adrp	x1, 400000 <_init-0x5d0>
  4009dc:	f9471421 	ldr	x1, [x1, #3624]
  4009e0:	b4000061 	cbz	x1, 4009ec <deregister_tm_clones+0x2c>
  4009e4:	aa0103f0 	mov	x16, x1
  4009e8:	d61f0200 	br	x16
  4009ec:	d65f03c0 	ret

00000000004009f0 <register_tm_clones>:
  4009f0:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  4009f4:	91016000 	add	x0, x0, #0x58
  4009f8:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  4009fc:	91016021 	add	x1, x1, #0x58
  400a00:	cb000021 	sub	x1, x1, x0
  400a04:	d37ffc22 	lsr	x2, x1, #63
  400a08:	8b810c41 	add	x1, x2, x1, asr #3
  400a0c:	eb8107ff 	cmp	xzr, x1, asr #1
  400a10:	9341fc21 	asr	x1, x1, #1
  400a14:	540000c0 	b.eq	400a2c <register_tm_clones+0x3c>  // b.none
  400a18:	90000002 	adrp	x2, 400000 <_init-0x5d0>
  400a1c:	f9471842 	ldr	x2, [x2, #3632]
  400a20:	b4000062 	cbz	x2, 400a2c <register_tm_clones+0x3c>
  400a24:	aa0203f0 	mov	x16, x2
  400a28:	d61f0200 	br	x16
  400a2c:	d65f03c0 	ret

0000000000400a30 <__do_global_dtors_aux>:
  400a30:	a9be7bfd 	stp	x29, x30, [sp, #-32]!
  400a34:	910003fd 	mov	x29, sp
  400a38:	f9000bf3 	str	x19, [sp, #16]
  400a3c:	d0000093 	adrp	x19, 412000 <clock_gettime@GLIBC_2.17>
  400a40:	39418260 	ldrb	w0, [x19, #96]
  400a44:	35000080 	cbnz	w0, 400a54 <__do_global_dtors_aux+0x24>
  400a48:	97ffffde 	bl	4009c0 <deregister_tm_clones>
  400a4c:	52800020 	mov	w0, #0x1                   	// #1
  400a50:	39018260 	strb	w0, [x19, #96]
  400a54:	f9400bf3 	ldr	x19, [sp, #16]
  400a58:	a8c27bfd 	ldp	x29, x30, [sp], #32
  400a5c:	d65f03c0 	ret

0000000000400a60 <frame_dummy>:
  400a60:	17ffffe4 	b	4009f0 <register_tm_clones>
  400a64:	d503201f 	nop
  400a68:	d503201f 	nop
  400a6c:	d503201f 	nop

0000000000400a70 <dot_product>:
  400a70:	7100005f 	cmp	w2, #0x0
  400a74:	540005cd 	b.le	400b2c <dot_product+0xbc>
  400a78:	51000443 	sub	w3, w2, #0x1
  400a7c:	7100087f 	cmp	w3, #0x2
  400a80:	540005a9 	b.ls	400b34 <dot_product+0xc4>  // b.plast
  400a84:	53027c44 	lsr	w4, w2, #2
  400a88:	0f000400 	movi	v0.2s, #0x0
  400a8c:	d2800003 	mov	x3, #0x0                   	// #0
  400a90:	d37cec84 	lsl	x4, x4, #4
  400a94:	d503201f 	nop
  400a98:	3ce36822 	ldr	q2, [x1, x3]
  400a9c:	3ce36801 	ldr	q1, [x0, x3]
  400aa0:	91004063 	add	x3, x3, #0x10
  400aa4:	eb04007f 	cmp	x3, x4
  400aa8:	6e22dc21 	fmul	v1.4s, v1.4s, v2.4s
  400aac:	5e040424 	mov	s4, v1.s[0]
  400ab0:	5e0c0423 	mov	s3, v1.s[1]
  400ab4:	5e140422 	mov	s2, v1.s[2]
  400ab8:	5e1c0421 	mov	s1, v1.s[3]
  400abc:	1e242800 	fadd	s0, s0, s4
  400ac0:	1e232800 	fadd	s0, s0, s3
  400ac4:	1e222800 	fadd	s0, s0, s2
  400ac8:	1e212800 	fadd	s0, s0, s1
  400acc:	54fffe61 	b.ne	400a98 <dot_product+0x28>  // b.any
  400ad0:	f240045f 	tst	x2, #0x3
  400ad4:	121e7443 	and	w3, w2, #0xfffffffc
  400ad8:	54000280 	b.eq	400b28 <dot_product+0xb8>  // b.none
  400adc:	93407c65 	sxtw	x5, w3
  400ae0:	11000464 	add	w4, w3, #0x1
  400ae4:	6b04005f 	cmp	w2, w4
  400ae8:	937e7c64 	sbfiz	x4, x3, #2, #32
  400aec:	bc657802 	ldr	s2, [x0, x5, lsl #2]
  400af0:	bc657821 	ldr	s1, [x1, x5, lsl #2]
  400af4:	1f010040 	fmadd	s0, s2, s1, s0
  400af8:	5400018d 	b.le	400b28 <dot_product+0xb8>
  400afc:	91001085 	add	x5, x4, #0x4
  400b00:	11000863 	add	w3, w3, #0x2
  400b04:	6b03005f 	cmp	w2, w3
  400b08:	bc656802 	ldr	s2, [x0, x5]
  400b0c:	bc656821 	ldr	s1, [x1, x5]
  400b10:	1f010040 	fmadd	s0, s2, s1, s0
  400b14:	540000ad 	b.le	400b28 <dot_product+0xb8>
  400b18:	91002084 	add	x4, x4, #0x8
  400b1c:	bc646822 	ldr	s2, [x1, x4]
  400b20:	bc646801 	ldr	s1, [x0, x4]
  400b24:	1f010040 	fmadd	s0, s2, s1, s0
  400b28:	d65f03c0 	ret
  400b2c:	0f000400 	movi	v0.2s, #0x0
  400b30:	d65f03c0 	ret
  400b34:	0f000400 	movi	v0.2s, #0x0
  400b38:	52800003 	mov	w3, #0x0                   	// #0
  400b3c:	17ffffe8 	b	400adc <dot_product+0x6c>

0000000000400b40 <conditional_sum>:
  400b40:	1e204002 	fmov	s2, s0
  400b44:	7100003f 	cmp	w1, #0x0
  400b48:	0f000400 	movi	v0.2s, #0x0
  400b4c:	5400014d 	b.le	400b74 <conditional_sum+0x34>
  400b50:	d2800002 	mov	x2, #0x0                   	// #0
  400b54:	d503201f 	nop
  400b58:	bc627801 	ldr	s1, [x0, x2, lsl #2]
  400b5c:	91000442 	add	x2, x2, #0x1
  400b60:	1e222030 	fcmpe	s1, s2
  400b64:	5400004d 	b.le	400b6c <conditional_sum+0x2c>
  400b68:	1e212800 	fadd	s0, s0, s1
  400b6c:	6b02003f 	cmp	w1, w2
  400b70:	54ffff4c 	b.gt	400b58 <conditional_sum+0x18>
  400b74:	d65f03c0 	ret
  400b78:	d503201f 	nop
  400b7c:	d503201f 	nop

0000000000400b80 <poly_eval>:
  400b80:	1e204002 	fmov	s2, s0
  400b84:	71000421 	subs	w1, w1, #0x1
  400b88:	0f000400 	movi	v0.2s, #0x0
  400b8c:	540000e4 	b.mi	400ba8 <poly_eval+0x28>  // b.first
  400b90:	93407c21 	sxtw	x1, w1
  400b94:	d503201f 	nop
  400b98:	bc617801 	ldr	s1, [x0, x1, lsl #2]
  400b9c:	d1000421 	sub	x1, x1, #0x1
  400ba0:	1f000440 	fmadd	s0, s2, s0, s1
  400ba4:	36ffffa1 	tbz	w1, #31, 400b98 <poly_eval+0x18>
  400ba8:	d65f03c0 	ret
  400bac:	d503201f 	nop

0000000000400bb0 <dead_code_test>:
  400bb0:	529eb860 	mov	w0, #0xf5c3                	// #62915
  400bb4:	d10043ff 	sub	sp, sp, #0x10
  400bb8:	72a80900 	movk	w0, #0x4048, lsl #16
  400bbc:	1e270001 	fmov	s1, w0
  400bc0:	1e210800 	fmul	s0, s0, s1
  400bc4:	bd000fe0 	str	s0, [sp, #12]
  400bc8:	910043ff 	add	sp, sp, #0x10
  400bcc:	d65f03c0 	ret

0000000000400bd0 <manual_unroll>:
  400bd0:	71000c5f 	cmp	w2, #0x3
  400bd4:	540008cd 	b.le	400cec <manual_unroll+0x11c>
  400bd8:	91003c23 	add	x3, x1, #0xf
  400bdc:	51001045 	sub	w5, w2, #0x4
  400be0:	cb000063 	sub	x3, x3, x0
  400be4:	f100787f 	cmp	x3, #0x1e
  400be8:	7a4388a0 	ccmp	w5, #0x3, #0x0, hi  // hi = pmore
  400bec:	53027ca5 	lsr	w5, w5, #2
  400bf0:	54000549 	b.ls	400c98 <manual_unroll+0xc8>  // b.plast
  400bf4:	110004a6 	add	w6, w5, #0x1
  400bf8:	d2800003 	mov	x3, #0x0                   	// #0
  400bfc:	52800004 	mov	w4, #0x0                   	// #0
  400c00:	3ce36820 	ldr	q0, [x1, x3]
  400c04:	11000484 	add	w4, w4, #0x1
  400c08:	6b0400df 	cmp	w6, w4
  400c0c:	4e20d400 	fadd	v0.4s, v0.4s, v0.4s
  400c10:	3ca36800 	str	q0, [x0, x3]
  400c14:	91004063 	add	x3, x3, #0x10
  400c18:	54ffff48 	b.hi	400c00 <manual_unroll+0x30>  // b.pmore
  400c1c:	110004a3 	add	w3, w5, #0x1
  400c20:	531e7463 	lsl	w3, w3, #2
  400c24:	6b03005f 	cmp	w2, w3
  400c28:	5400036d 	b.le	400c94 <manual_unroll+0xc4>
  400c2c:	93407c65 	sxtw	x5, w3
  400c30:	11000464 	add	w4, w3, #0x1
  400c34:	6b02009f 	cmp	w4, w2
  400c38:	937e7c64 	sbfiz	x4, x3, #2, #32
  400c3c:	bc657820 	ldr	s0, [x1, x5, lsl #2]
  400c40:	1e202800 	fadd	s0, s0, s0
  400c44:	bc257800 	str	s0, [x0, x5, lsl #2]
  400c48:	5400026a 	b.ge	400c94 <manual_unroll+0xc4>  // b.tcont
  400c4c:	91001085 	add	x5, x4, #0x4
  400c50:	11000866 	add	w6, w3, #0x2
  400c54:	6b0200df 	cmp	w6, w2
  400c58:	bc656820 	ldr	s0, [x1, x5]
  400c5c:	1e202800 	fadd	s0, s0, s0
  400c60:	bc256800 	str	s0, [x0, x5]
  400c64:	5400018a 	b.ge	400c94 <manual_unroll+0xc4>  // b.tcont
  400c68:	91002085 	add	x5, x4, #0x8
  400c6c:	11000c63 	add	w3, w3, #0x3
  400c70:	6b02007f 	cmp	w3, w2
  400c74:	bc656820 	ldr	s0, [x1, x5]
  400c78:	1e202800 	fadd	s0, s0, s0
  400c7c:	bc256800 	str	s0, [x0, x5]
  400c80:	540000aa 	b.ge	400c94 <manual_unroll+0xc4>  // b.tcont
  400c84:	91003084 	add	x4, x4, #0xc
  400c88:	bc646820 	ldr	s0, [x1, x4]
  400c8c:	1e202800 	fadd	s0, s0, s0
  400c90:	bc246800 	str	s0, [x0, x4]
  400c94:	d65f03c0 	ret
  400c98:	91004026 	add	x6, x1, #0x10
  400c9c:	aa0103e3 	mov	x3, x1
  400ca0:	aa0003e4 	mov	x4, x0
  400ca4:	8b2550c6 	add	x6, x6, w5, uxtw #4
  400ca8:	bd400060 	ldr	s0, [x3]
  400cac:	91004063 	add	x3, x3, #0x10
  400cb0:	91004084 	add	x4, x4, #0x10
  400cb4:	1e202800 	fadd	s0, s0, s0
  400cb8:	bc1f0080 	stur	s0, [x4, #-16]
  400cbc:	bc5f4060 	ldur	s0, [x3, #-12]
  400cc0:	1e202800 	fadd	s0, s0, s0
  400cc4:	bc1f4080 	stur	s0, [x4, #-12]
  400cc8:	bc5f8060 	ldur	s0, [x3, #-8]
  400ccc:	1e202800 	fadd	s0, s0, s0
  400cd0:	bc1f8080 	stur	s0, [x4, #-8]
  400cd4:	bc5fc060 	ldur	s0, [x3, #-4]
  400cd8:	eb06007f 	cmp	x3, x6
  400cdc:	1e202800 	fadd	s0, s0, s0
  400ce0:	bc1fc080 	stur	s0, [x4, #-4]
  400ce4:	54fffe21 	b.ne	400ca8 <manual_unroll+0xd8>  // b.any
  400ce8:	17ffffcd 	b	400c1c <manual_unroll+0x4c>
  400cec:	52800003 	mov	w3, #0x0                   	// #0
  400cf0:	17ffffcd 	b	400c24 <manual_unroll+0x54>

0000000000400cf4 <bad_loop>:
  400cf4:	2a0003e2 	mov	w2, w0
  400cf8:	7100001f 	cmp	w0, #0x0
  400cfc:	5400038d 	b.le	400d6c <bad_loop+0x78>
  400d00:	51000400 	sub	w0, w0, #0x1
  400d04:	7100641f 	cmp	w0, #0x19
  400d08:	54000369 	b.ls	400d74 <bad_loop+0x80>  // b.plast
  400d0c:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x1e0>
  400d10:	52800001 	mov	w1, #0x0                   	// #0
  400d14:	4f000400 	movi	v0.4s, #0x0
  400d18:	4f000483 	movi	v3.4s, #0x4
  400d1c:	3dc01001 	ldr	q1, [x0, #64]
  400d20:	53027c40 	lsr	w0, w2, #2
  400d24:	d503201f 	nop
  400d28:	4ea11c22 	mov	v2.16b, v1.16b
  400d2c:	11000421 	add	w1, w1, #0x1
  400d30:	4ea38421 	add	v1.4s, v1.4s, v3.4s
  400d34:	6b00003f 	cmp	w1, w0
  400d38:	4ea28400 	add	v0.4s, v0.4s, v2.4s
  400d3c:	54ffff61 	b.ne	400d28 <bad_loop+0x34>  // b.any
  400d40:	4eb1b800 	addv	s0, v0.4s
  400d44:	f240045f 	tst	x2, #0x3
  400d48:	121e7441 	and	w1, w2, #0xfffffffc
  400d4c:	0e043c00 	mov	w0, v0.s[0]
  400d50:	540000c0 	b.eq	400d68 <bad_loop+0x74>  // b.none
  400d54:	d503201f 	nop
  400d58:	0b010000 	add	w0, w0, w1
  400d5c:	11000421 	add	w1, w1, #0x1
  400d60:	6b01005f 	cmp	w2, w1
  400d64:	54ffffac 	b.gt	400d58 <bad_loop+0x64>
  400d68:	d65f03c0 	ret
  400d6c:	52800000 	mov	w0, #0x0                   	// #0
  400d70:	d65f03c0 	ret
  400d74:	52800001 	mov	w1, #0x0                   	// #0
  400d78:	52800000 	mov	w0, #0x0                   	// #0
  400d7c:	17fffff7 	b	400d58 <bad_loop+0x64>

0000000000400d80 <__libc_csu_init>:
  400d80:	a9bc7bfd 	stp	x29, x30, [sp, #-64]!
  400d84:	910003fd 	mov	x29, sp
  400d88:	a90153f3 	stp	x19, x20, [sp, #16]
  400d8c:	b0000094 	adrp	x20, 411000 <__FRAME_END__+0xfda8>
  400d90:	91378294 	add	x20, x20, #0xde0
  400d94:	a9025bf5 	stp	x21, x22, [sp, #32]
  400d98:	b0000095 	adrp	x21, 411000 <__FRAME_END__+0xfda8>
  400d9c:	913762b5 	add	x21, x21, #0xdd8
  400da0:	cb150294 	sub	x20, x20, x21
  400da4:	2a0003f6 	mov	w22, w0
  400da8:	a90363f7 	stp	x23, x24, [sp, #48]
  400dac:	aa0103f7 	mov	x23, x1
  400db0:	aa0203f8 	mov	x24, x2
  400db4:	97fffe07 	bl	4005d0 <_init>
  400db8:	eb940fff 	cmp	xzr, x20, asr #3
  400dbc:	54000160 	b.eq	400de8 <__libc_csu_init+0x68>  // b.none
  400dc0:	9343fe94 	asr	x20, x20, #3
  400dc4:	d2800013 	mov	x19, #0x0                   	// #0
  400dc8:	f8737aa3 	ldr	x3, [x21, x19, lsl #3]
  400dcc:	aa1803e2 	mov	x2, x24
  400dd0:	91000673 	add	x19, x19, #0x1
  400dd4:	aa1703e1 	mov	x1, x23
  400dd8:	2a1603e0 	mov	w0, w22
  400ddc:	d63f0060 	blr	x3
  400de0:	eb13029f 	cmp	x20, x19
  400de4:	54ffff21 	b.ne	400dc8 <__libc_csu_init+0x48>  // b.any
  400de8:	a94153f3 	ldp	x19, x20, [sp, #16]
  400dec:	a9425bf5 	ldp	x21, x22, [sp, #32]
  400df0:	a94363f7 	ldp	x23, x24, [sp, #48]
  400df4:	a8c47bfd 	ldp	x29, x30, [sp], #64
  400df8:	d65f03c0 	ret
  400dfc:	d503201f 	nop

0000000000400e00 <__libc_csu_fini>:
  400e00:	d65f03c0 	ret

Disassembly of section .fini:

0000000000400e04 <_fini>:
  400e04:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  400e08:	910003fd 	mov	x29, sp
  400e0c:	a8c17bfd 	ldp	x29, x30, [sp], #16
  400e10:	d65f03c0 	ret
