
build/opt_Ofast：     文件格式 elf64-littleaarch64


Disassembly of section .init:

00000000004005d0 <_init>:
  4005d0:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  4005d4:	910003fd 	mov	x29, sp
  4005d8:	940000ed 	bl	40098c <call_weak_fn>
  4005dc:	a8c17bfd 	ldp	x29, x30, [sp], #16
  4005e0:	d65f03c0 	ret

Disassembly of section .plt:

00000000004005f0 <.plt>:
  4005f0:	a9bf7bf0 	stp	x16, x30, [sp, #-16]!
  4005f4:	b0000090 	adrp	x16, 411000 <__FRAME_END__+0xfce4>
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
  40070c:	4f000409 	movi	v9.4s, #0x0
  400710:	d2800000 	mov	x0, #0x0                   	// #0
  400714:	3ce06a61 	ldr	q1, [x19, x0]
  400718:	3ce06a80 	ldr	q0, [x20, x0]
  40071c:	91004000 	add	x0, x0, #0x10
  400720:	f140101f 	cmp	x0, #0x4, lsl #12
  400724:	4e20cc29 	fmla	v9.4s, v1.4s, v0.4s
  400728:	54ffff61 	b.ne	400714 <main+0x74>  // b.any
  40072c:	6e29d529 	faddp	v9.4s, v9.4s, v9.4s
  400730:	aa1303e0 	mov	x0, x19
  400734:	4f000408 	movi	v8.4s, #0x0
  400738:	91401261 	add	x1, x19, #0x4, lsl #12
  40073c:	4f03f402 	fmov	v2.4s, #5.000000000000000000e-01
  400740:	6e29d529 	faddp	v9.4s, v9.4s, v9.4s
  400744:	3cc10401 	ldr	q1, [x0], #16
  400748:	6ea2e420 	fcmgt	v0.4s, v1.4s, v2.4s
  40074c:	eb00003f 	cmp	x1, x0
  400750:	4e211c00 	and	v0.16b, v0.16b, v1.16b
  400754:	4e20d508 	fadd	v8.4s, v8.4s, v0.4s
  400758:	54ffff61 	b.ne	400744 <main+0xa4>  // b.any
  40075c:	6e28d508 	faddp	v8.4s, v8.4s, v8.4s
  400760:	52970a40 	mov	w0, #0xb852                	// #47186
  400764:	72a812c0 	movk	w0, #0x4096, lsl #16
  400768:	1e270000 	fmov	s0, w0
  40076c:	52820002 	mov	w2, #0x1000                	// #4096
  400770:	aa1303e1 	mov	x1, x19
  400774:	9101c3e0 	add	x0, sp, #0x70
  400778:	bd004fe0 	str	s0, [sp, #76]
  40077c:	6e28d508 	faddp	v8.4s, v8.4s, v8.4s
  400780:	9400013c 	bl	400c70 <manual_unroll>
  400784:	910143e1 	add	x1, sp, #0x50
  400788:	52800020 	mov	w0, #0x1                   	// #1
  40078c:	97ffffa1 	bl	400610 <clock_gettime@plt>
  400790:	b9004bff 	str	wzr, [sp, #72]
  400794:	52807d01 	mov	w1, #0x3e8                 	// #1000
  400798:	4f000400 	movi	v0.4s, #0x0
  40079c:	d2800000 	mov	x0, #0x0                   	// #0
  4007a0:	3ce06a82 	ldr	q2, [x20, x0]
  4007a4:	3ce06a61 	ldr	q1, [x19, x0]
  4007a8:	91004000 	add	x0, x0, #0x10
  4007ac:	f140101f 	cmp	x0, #0x4, lsl #12
  4007b0:	4e21cc40 	fmla	v0.4s, v2.4s, v1.4s
  4007b4:	54ffff61 	b.ne	4007a0 <main+0x100>  // b.any
  4007b8:	6e20d400 	faddp	v0.4s, v0.4s, v0.4s
  4007bc:	bd404be1 	ldr	s1, [sp, #72]
  4007c0:	71000421 	subs	w1, w1, #0x1
  4007c4:	6e20d400 	faddp	v0.4s, v0.4s, v0.4s
  4007c8:	1e202820 	fadd	s0, s1, s0
  4007cc:	bd004be0 	str	s0, [sp, #72]
  4007d0:	54fffe41 	b.ne	400798 <main+0xf8>  // b.any
  4007d4:	910183e1 	add	x1, sp, #0x60
  4007d8:	52800020 	mov	w0, #0x1                   	// #1
  4007dc:	97ffff8d 	bl	400610 <clock_gettime@plt>
  4007e0:	a9450be3 	ldp	x3, x2, [sp, #80]
  4007e4:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x140>
  4007e8:	f94037e1 	ldr	x1, [sp, #104]
  4007ec:	fd407802 	ldr	d2, [x0, #240]
  4007f0:	d2c80000 	mov	x0, #0x400000000000        	// #70368744177664
  4007f4:	f2e811e0 	movk	x0, #0x408f, lsl #48
  4007f8:	9e670001 	fmov	d1, x0
  4007fc:	cb020021 	sub	x1, x1, x2
  400800:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400804:	f94033e2 	ldr	x2, [sp, #96]
  400808:	9e62002a 	scvtf	d10, x1
  40080c:	913b6000 	add	x0, x0, #0xed8
  400810:	cb030042 	sub	x2, x2, x3
  400814:	9e620040 	scvtf	d0, x2
  400818:	1e62094a 	fmul	d10, d10, d2
  40081c:	1f41280a 	fmadd	d10, d0, d1, d10
  400820:	97ffff90 	bl	400660 <puts@plt>
  400824:	1e22c120 	fcvt	d0, s9
  400828:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  40082c:	913c6000 	add	x0, x0, #0xf18
  400830:	97ffff94 	bl	400680 <printf@plt>
  400834:	1e22c100 	fcvt	d0, s8
  400838:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  40083c:	913cc000 	add	x0, x0, #0xf30
  400840:	97ffff90 	bl	400680 <printf@plt>
  400844:	d2c40000 	mov	x0, #0x200000000000        	// #35184372088832
  400848:	f2e80c00 	movk	x0, #0x4060, lsl #48
  40084c:	9e670000 	fmov	d0, x0
  400850:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400854:	913d2000 	add	x0, x0, #0xf48
  400858:	97ffff8a 	bl	400680 <printf@plt>
  40085c:	b0000001 	adrp	x1, 401000 <_IO_stdin_used+0x140>
  400860:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400864:	913d8000 	add	x0, x0, #0xf60
  400868:	fd407c20 	ldr	d0, [x1, #248]
  40086c:	97ffff85 	bl	400680 <printf@plt>
  400870:	2d4e07e0 	ldp	s0, s1, [sp, #112]
  400874:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400878:	2d4f0fe2 	ldp	s2, s3, [sp, #120]
  40087c:	913de000 	add	x0, x0, #0xf78
  400880:	1e22c021 	fcvt	d1, s1
  400884:	1e22c000 	fcvt	d0, s0
  400888:	1e22c042 	fcvt	d2, s2
  40088c:	1e22c063 	fcvt	d3, s3
  400890:	97ffff7c 	bl	400680 <printf@plt>
  400894:	52800140 	mov	w0, #0xa                   	// #10
  400898:	97ffff7e 	bl	400690 <putchar@plt>
  40089c:	1e604140 	fmov	d0, d10
  4008a0:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008a4:	913ea000 	add	x0, x0, #0xfa8
  4008a8:	97ffff76 	bl	400680 <printf@plt>
  4008ac:	52800140 	mov	w0, #0xa                   	// #10
  4008b0:	97ffff78 	bl	400690 <putchar@plt>
  4008b4:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008b8:	913f4000 	add	x0, x0, #0xfd0
  4008bc:	97ffff69 	bl	400660 <puts@plt>
  4008c0:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  4008c4:	913fa000 	add	x0, x0, #0xfe8
  4008c8:	97ffff66 	bl	400660 <puts@plt>
  4008cc:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x140>
  4008d0:	91008000 	add	x0, x0, #0x20
  4008d4:	97ffff63 	bl	400660 <puts@plt>
  4008d8:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x140>
  4008dc:	91014000 	add	x0, x0, #0x50
  4008e0:	97ffff60 	bl	400660 <puts@plt>
  4008e4:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x140>
  4008e8:	9101e000 	add	x0, x0, #0x78
  4008ec:	97ffff5d 	bl	400660 <puts@plt>
  4008f0:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x140>
  4008f4:	9102a000 	add	x0, x0, #0xa8
  4008f8:	97ffff5a 	bl	400660 <puts@plt>
  4008fc:	52800000 	mov	w0, #0x0                   	// #0
  400900:	d2880e0c 	mov	x12, #0x4070                	// #16496
  400904:	a9407bfd 	ldp	x29, x30, [sp]
  400908:	a94153f3 	ldp	x19, x20, [sp, #16]
  40090c:	f94013f5 	ldr	x21, [sp, #32]
  400910:	fd4017ea 	ldr	d10, [sp, #40]
  400914:	6d4327e8 	ldp	d8, d9, [sp, #48]
  400918:	bd404be0 	ldr	s0, [sp, #72]
  40091c:	8b2c63ff 	add	sp, sp, x12
  400920:	d65f03c0 	ret
  400924:	d503201f 	nop
  400928:	d503201f 	nop
  40092c:	d503201f 	nop

0000000000400930 <set_fast_math>:
  400930:	52a02000 	mov	w0, #0x1000000             	// #16777216
  400934:	d51b4400 	msr	fpcr, x0
  400938:	d65f03c0 	ret

000000000040093c <_start>:
  40093c:	d280001d 	mov	x29, #0x0                   	// #0
  400940:	d280001e 	mov	x30, #0x0                   	// #0
  400944:	aa0003e5 	mov	x5, x0
  400948:	f94003e1 	ldr	x1, [sp]
  40094c:	910023e2 	add	x2, sp, #0x8
  400950:	910003e6 	mov	x6, sp
  400954:	d2e00000 	movz	x0, #0x0, lsl #48
  400958:	f2c00000 	movk	x0, #0x0, lsl #32
  40095c:	f2a00800 	movk	x0, #0x40, lsl #16
  400960:	f280d400 	movk	x0, #0x6a0
  400964:	d2e00003 	movz	x3, #0x0, lsl #48
  400968:	f2c00003 	movk	x3, #0x0, lsl #32
  40096c:	f2a00803 	movk	x3, #0x40, lsl #16
  400970:	f281c403 	movk	x3, #0xe20
  400974:	d2e00004 	movz	x4, #0x0, lsl #48
  400978:	f2c00004 	movk	x4, #0x0, lsl #32
  40097c:	f2a00804 	movk	x4, #0x40, lsl #16
  400980:	f281d404 	movk	x4, #0xea0
  400984:	97ffff27 	bl	400620 <__libc_start_main@plt>
  400988:	97ffff32 	bl	400650 <abort@plt>

000000000040098c <call_weak_fn>:
  40098c:	b0000080 	adrp	x0, 411000 <__FRAME_END__+0xfce4>
  400990:	f947f000 	ldr	x0, [x0, #4064]
  400994:	b4000040 	cbz	x0, 40099c <call_weak_fn+0x10>
  400998:	17ffff2a 	b	400640 <__gmon_start__@plt>
  40099c:	d65f03c0 	ret

00000000004009a0 <deregister_tm_clones>:
  4009a0:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  4009a4:	91016000 	add	x0, x0, #0x58
  4009a8:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  4009ac:	91016021 	add	x1, x1, #0x58
  4009b0:	eb00003f 	cmp	x1, x0
  4009b4:	540000c0 	b.eq	4009cc <deregister_tm_clones+0x2c>  // b.none
  4009b8:	90000001 	adrp	x1, 400000 <_init-0x5d0>
  4009bc:	f9476421 	ldr	x1, [x1, #3784]
  4009c0:	b4000061 	cbz	x1, 4009cc <deregister_tm_clones+0x2c>
  4009c4:	aa0103f0 	mov	x16, x1
  4009c8:	d61f0200 	br	x16
  4009cc:	d65f03c0 	ret

00000000004009d0 <register_tm_clones>:
  4009d0:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  4009d4:	91016000 	add	x0, x0, #0x58
  4009d8:	d0000081 	adrp	x1, 412000 <clock_gettime@GLIBC_2.17>
  4009dc:	91016021 	add	x1, x1, #0x58
  4009e0:	cb000021 	sub	x1, x1, x0
  4009e4:	d37ffc22 	lsr	x2, x1, #63
  4009e8:	8b810c41 	add	x1, x2, x1, asr #3
  4009ec:	eb8107ff 	cmp	xzr, x1, asr #1
  4009f0:	9341fc21 	asr	x1, x1, #1
  4009f4:	540000c0 	b.eq	400a0c <register_tm_clones+0x3c>  // b.none
  4009f8:	90000002 	adrp	x2, 400000 <_init-0x5d0>
  4009fc:	f9476842 	ldr	x2, [x2, #3792]
  400a00:	b4000062 	cbz	x2, 400a0c <register_tm_clones+0x3c>
  400a04:	aa0203f0 	mov	x16, x2
  400a08:	d61f0200 	br	x16
  400a0c:	d65f03c0 	ret

0000000000400a10 <__do_global_dtors_aux>:
  400a10:	a9be7bfd 	stp	x29, x30, [sp, #-32]!
  400a14:	910003fd 	mov	x29, sp
  400a18:	f9000bf3 	str	x19, [sp, #16]
  400a1c:	d0000093 	adrp	x19, 412000 <clock_gettime@GLIBC_2.17>
  400a20:	39418260 	ldrb	w0, [x19, #96]
  400a24:	35000080 	cbnz	w0, 400a34 <__do_global_dtors_aux+0x24>
  400a28:	97ffffde 	bl	4009a0 <deregister_tm_clones>
  400a2c:	52800020 	mov	w0, #0x1                   	// #1
  400a30:	39018260 	strb	w0, [x19, #96]
  400a34:	f9400bf3 	ldr	x19, [sp, #16]
  400a38:	a8c27bfd 	ldp	x29, x30, [sp], #32
  400a3c:	d65f03c0 	ret

0000000000400a40 <frame_dummy>:
  400a40:	17ffffe4 	b	4009d0 <register_tm_clones>
  400a44:	d503201f 	nop
  400a48:	d503201f 	nop
  400a4c:	d503201f 	nop

0000000000400a50 <dot_product>:
  400a50:	7100005f 	cmp	w2, #0x0
  400a54:	5400050d 	b.le	400af4 <dot_product+0xa4>
  400a58:	51000443 	sub	w3, w2, #0x1
  400a5c:	7100087f 	cmp	w3, #0x2
  400a60:	540004e9 	b.ls	400afc <dot_product+0xac>  // b.plast
  400a64:	53027c44 	lsr	w4, w2, #2
  400a68:	d2800003 	mov	x3, #0x0                   	// #0
  400a6c:	4f000400 	movi	v0.4s, #0x0
  400a70:	d37cec84 	lsl	x4, x4, #4
  400a74:	d503201f 	nop
  400a78:	3ce36802 	ldr	q2, [x0, x3]
  400a7c:	3ce36821 	ldr	q1, [x1, x3]
  400a80:	91004063 	add	x3, x3, #0x10
  400a84:	eb04007f 	cmp	x3, x4
  400a88:	4e21cc40 	fmla	v0.4s, v2.4s, v1.4s
  400a8c:	54ffff61 	b.ne	400a78 <dot_product+0x28>  // b.any
  400a90:	6e20d400 	faddp	v0.4s, v0.4s, v0.4s
  400a94:	f240045f 	tst	x2, #0x3
  400a98:	121e7443 	and	w3, w2, #0xfffffffc
  400a9c:	6e20d400 	faddp	v0.4s, v0.4s, v0.4s
  400aa0:	54000280 	b.eq	400af0 <dot_product+0xa0>  // b.none
  400aa4:	93407c65 	sxtw	x5, w3
  400aa8:	11000464 	add	w4, w3, #0x1
  400aac:	6b04005f 	cmp	w2, w4
  400ab0:	937e7c64 	sbfiz	x4, x3, #2, #32
  400ab4:	bc657802 	ldr	s2, [x0, x5, lsl #2]
  400ab8:	bc657821 	ldr	s1, [x1, x5, lsl #2]
  400abc:	1f010040 	fmadd	s0, s2, s1, s0
  400ac0:	5400018d 	b.le	400af0 <dot_product+0xa0>
  400ac4:	91001085 	add	x5, x4, #0x4
  400ac8:	11000863 	add	w3, w3, #0x2
  400acc:	6b03005f 	cmp	w2, w3
  400ad0:	bc656802 	ldr	s2, [x0, x5]
  400ad4:	bc656821 	ldr	s1, [x1, x5]
  400ad8:	1f010040 	fmadd	s0, s2, s1, s0
  400adc:	540000ad 	b.le	400af0 <dot_product+0xa0>
  400ae0:	91002084 	add	x4, x4, #0x8
  400ae4:	bc646822 	ldr	s2, [x1, x4]
  400ae8:	bc646801 	ldr	s1, [x0, x4]
  400aec:	1f010040 	fmadd	s0, s2, s1, s0
  400af0:	d65f03c0 	ret
  400af4:	0f000400 	movi	v0.2s, #0x0
  400af8:	d65f03c0 	ret
  400afc:	0f000400 	movi	v0.2s, #0x0
  400b00:	52800003 	mov	w3, #0x0                   	// #0
  400b04:	17ffffe8 	b	400aa4 <dot_product+0x54>
  400b08:	d503201f 	nop
  400b0c:	d503201f 	nop

0000000000400b10 <conditional_sum>:
  400b10:	1e204004 	fmov	s4, s0
  400b14:	7100003f 	cmp	w1, #0x0
  400b18:	5400076d 	b.le	400c04 <conditional_sum+0xf4>
  400b1c:	51000422 	sub	w2, w1, #0x1
  400b20:	7100105f 	cmp	w2, #0x4
  400b24:	54000749 	b.ls	400c0c <conditional_sum+0xfc>  // b.plast
  400b28:	53027c24 	lsr	w4, w1, #2
  400b2c:	91004003 	add	x3, x0, #0x10
  400b30:	51000484 	sub	w4, w4, #0x1
  400b34:	aa0003e2 	mov	x2, x0
  400b38:	4e040400 	dup	v0.4s, v0.s[0]
  400b3c:	4f000401 	movi	v1.4s, #0x0
  400b40:	8b245063 	add	x3, x3, w4, uxtw #4
  400b44:	d503201f 	nop
  400b48:	3cc10443 	ldr	q3, [x2], #16
  400b4c:	6ea0e462 	fcmgt	v2.4s, v3.4s, v0.4s
  400b50:	eb03005f 	cmp	x2, x3
  400b54:	4e231c42 	and	v2.16b, v2.16b, v3.16b
  400b58:	4e22d421 	fadd	v1.4s, v1.4s, v2.4s
  400b5c:	54ffff61 	b.ne	400b48 <conditional_sum+0x38>  // b.any
  400b60:	6e21d421 	faddp	v1.4s, v1.4s, v1.4s
  400b64:	f240043f 	tst	x1, #0x3
  400b68:	121e7422 	and	w2, w1, #0xfffffffc
  400b6c:	6e21d421 	faddp	v1.4s, v1.4s, v1.4s
  400b70:	5e040420 	mov	s0, v1.s[0]
  400b74:	54000460 	b.eq	400c00 <conditional_sum+0xf0>  // b.none
  400b78:	bc62d801 	ldr	s1, [x0, w2, sxtw #2]
  400b7c:	11000443 	add	w3, w2, #0x1
  400b80:	937e7c44 	sbfiz	x4, x2, #2, #32
  400b84:	1e242030 	fcmpe	s1, s4
  400b88:	1e212801 	fadd	s1, s0, s1
  400b8c:	1e20cc20 	fcsel	s0, s1, s0, gt
  400b90:	6b01007f 	cmp	w3, w1
  400b94:	5400036a 	b.ge	400c00 <conditional_sum+0xf0>  // b.tcont
  400b98:	8b040000 	add	x0, x0, x4
  400b9c:	11000843 	add	w3, w2, #0x2
  400ba0:	bd400401 	ldr	s1, [x0, #4]
  400ba4:	1e212090 	fcmpe	s4, s1
  400ba8:	1e212801 	fadd	s1, s0, s1
  400bac:	1e204c20 	fcsel	s0, s1, s0, mi  // mi = first
  400bb0:	6b01007f 	cmp	w3, w1
  400bb4:	5400026a 	b.ge	400c00 <conditional_sum+0xf0>  // b.tcont
  400bb8:	bd400801 	ldr	s1, [x0, #8]
  400bbc:	11000c43 	add	w3, w2, #0x3
  400bc0:	1e212090 	fcmpe	s4, s1
  400bc4:	1e212801 	fadd	s1, s0, s1
  400bc8:	1e204c20 	fcsel	s0, s1, s0, mi  // mi = first
  400bcc:	6b03003f 	cmp	w1, w3
  400bd0:	5400018d 	b.le	400c00 <conditional_sum+0xf0>
  400bd4:	bd400c01 	ldr	s1, [x0, #12]
  400bd8:	11001042 	add	w2, w2, #0x4
  400bdc:	1e212090 	fcmpe	s4, s1
  400be0:	1e212801 	fadd	s1, s0, s1
  400be4:	1e204c20 	fcsel	s0, s1, s0, mi  // mi = first
  400be8:	6b02003f 	cmp	w1, w2
  400bec:	540000ad 	b.le	400c00 <conditional_sum+0xf0>
  400bf0:	bd401001 	ldr	s1, [x0, #16]
  400bf4:	1e212090 	fcmpe	s4, s1
  400bf8:	1e212801 	fadd	s1, s0, s1
  400bfc:	1e204c20 	fcsel	s0, s1, s0, mi  // mi = first
  400c00:	d65f03c0 	ret
  400c04:	0f000400 	movi	v0.2s, #0x0
  400c08:	d65f03c0 	ret
  400c0c:	0f000400 	movi	v0.2s, #0x0
  400c10:	52800002 	mov	w2, #0x0                   	// #0
  400c14:	17ffffd9 	b	400b78 <conditional_sum+0x68>
  400c18:	d503201f 	nop
  400c1c:	d503201f 	nop

0000000000400c20 <poly_eval>:
  400c20:	1e204002 	fmov	s2, s0
  400c24:	71000421 	subs	w1, w1, #0x1
  400c28:	0f000400 	movi	v0.2s, #0x0
  400c2c:	540000e4 	b.mi	400c48 <poly_eval+0x28>  // b.first
  400c30:	93407c21 	sxtw	x1, w1
  400c34:	d503201f 	nop
  400c38:	bc617801 	ldr	s1, [x0, x1, lsl #2]
  400c3c:	d1000421 	sub	x1, x1, #0x1
  400c40:	1f000440 	fmadd	s0, s2, s0, s1
  400c44:	36ffffa1 	tbz	w1, #31, 400c38 <poly_eval+0x18>
  400c48:	d65f03c0 	ret
  400c4c:	d503201f 	nop

0000000000400c50 <dead_code_test>:
  400c50:	529eb860 	mov	w0, #0xf5c3                	// #62915
  400c54:	d10043ff 	sub	sp, sp, #0x10
  400c58:	72a80900 	movk	w0, #0x4048, lsl #16
  400c5c:	1e270001 	fmov	s1, w0
  400c60:	1e210800 	fmul	s0, s0, s1
  400c64:	bd000fe0 	str	s0, [sp, #12]
  400c68:	910043ff 	add	sp, sp, #0x10
  400c6c:	d65f03c0 	ret

0000000000400c70 <manual_unroll>:
  400c70:	71000c5f 	cmp	w2, #0x3
  400c74:	540008cd 	b.le	400d8c <manual_unroll+0x11c>
  400c78:	91003c23 	add	x3, x1, #0xf
  400c7c:	51001045 	sub	w5, w2, #0x4
  400c80:	cb000063 	sub	x3, x3, x0
  400c84:	f100787f 	cmp	x3, #0x1e
  400c88:	7a4388a0 	ccmp	w5, #0x3, #0x0, hi  // hi = pmore
  400c8c:	53027ca5 	lsr	w5, w5, #2
  400c90:	54000549 	b.ls	400d38 <manual_unroll+0xc8>  // b.plast
  400c94:	110004a6 	add	w6, w5, #0x1
  400c98:	d2800003 	mov	x3, #0x0                   	// #0
  400c9c:	52800004 	mov	w4, #0x0                   	// #0
  400ca0:	3ce36820 	ldr	q0, [x1, x3]
  400ca4:	11000484 	add	w4, w4, #0x1
  400ca8:	6b0400df 	cmp	w6, w4
  400cac:	4e20d400 	fadd	v0.4s, v0.4s, v0.4s
  400cb0:	3ca36800 	str	q0, [x0, x3]
  400cb4:	91004063 	add	x3, x3, #0x10
  400cb8:	54ffff48 	b.hi	400ca0 <manual_unroll+0x30>  // b.pmore
  400cbc:	110004a3 	add	w3, w5, #0x1
  400cc0:	531e7463 	lsl	w3, w3, #2
  400cc4:	6b03005f 	cmp	w2, w3
  400cc8:	5400036d 	b.le	400d34 <manual_unroll+0xc4>
  400ccc:	93407c65 	sxtw	x5, w3
  400cd0:	11000464 	add	w4, w3, #0x1
  400cd4:	6b02009f 	cmp	w4, w2
  400cd8:	937e7c64 	sbfiz	x4, x3, #2, #32
  400cdc:	bc657820 	ldr	s0, [x1, x5, lsl #2]
  400ce0:	1e202800 	fadd	s0, s0, s0
  400ce4:	bc257800 	str	s0, [x0, x5, lsl #2]
  400ce8:	5400026a 	b.ge	400d34 <manual_unroll+0xc4>  // b.tcont
  400cec:	91001085 	add	x5, x4, #0x4
  400cf0:	11000866 	add	w6, w3, #0x2
  400cf4:	6b0200df 	cmp	w6, w2
  400cf8:	bc656820 	ldr	s0, [x1, x5]
  400cfc:	1e202800 	fadd	s0, s0, s0
  400d00:	bc256800 	str	s0, [x0, x5]
  400d04:	5400018a 	b.ge	400d34 <manual_unroll+0xc4>  // b.tcont
  400d08:	91002085 	add	x5, x4, #0x8
  400d0c:	11000c63 	add	w3, w3, #0x3
  400d10:	6b02007f 	cmp	w3, w2
  400d14:	bc656820 	ldr	s0, [x1, x5]
  400d18:	1e202800 	fadd	s0, s0, s0
  400d1c:	bc256800 	str	s0, [x0, x5]
  400d20:	540000aa 	b.ge	400d34 <manual_unroll+0xc4>  // b.tcont
  400d24:	91003084 	add	x4, x4, #0xc
  400d28:	bc646820 	ldr	s0, [x1, x4]
  400d2c:	1e202800 	fadd	s0, s0, s0
  400d30:	bc246800 	str	s0, [x0, x4]
  400d34:	d65f03c0 	ret
  400d38:	91004026 	add	x6, x1, #0x10
  400d3c:	aa0103e3 	mov	x3, x1
  400d40:	aa0003e4 	mov	x4, x0
  400d44:	8b2550c6 	add	x6, x6, w5, uxtw #4
  400d48:	bd400060 	ldr	s0, [x3]
  400d4c:	91004063 	add	x3, x3, #0x10
  400d50:	91004084 	add	x4, x4, #0x10
  400d54:	1e202800 	fadd	s0, s0, s0
  400d58:	bc1f0080 	stur	s0, [x4, #-16]
  400d5c:	bc5f4060 	ldur	s0, [x3, #-12]
  400d60:	1e202800 	fadd	s0, s0, s0
  400d64:	bc1f4080 	stur	s0, [x4, #-12]
  400d68:	bc5f8060 	ldur	s0, [x3, #-8]
  400d6c:	1e202800 	fadd	s0, s0, s0
  400d70:	bc1f8080 	stur	s0, [x4, #-8]
  400d74:	bc5fc060 	ldur	s0, [x3, #-4]
  400d78:	eb06007f 	cmp	x3, x6
  400d7c:	1e202800 	fadd	s0, s0, s0
  400d80:	bc1fc080 	stur	s0, [x4, #-4]
  400d84:	54fffe21 	b.ne	400d48 <manual_unroll+0xd8>  // b.any
  400d88:	17ffffcd 	b	400cbc <manual_unroll+0x4c>
  400d8c:	52800003 	mov	w3, #0x0                   	// #0
  400d90:	17ffffcd 	b	400cc4 <manual_unroll+0x54>

0000000000400d94 <bad_loop>:
  400d94:	2a0003e2 	mov	w2, w0
  400d98:	7100001f 	cmp	w0, #0x0
  400d9c:	5400038d 	b.le	400e0c <bad_loop+0x78>
  400da0:	51000400 	sub	w0, w0, #0x1
  400da4:	7100641f 	cmp	w0, #0x19
  400da8:	54000369 	b.ls	400e14 <bad_loop+0x80>  // b.plast
  400dac:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x140>
  400db0:	52800001 	mov	w1, #0x0                   	// #0
  400db4:	4f000400 	movi	v0.4s, #0x0
  400db8:	4f000483 	movi	v3.4s, #0x4
  400dbc:	3dc03801 	ldr	q1, [x0, #224]
  400dc0:	53027c40 	lsr	w0, w2, #2
  400dc4:	d503201f 	nop
  400dc8:	4ea11c22 	mov	v2.16b, v1.16b
  400dcc:	11000421 	add	w1, w1, #0x1
  400dd0:	4ea38421 	add	v1.4s, v1.4s, v3.4s
  400dd4:	6b00003f 	cmp	w1, w0
  400dd8:	4ea28400 	add	v0.4s, v0.4s, v2.4s
  400ddc:	54ffff61 	b.ne	400dc8 <bad_loop+0x34>  // b.any
  400de0:	4eb1b800 	addv	s0, v0.4s
  400de4:	f240045f 	tst	x2, #0x3
  400de8:	121e7441 	and	w1, w2, #0xfffffffc
  400dec:	0e043c00 	mov	w0, v0.s[0]
  400df0:	540000c0 	b.eq	400e08 <bad_loop+0x74>  // b.none
  400df4:	d503201f 	nop
  400df8:	0b010000 	add	w0, w0, w1
  400dfc:	11000421 	add	w1, w1, #0x1
  400e00:	6b01005f 	cmp	w2, w1
  400e04:	54ffffac 	b.gt	400df8 <bad_loop+0x64>
  400e08:	d65f03c0 	ret
  400e0c:	52800000 	mov	w0, #0x0                   	// #0
  400e10:	d65f03c0 	ret
  400e14:	52800001 	mov	w1, #0x0                   	// #0
  400e18:	52800000 	mov	w0, #0x0                   	// #0
  400e1c:	17fffff7 	b	400df8 <bad_loop+0x64>

0000000000400e20 <__libc_csu_init>:
  400e20:	a9bc7bfd 	stp	x29, x30, [sp, #-64]!
  400e24:	910003fd 	mov	x29, sp
  400e28:	a90153f3 	stp	x19, x20, [sp, #16]
  400e2c:	b0000094 	adrp	x20, 411000 <__FRAME_END__+0xfce4>
  400e30:	91378294 	add	x20, x20, #0xde0
  400e34:	a9025bf5 	stp	x21, x22, [sp, #32]
  400e38:	b0000095 	adrp	x21, 411000 <__FRAME_END__+0xfce4>
  400e3c:	913742b5 	add	x21, x21, #0xdd0
  400e40:	cb150294 	sub	x20, x20, x21
  400e44:	2a0003f6 	mov	w22, w0
  400e48:	a90363f7 	stp	x23, x24, [sp, #48]
  400e4c:	aa0103f7 	mov	x23, x1
  400e50:	aa0203f8 	mov	x24, x2
  400e54:	97fffddf 	bl	4005d0 <_init>
  400e58:	eb940fff 	cmp	xzr, x20, asr #3
  400e5c:	54000160 	b.eq	400e88 <__libc_csu_init+0x68>  // b.none
  400e60:	9343fe94 	asr	x20, x20, #3
  400e64:	d2800013 	mov	x19, #0x0                   	// #0
  400e68:	f8737aa3 	ldr	x3, [x21, x19, lsl #3]
  400e6c:	aa1803e2 	mov	x2, x24
  400e70:	91000673 	add	x19, x19, #0x1
  400e74:	aa1703e1 	mov	x1, x23
  400e78:	2a1603e0 	mov	w0, w22
  400e7c:	d63f0060 	blr	x3
  400e80:	eb13029f 	cmp	x20, x19
  400e84:	54ffff21 	b.ne	400e68 <__libc_csu_init+0x48>  // b.any
  400e88:	a94153f3 	ldp	x19, x20, [sp, #16]
  400e8c:	a9425bf5 	ldp	x21, x22, [sp, #32]
  400e90:	a94363f7 	ldp	x23, x24, [sp, #48]
  400e94:	a8c47bfd 	ldp	x29, x30, [sp], #64
  400e98:	d65f03c0 	ret
  400e9c:	d503201f 	nop

0000000000400ea0 <__libc_csu_fini>:
  400ea0:	d65f03c0 	ret

Disassembly of section .fini:

0000000000400ea4 <_fini>:
  400ea4:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  400ea8:	910003fd 	mov	x29, sp
  400eac:	a8c17bfd 	ldp	x29, x30, [sp], #16
  400eb0:	d65f03c0 	ret
