// push constant 10
@10
D=A
@SP
M=M+1
A=M-1
M=D
// pop local 0
@0
D=A
@LCL
D=D+M
@addr
M=D
@SP
AM=M-1
D=M
@addr
A=M
M=D
// push constant 21
@21
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 22
@22
D=A
@SP
M=M+1
A=M-1
M=D
// pop argument 2
@2
D=A
@ARG
D=D+M
@addr
M=D
@SP
AM=M-1
D=M
@addr
A=M
M=D
// pop argument 1
@1
D=A
@ARG
D=D+M
@addr
M=D
@SP
AM=M-1
D=M
@addr
A=M
M=D
// push constant 36
@36
D=A
@SP
M=M+1
A=M-1
M=D
// pop this 6
@6
D=A
@THIS
D=D+M
@addr
M=D
@SP
AM=M-1
D=M
@addr
A=M
M=D
// push constant 42
@42
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 45
@45
D=A
@SP
M=M+1
A=M-1
M=D
// pop that 5
@5
D=A
@THAT
D=D+M
@addr
M=D
@SP
AM=M-1
D=M
@addr
A=M
M=D
// pop that 2
@2
D=A
@THAT
D=D+M
@addr
M=D
@SP
AM=M-1
D=M
@addr
A=M
M=D
// push constant 510
@510
D=A
@SP
M=M+1
A=M-1
M=D
// pop temp 6
@11
D=A
@addr
M=D
@SP
AM=M-1
D=M
@addr
A=M
M=D
// push local 0
@0
D=A
@LCL
D=D+M
@addr
AM=D
D=M
@SP
AM=M+1
A=A-1
M=D
// push that 5
@5
D=A
@THAT
D=D+M
@addr
AM=D
D=M
@SP
AM=M+1
A=A-1
M=D
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
// push argument 1
@1
D=A
@ARG
D=D+M
@addr
AM=D
D=M
@SP
AM=M+1
A=A-1
M=D
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// push this 6
@6
D=A
@THIS
D=D+M
@addr
AM=D
D=M
@SP
AM=M+1
A=A-1
M=D
// push this 6
@6
D=A
@THIS
D=D+M
@addr
AM=D
D=M
@SP
AM=M+1
A=A-1
M=D
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// push temp 6
@11
D=A
@addr
AM=D
D=M
@SP
AM=M+1
A=A-1
M=D
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
