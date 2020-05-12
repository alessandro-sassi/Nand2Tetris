// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

    // sum = 0, count= 0

    @sum
    M=0     
    @count
    M=0

    // if R1 == 0 -> go to R2=sum (perchè R0*0=0)
    @R1
    D=M
    @OUTPUT
    D;JEQ
    
(LOOP) // do {

    // sum = sum + R0

    @R0     
    D=M        
    @sum
    D=M+D     
    M=D

    // count = count + 1

    @count
    D=M
    M=D+1

    // } while count < R1
    
    @R1
    D=M
    @count
    D=M-D      // D= count - R1
    @LOOP
    D;JLT

(OUTPUT) // R2 = sum
    
    @sum
    D=M
    @R2
    M=D

(HALT)    // loop forever
    @HALT
    0;JMP
    
    
    

    