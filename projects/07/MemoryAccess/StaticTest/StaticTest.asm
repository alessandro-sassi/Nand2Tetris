// push constant 111
@111
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 333
@333
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 888
@888
D=A
@SP
M=M+1
A=M-1
M=D
// pop static 8
@SP
AM=M-1
D=M
@BasicTest.8
M=D
// pop static 3
@SP
AM=M-1
D=M
@BasicTest.3
M=D
// pop static 1
@SP
AM=M-1
D=M
@BasicTest.1
M=D
// push static 3
@BasicTest.3
D=M
@SP
M=M+1
A=M-1
M=D
// push static 1
@BasicTest.1
D=M
@SP
M=M+1
A=M-1
M=D
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// push static 8
@BasicTest.8
D=M
@SP
M=M+1
A=M-1
M=D
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
