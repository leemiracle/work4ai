
build/opt_O0：     文件格式 elf64-littleaarch64


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
  4005f4:	b0000090 	adrp	x16, 411000 <__FRAME_END__+0xfd18>
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
  4006c4:	f2816300 	movk	x0, #0xb18
  4006c8:	d2e00003 	movz	x3, #0x0, lsl #48
  4006cc:	f2c00003 	movk	x3, #0x0, lsl #32
  4006d0:	f2a00803 	movk	x3, #0x40, lsl #16
  4006d4:	f281c703 	movk	x3, #0xe38
  4006d8:	d2e00004 	movz	x4, #0x0, lsl #48
  4006dc:	f2c00004 	movk	x4, #0x0, lsl #32
  4006e0:	f2a00804 	movk	x4, #0x40, lsl #16
  4006e4:	f281d704 	movk	x4, #0xeb8
  4006e8:	97ffffce 	bl	400620 <__libc_start_main@plt>
  4006ec:	97ffffd9 	bl	400650 <abort@plt>

00000000004006f0 <call_weak_fn>:
  4006f0:	b0000080 	adrp	x0, 411000 <__FRAME_END__+0xfd18>
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
  40072c:	f9476c21 	ldr	x1, [x1, #3800]
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
  40076c:	f9477042 	ldr	x2, [x2, #3808]
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
  4007b4:	d100c3ff 	sub	sp, sp, #0x30
  4007b8:	f9000fe0 	str	x0, [sp, #24]
  4007bc:	f9000be1 	str	x1, [sp, #16]
  4007c0:	b9000fe2 	str	w2, [sp, #12]
  4007c4:	b9002fff 	str	wzr, [sp, #44]
  4007c8:	b9002bff 	str	wzr, [sp, #40]
  4007cc:	14000012 	b	400814 <dot_product+0x60>
  4007d0:	b9802be0 	ldrsw	x0, [sp, #40]
  4007d4:	d37ef400 	lsl	x0, x0, #2
  4007d8:	f9400fe1 	ldr	x1, [sp, #24]
  4007dc:	8b000020 	add	x0, x1, x0
  4007e0:	bd400001 	ldr	s1, [x0]
  4007e4:	b9802be0 	ldrsw	x0, [sp, #40]
  4007e8:	d37ef400 	lsl	x0, x0, #2
  4007ec:	f9400be1 	ldr	x1, [sp, #16]
  4007f0:	8b000020 	add	x0, x1, x0
  4007f4:	bd400000 	ldr	s0, [x0]
  4007f8:	1e200820 	fmul	s0, s1, s0
  4007fc:	bd402fe1 	ldr	s1, [sp, #44]
  400800:	1e202820 	fadd	s0, s1, s0
  400804:	bd002fe0 	str	s0, [sp, #44]
  400808:	b9402be0 	ldr	w0, [sp, #40]
  40080c:	11000400 	add	w0, w0, #0x1
  400810:	b9002be0 	str	w0, [sp, #40]
  400814:	b9402be1 	ldr	w1, [sp, #40]
  400818:	b9400fe0 	ldr	w0, [sp, #12]
  40081c:	6b00003f 	cmp	w1, w0
  400820:	54fffd8b 	b.lt	4007d0 <dot_product+0x1c>  // b.tstop
  400824:	bd402fe0 	ldr	s0, [sp, #44]
  400828:	9100c3ff 	add	sp, sp, #0x30
  40082c:	d65f03c0 	ret

0000000000400830 <conditional_sum>:
  400830:	d10083ff 	sub	sp, sp, #0x20
  400834:	f90007e0 	str	x0, [sp, #8]
  400838:	b90007e1 	str	w1, [sp, #4]
  40083c:	bd0003e0 	str	s0, [sp]
  400840:	b9001fff 	str	wzr, [sp, #28]
  400844:	b9001bff 	str	wzr, [sp, #24]
  400848:	14000014 	b	400898 <conditional_sum+0x68>
  40084c:	b9801be0 	ldrsw	x0, [sp, #24]
  400850:	d37ef400 	lsl	x0, x0, #2
  400854:	f94007e1 	ldr	x1, [sp, #8]
  400858:	8b000020 	add	x0, x1, x0
  40085c:	bd400000 	ldr	s0, [x0]
  400860:	bd4003e1 	ldr	s1, [sp]
  400864:	1e202030 	fcmpe	s1, s0
  400868:	54000125 	b.pl	40088c <conditional_sum+0x5c>  // b.nfrst
  40086c:	b9801be0 	ldrsw	x0, [sp, #24]
  400870:	d37ef400 	lsl	x0, x0, #2
  400874:	f94007e1 	ldr	x1, [sp, #8]
  400878:	8b000020 	add	x0, x1, x0
  40087c:	bd400000 	ldr	s0, [x0]
  400880:	bd401fe1 	ldr	s1, [sp, #28]
  400884:	1e202820 	fadd	s0, s1, s0
  400888:	bd001fe0 	str	s0, [sp, #28]
  40088c:	b9401be0 	ldr	w0, [sp, #24]
  400890:	11000400 	add	w0, w0, #0x1
  400894:	b9001be0 	str	w0, [sp, #24]
  400898:	b9401be1 	ldr	w1, [sp, #24]
  40089c:	b94007e0 	ldr	w0, [sp, #4]
  4008a0:	6b00003f 	cmp	w1, w0
  4008a4:	54fffd4b 	b.lt	40084c <conditional_sum+0x1c>  // b.tstop
  4008a8:	bd401fe0 	ldr	s0, [sp, #28]
  4008ac:	910083ff 	add	sp, sp, #0x20
  4008b0:	d65f03c0 	ret

00000000004008b4 <poly_eval>:
  4008b4:	d10083ff 	sub	sp, sp, #0x20
  4008b8:	f90007e0 	str	x0, [sp, #8]
  4008bc:	b90007e1 	str	w1, [sp, #4]
  4008c0:	bd0003e0 	str	s0, [sp]
  4008c4:	b9001fff 	str	wzr, [sp, #28]
  4008c8:	b94007e0 	ldr	w0, [sp, #4]
  4008cc:	51000400 	sub	w0, w0, #0x1
  4008d0:	b9001be0 	str	w0, [sp, #24]
  4008d4:	1400000e 	b	40090c <poly_eval+0x58>
  4008d8:	bd401fe1 	ldr	s1, [sp, #28]
  4008dc:	bd4003e0 	ldr	s0, [sp]
  4008e0:	1e200821 	fmul	s1, s1, s0
  4008e4:	b9801be0 	ldrsw	x0, [sp, #24]
  4008e8:	d37ef400 	lsl	x0, x0, #2
  4008ec:	f94007e1 	ldr	x1, [sp, #8]
  4008f0:	8b000020 	add	x0, x1, x0
  4008f4:	bd400000 	ldr	s0, [x0]
  4008f8:	1e202820 	fadd	s0, s1, s0
  4008fc:	bd001fe0 	str	s0, [sp, #28]
  400900:	b9401be0 	ldr	w0, [sp, #24]
  400904:	51000400 	sub	w0, w0, #0x1
  400908:	b9001be0 	str	w0, [sp, #24]
  40090c:	b9401be0 	ldr	w0, [sp, #24]
  400910:	7100001f 	cmp	w0, #0x0
  400914:	54fffe2a 	b.ge	4008d8 <poly_eval+0x24>  // b.tcont
  400918:	bd401fe0 	ldr	s0, [sp, #28]
  40091c:	910083ff 	add	sp, sp, #0x20
  400920:	d65f03c0 	ret

0000000000400924 <dead_code_test>:
  400924:	d10083ff 	sub	sp, sp, #0x20
  400928:	bd000fe0 	str	s0, [sp, #12]
  40092c:	bd400fe0 	ldr	s0, [sp, #12]
  400930:	529eb860 	mov	w0, #0xf5c3                	// #62915
  400934:	72a80900 	movk	w0, #0x4048, lsl #16
  400938:	1e270001 	fmov	s1, w0
  40093c:	1e210800 	fmul	s0, s0, s1
  400940:	bd001fe0 	str	s0, [sp, #28]
  400944:	bd401fe0 	ldr	s0, [sp, #28]
  400948:	bd0017e0 	str	s0, [sp, #20]
  40094c:	bd400fe0 	ldr	s0, [sp, #12]
  400950:	528e1480 	mov	w0, #0x70a4                	// #28836
  400954:	72a805a0 	movk	w0, #0x402d, lsl #16
  400958:	1e270001 	fmov	s1, w0
  40095c:	1e210800 	fmul	s0, s0, s1
  400960:	bd001be0 	str	s0, [sp, #24]
  400964:	bd401fe0 	ldr	s0, [sp, #28]
  400968:	910083ff 	add	sp, sp, #0x20
  40096c:	d65f03c0 	ret

0000000000400970 <manual_unroll>:
  400970:	d100c3ff 	sub	sp, sp, #0x30
  400974:	f9000fe0 	str	x0, [sp, #24]
  400978:	f9000be1 	str	x1, [sp, #16]
  40097c:	b9000fe2 	str	w2, [sp, #12]
  400980:	b9002fff 	str	wzr, [sp, #44]
  400984:	14000036 	b	400a5c <manual_unroll+0xec>
  400988:	b9802fe0 	ldrsw	x0, [sp, #44]
  40098c:	d37ef400 	lsl	x0, x0, #2
  400990:	f9400be1 	ldr	x1, [sp, #16]
  400994:	8b000020 	add	x0, x1, x0
  400998:	bd400000 	ldr	s0, [x0]
  40099c:	b9802fe0 	ldrsw	x0, [sp, #44]
  4009a0:	d37ef400 	lsl	x0, x0, #2
  4009a4:	f9400fe1 	ldr	x1, [sp, #24]
  4009a8:	8b000020 	add	x0, x1, x0
  4009ac:	1e202800 	fadd	s0, s0, s0
  4009b0:	bd000000 	str	s0, [x0]
  4009b4:	b9802fe0 	ldrsw	x0, [sp, #44]
  4009b8:	91000400 	add	x0, x0, #0x1
  4009bc:	d37ef400 	lsl	x0, x0, #2
  4009c0:	f9400be1 	ldr	x1, [sp, #16]
  4009c4:	8b000020 	add	x0, x1, x0
  4009c8:	bd400000 	ldr	s0, [x0]
  4009cc:	b9802fe0 	ldrsw	x0, [sp, #44]
  4009d0:	91000400 	add	x0, x0, #0x1
  4009d4:	d37ef400 	lsl	x0, x0, #2
  4009d8:	f9400fe1 	ldr	x1, [sp, #24]
  4009dc:	8b000020 	add	x0, x1, x0
  4009e0:	1e202800 	fadd	s0, s0, s0
  4009e4:	bd000000 	str	s0, [x0]
  4009e8:	b9802fe0 	ldrsw	x0, [sp, #44]
  4009ec:	91000800 	add	x0, x0, #0x2
  4009f0:	d37ef400 	lsl	x0, x0, #2
  4009f4:	f9400be1 	ldr	x1, [sp, #16]
  4009f8:	8b000020 	add	x0, x1, x0
  4009fc:	bd400000 	ldr	s0, [x0]
  400a00:	b9802fe0 	ldrsw	x0, [sp, #44]
  400a04:	91000800 	add	x0, x0, #0x2
  400a08:	d37ef400 	lsl	x0, x0, #2
  400a0c:	f9400fe1 	ldr	x1, [sp, #24]
  400a10:	8b000020 	add	x0, x1, x0
  400a14:	1e202800 	fadd	s0, s0, s0
  400a18:	bd000000 	str	s0, [x0]
  400a1c:	b9802fe0 	ldrsw	x0, [sp, #44]
  400a20:	91000c00 	add	x0, x0, #0x3
  400a24:	d37ef400 	lsl	x0, x0, #2
  400a28:	f9400be1 	ldr	x1, [sp, #16]
  400a2c:	8b000020 	add	x0, x1, x0
  400a30:	bd400000 	ldr	s0, [x0]
  400a34:	b9802fe0 	ldrsw	x0, [sp, #44]
  400a38:	91000c00 	add	x0, x0, #0x3
  400a3c:	d37ef400 	lsl	x0, x0, #2
  400a40:	f9400fe1 	ldr	x1, [sp, #24]
  400a44:	8b000020 	add	x0, x1, x0
  400a48:	1e202800 	fadd	s0, s0, s0
  400a4c:	bd000000 	str	s0, [x0]
  400a50:	b9402fe0 	ldr	w0, [sp, #44]
  400a54:	11001000 	add	w0, w0, #0x4
  400a58:	b9002fe0 	str	w0, [sp, #44]
  400a5c:	b9402fe0 	ldr	w0, [sp, #44]
  400a60:	11000c00 	add	w0, w0, #0x3
  400a64:	b9400fe1 	ldr	w1, [sp, #12]
  400a68:	6b00003f 	cmp	w1, w0
  400a6c:	54fff8ec 	b.gt	400988 <manual_unroll+0x18>
  400a70:	1400000f 	b	400aac <manual_unroll+0x13c>
  400a74:	b9802fe0 	ldrsw	x0, [sp, #44]
  400a78:	d37ef400 	lsl	x0, x0, #2
  400a7c:	f9400be1 	ldr	x1, [sp, #16]
  400a80:	8b000020 	add	x0, x1, x0
  400a84:	bd400000 	ldr	s0, [x0]
  400a88:	b9802fe0 	ldrsw	x0, [sp, #44]
  400a8c:	d37ef400 	lsl	x0, x0, #2
  400a90:	f9400fe1 	ldr	x1, [sp, #24]
  400a94:	8b000020 	add	x0, x1, x0
  400a98:	1e202800 	fadd	s0, s0, s0
  400a9c:	bd000000 	str	s0, [x0]
  400aa0:	b9402fe0 	ldr	w0, [sp, #44]
  400aa4:	11000400 	add	w0, w0, #0x1
  400aa8:	b9002fe0 	str	w0, [sp, #44]
  400aac:	b9402fe1 	ldr	w1, [sp, #44]
  400ab0:	b9400fe0 	ldr	w0, [sp, #12]
  400ab4:	6b00003f 	cmp	w1, w0
  400ab8:	54fffdeb 	b.lt	400a74 <manual_unroll+0x104>  // b.tstop
  400abc:	d503201f 	nop
  400ac0:	d503201f 	nop
  400ac4:	9100c3ff 	add	sp, sp, #0x30
  400ac8:	d65f03c0 	ret

0000000000400acc <bad_loop>:
  400acc:	d10083ff 	sub	sp, sp, #0x20
  400ad0:	b9000fe0 	str	w0, [sp, #12]
  400ad4:	b9001fff 	str	wzr, [sp, #28]
  400ad8:	b9001bff 	str	wzr, [sp, #24]
  400adc:	14000008 	b	400afc <bad_loop+0x30>
  400ae0:	b9401fe1 	ldr	w1, [sp, #28]
  400ae4:	b9401be0 	ldr	w0, [sp, #24]
  400ae8:	0b000020 	add	w0, w1, w0
  400aec:	b9001fe0 	str	w0, [sp, #28]
  400af0:	b9401be0 	ldr	w0, [sp, #24]
  400af4:	11000400 	add	w0, w0, #0x1
  400af8:	b9001be0 	str	w0, [sp, #24]
  400afc:	b9401be1 	ldr	w1, [sp, #24]
  400b00:	b9400fe0 	ldr	w0, [sp, #12]
  400b04:	6b00003f 	cmp	w1, w0
  400b08:	54fffecb 	b.lt	400ae0 <bad_loop+0x14>  // b.tstop
  400b0c:	b9401fe0 	ldr	w0, [sp, #28]
  400b10:	910083ff 	add	sp, sp, #0x20
  400b14:	d65f03c0 	ret

0000000000400b18 <main>:
  400b18:	d2880e0c 	mov	x12, #0x4070                	// #16496
  400b1c:	cb2c63ff 	sub	sp, sp, x12
  400b20:	a9007bfd 	stp	x29, x30, [sp]
  400b24:	910003fd 	mov	x29, sp
  400b28:	52800540 	mov	w0, #0x2a                  	// #42
  400b2c:	97fffed1 	bl	400670 <srand@plt>
  400b30:	914013e0 	add	x0, sp, #0x4, lsl #12
  400b34:	b9006c1f 	str	wzr, [x0, #108]
  400b38:	14000018 	b	400b98 <main+0x80>
  400b3c:	97fffebd 	bl	400630 <rand@plt>
  400b40:	1e220001 	scvtf	s1, w0
  400b44:	0f0265e0 	movi	v0.2s, #0x4f, lsl #24
  400b48:	1e201820 	fdiv	s0, s1, s0
  400b4c:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400b50:	91018000 	add	x0, x0, #0x60
  400b54:	914013e1 	add	x1, sp, #0x4, lsl #12
  400b58:	b9806c21 	ldrsw	x1, [x1, #108]
  400b5c:	bc217800 	str	s0, [x0, x1, lsl #2]
  400b60:	97fffeb4 	bl	400630 <rand@plt>
  400b64:	1e220001 	scvtf	s1, w0
  400b68:	0f0265e0 	movi	v0.2s, #0x4f, lsl #24
  400b6c:	1e201820 	fdiv	s0, s1, s0
  400b70:	d00000a0 	adrp	x0, 416000 <A+0x3fa0>
  400b74:	91018000 	add	x0, x0, #0x60
  400b78:	914013e1 	add	x1, sp, #0x4, lsl #12
  400b7c:	b9806c21 	ldrsw	x1, [x1, #108]
  400b80:	bc217800 	str	s0, [x0, x1, lsl #2]
  400b84:	914013e0 	add	x0, sp, #0x4, lsl #12
  400b88:	b9406c00 	ldr	w0, [x0, #108]
  400b8c:	11000400 	add	w0, w0, #0x1
  400b90:	914013e1 	add	x1, sp, #0x4, lsl #12
  400b94:	b9006c20 	str	w0, [x1, #108]
  400b98:	914013e0 	add	x0, sp, #0x4, lsl #12
  400b9c:	b9406c00 	ldr	w0, [x0, #108]
  400ba0:	713ffc1f 	cmp	w0, #0xfff
  400ba4:	54fffccd 	b.le	400b3c <main+0x24>
  400ba8:	52820002 	mov	w2, #0x1000                	// #4096
  400bac:	d00000a0 	adrp	x0, 416000 <A+0x3fa0>
  400bb0:	91018001 	add	x1, x0, #0x60
  400bb4:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400bb8:	91018000 	add	x0, x0, #0x60
  400bbc:	97fffefe 	bl	4007b4 <dot_product>
  400bc0:	914013e0 	add	x0, sp, #0x4, lsl #12
  400bc4:	bd006400 	str	s0, [x0, #100]
  400bc8:	1e2c1000 	fmov	s0, #5.000000000000000000e-01
  400bcc:	52820001 	mov	w1, #0x1000                	// #4096
  400bd0:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400bd4:	91018000 	add	x0, x0, #0x60
  400bd8:	97ffff16 	bl	400830 <conditional_sum>
  400bdc:	914013e0 	add	x0, sp, #0x4, lsl #12
  400be0:	bd006000 	str	s0, [x0, #96]
  400be4:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x130>
  400be8:	9103a000 	add	x0, x0, #0xe8
  400bec:	914013e2 	add	x2, sp, #0x4, lsl #12
  400bf0:	9100e042 	add	x2, x2, #0x38
  400bf4:	aa0003e3 	mov	x3, x0
  400bf8:	a9400460 	ldp	x0, x1, [x3]
  400bfc:	a9000440 	stp	x0, x1, [x2]
  400c00:	b9401060 	ldr	w0, [x3, #16]
  400c04:	b9001040 	str	w0, [x2, #16]
  400c08:	914013e0 	add	x0, sp, #0x4, lsl #12
  400c0c:	9100e000 	add	x0, x0, #0x38
  400c10:	1e201000 	fmov	s0, #2.000000000000000000e+00
  400c14:	528000a1 	mov	w1, #0x5                   	// #5
  400c18:	97ffff27 	bl	4008b4 <poly_eval>
  400c1c:	914013e0 	add	x0, sp, #0x4, lsl #12
  400c20:	bd005c00 	str	s0, [x0, #92]
  400c24:	1e2f1000 	fmov	s0, #1.500000000000000000e+00
  400c28:	97ffff3f 	bl	400924 <dead_code_test>
  400c2c:	914013e0 	add	x0, sp, #0x4, lsl #12
  400c30:	bd005800 	str	s0, [x0, #88]
  400c34:	9100e3e3 	add	x3, sp, #0x38
  400c38:	52820002 	mov	w2, #0x1000                	// #4096
  400c3c:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400c40:	91018001 	add	x1, x0, #0x60
  400c44:	aa0303e0 	mov	x0, x3
  400c48:	97ffff4a 	bl	400970 <manual_unroll>
  400c4c:	9100a3e0 	add	x0, sp, #0x28
  400c50:	aa0003e1 	mov	x1, x0
  400c54:	52800020 	mov	w0, #0x1                   	// #1
  400c58:	97fffe6e 	bl	400610 <clock_gettime@plt>
  400c5c:	b90017ff 	str	wzr, [sp, #20]
  400c60:	914013e0 	add	x0, sp, #0x4, lsl #12
  400c64:	b900681f 	str	wzr, [x0, #104]
  400c68:	14000010 	b	400ca8 <main+0x190>
  400c6c:	52820002 	mov	w2, #0x1000                	// #4096
  400c70:	d00000a0 	adrp	x0, 416000 <A+0x3fa0>
  400c74:	91018001 	add	x1, x0, #0x60
  400c78:	d0000080 	adrp	x0, 412000 <clock_gettime@GLIBC_2.17>
  400c7c:	91018000 	add	x0, x0, #0x60
  400c80:	97fffecd 	bl	4007b4 <dot_product>
  400c84:	1e204001 	fmov	s1, s0
  400c88:	bd4017e0 	ldr	s0, [sp, #20]
  400c8c:	1e202820 	fadd	s0, s1, s0
  400c90:	bd0017e0 	str	s0, [sp, #20]
  400c94:	914013e0 	add	x0, sp, #0x4, lsl #12
  400c98:	b9406800 	ldr	w0, [x0, #104]
  400c9c:	11000400 	add	w0, w0, #0x1
  400ca0:	914013e1 	add	x1, sp, #0x4, lsl #12
  400ca4:	b9006820 	str	w0, [x1, #104]
  400ca8:	914013e0 	add	x0, sp, #0x4, lsl #12
  400cac:	b9406800 	ldr	w0, [x0, #104]
  400cb0:	710f9c1f 	cmp	w0, #0x3e7
  400cb4:	54fffdcd 	b.le	400c6c <main+0x154>
  400cb8:	910063e0 	add	x0, sp, #0x18
  400cbc:	aa0003e1 	mov	x1, x0
  400cc0:	52800020 	mov	w0, #0x1                   	// #1
  400cc4:	97fffe53 	bl	400610 <clock_gettime@plt>
  400cc8:	f9400fe1 	ldr	x1, [sp, #24]
  400ccc:	f94017e0 	ldr	x0, [sp, #40]
  400cd0:	cb000020 	sub	x0, x1, x0
  400cd4:	9e670000 	fmov	d0, x0
  400cd8:	5e61d800 	scvtf	d0, d0
  400cdc:	d2c80000 	mov	x0, #0x400000000000        	// #70368744177664
  400ce0:	f2e811e0 	movk	x0, #0x408f, lsl #48
  400ce4:	9e670001 	fmov	d1, x0
  400ce8:	1e610801 	fmul	d1, d0, d1
  400cec:	f94013e1 	ldr	x1, [sp, #32]
  400cf0:	f9401be0 	ldr	x0, [sp, #48]
  400cf4:	cb000020 	sub	x0, x1, x0
  400cf8:	9e670000 	fmov	d0, x0
  400cfc:	5e61d800 	scvtf	d0, d0
  400d00:	d2d09000 	mov	x0, #0x848000000000        	// #145685290680320
  400d04:	f2e825c0 	movk	x0, #0x412e, lsl #48
  400d08:	9e670002 	fmov	d2, x0
  400d0c:	1e621800 	fdiv	d0, d0, d2
  400d10:	1e602820 	fadd	d0, d1, d0
  400d14:	fd202be0 	str	d0, [sp, #16464]
  400d18:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400d1c:	913ba000 	add	x0, x0, #0xee8
  400d20:	97fffe50 	bl	400660 <puts@plt>
  400d24:	914013e0 	add	x0, sp, #0x4, lsl #12
  400d28:	bd406400 	ldr	s0, [x0, #100]
  400d2c:	1e22c000 	fcvt	d0, s0
  400d30:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400d34:	913ca000 	add	x0, x0, #0xf28
  400d38:	97fffe52 	bl	400680 <printf@plt>
  400d3c:	914013e0 	add	x0, sp, #0x4, lsl #12
  400d40:	bd406000 	ldr	s0, [x0, #96]
  400d44:	1e22c000 	fcvt	d0, s0
  400d48:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400d4c:	913d0000 	add	x0, x0, #0xf40
  400d50:	97fffe4c 	bl	400680 <printf@plt>
  400d54:	914013e0 	add	x0, sp, #0x4, lsl #12
  400d58:	bd405c00 	ldr	s0, [x0, #92]
  400d5c:	1e22c000 	fcvt	d0, s0
  400d60:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400d64:	913d6000 	add	x0, x0, #0xf58
  400d68:	97fffe46 	bl	400680 <printf@plt>
  400d6c:	914013e0 	add	x0, sp, #0x4, lsl #12
  400d70:	bd405800 	ldr	s0, [x0, #88]
  400d74:	1e22c000 	fcvt	d0, s0
  400d78:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400d7c:	913dc000 	add	x0, x0, #0xf70
  400d80:	97fffe40 	bl	400680 <printf@plt>
  400d84:	bd403be0 	ldr	s0, [sp, #56]
  400d88:	1e22c004 	fcvt	d4, s0
  400d8c:	bd403fe0 	ldr	s0, [sp, #60]
  400d90:	1e22c001 	fcvt	d1, s0
  400d94:	bd4043e0 	ldr	s0, [sp, #64]
  400d98:	1e22c002 	fcvt	d2, s0
  400d9c:	bd4047e0 	ldr	s0, [sp, #68]
  400da0:	1e22c000 	fcvt	d0, s0
  400da4:	1e604003 	fmov	d3, d0
  400da8:	1e604080 	fmov	d0, d4
  400dac:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400db0:	913e2000 	add	x0, x0, #0xf88
  400db4:	97fffe33 	bl	400680 <printf@plt>
  400db8:	52800140 	mov	w0, #0xa                   	// #10
  400dbc:	97fffe35 	bl	400690 <putchar@plt>
  400dc0:	fd602be0 	ldr	d0, [sp, #16464]
  400dc4:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400dc8:	913ee000 	add	x0, x0, #0xfb8
  400dcc:	97fffe2d 	bl	400680 <printf@plt>
  400dd0:	52800140 	mov	w0, #0xa                   	// #10
  400dd4:	97fffe2f 	bl	400690 <putchar@plt>
  400dd8:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400ddc:	913f8000 	add	x0, x0, #0xfe0
  400de0:	97fffe20 	bl	400660 <puts@plt>
  400de4:	90000000 	adrp	x0, 400000 <_init-0x5d0>
  400de8:	913fe000 	add	x0, x0, #0xff8
  400dec:	97fffe1d 	bl	400660 <puts@plt>
  400df0:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x130>
  400df4:	9100c000 	add	x0, x0, #0x30
  400df8:	97fffe1a 	bl	400660 <puts@plt>
  400dfc:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x130>
  400e00:	91018000 	add	x0, x0, #0x60
  400e04:	97fffe17 	bl	400660 <puts@plt>
  400e08:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x130>
  400e0c:	91022000 	add	x0, x0, #0x88
  400e10:	97fffe14 	bl	400660 <puts@plt>
  400e14:	b0000000 	adrp	x0, 401000 <_IO_stdin_used+0x130>
  400e18:	9102e000 	add	x0, x0, #0xb8
  400e1c:	97fffe11 	bl	400660 <puts@plt>
  400e20:	bd4017e0 	ldr	s0, [sp, #20]
  400e24:	52800000 	mov	w0, #0x0                   	// #0
  400e28:	a9407bfd 	ldp	x29, x30, [sp]
  400e2c:	d2880e0c 	mov	x12, #0x4070                	// #16496
  400e30:	8b2c63ff 	add	sp, sp, x12
  400e34:	d65f03c0 	ret

0000000000400e38 <__libc_csu_init>:
  400e38:	a9bc7bfd 	stp	x29, x30, [sp, #-64]!
  400e3c:	910003fd 	mov	x29, sp
  400e40:	a90153f3 	stp	x19, x20, [sp, #16]
  400e44:	b0000094 	adrp	x20, 411000 <__FRAME_END__+0xfd18>
  400e48:	91378294 	add	x20, x20, #0xde0
  400e4c:	a9025bf5 	stp	x21, x22, [sp, #32]
  400e50:	b0000095 	adrp	x21, 411000 <__FRAME_END__+0xfd18>
  400e54:	913762b5 	add	x21, x21, #0xdd8
  400e58:	cb150294 	sub	x20, x20, x21
  400e5c:	2a0003f6 	mov	w22, w0
  400e60:	a90363f7 	stp	x23, x24, [sp, #48]
  400e64:	aa0103f7 	mov	x23, x1
  400e68:	aa0203f8 	mov	x24, x2
  400e6c:	97fffdd9 	bl	4005d0 <_init>
  400e70:	eb940fff 	cmp	xzr, x20, asr #3
  400e74:	54000160 	b.eq	400ea0 <__libc_csu_init+0x68>  // b.none
  400e78:	9343fe94 	asr	x20, x20, #3
  400e7c:	d2800013 	mov	x19, #0x0                   	// #0
  400e80:	f8737aa3 	ldr	x3, [x21, x19, lsl #3]
  400e84:	aa1803e2 	mov	x2, x24
  400e88:	91000673 	add	x19, x19, #0x1
  400e8c:	aa1703e1 	mov	x1, x23
  400e90:	2a1603e0 	mov	w0, w22
  400e94:	d63f0060 	blr	x3
  400e98:	eb13029f 	cmp	x20, x19
  400e9c:	54ffff21 	b.ne	400e80 <__libc_csu_init+0x48>  // b.any
  400ea0:	a94153f3 	ldp	x19, x20, [sp, #16]
  400ea4:	a9425bf5 	ldp	x21, x22, [sp, #32]
  400ea8:	a94363f7 	ldp	x23, x24, [sp, #48]
  400eac:	a8c47bfd 	ldp	x29, x30, [sp], #64
  400eb0:	d65f03c0 	ret
  400eb4:	d503201f 	nop

0000000000400eb8 <__libc_csu_fini>:
  400eb8:	d65f03c0 	ret

Disassembly of section .fini:

0000000000400ebc <_fini>:
  400ebc:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
  400ec0:	910003fd 	mov	x29, sp
  400ec4:	a8c17bfd 	ldp	x29, x30, [sp], #16
  400ec8:	d65f03c0 	ret
