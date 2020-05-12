// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


    (SET)
        @i
        M=0        // i = 0
 
        @SCREEN
        D=A
        @addr
        M=D        // addr = SCREEN

        @8192
        D=A
        @n
        M=D        // n = 8192
  
    (CHECK_KBD)         // do {
        @KBD
        D=M
        @SET_BLACK     
        D;JNE        // go to SET BLACK if RAM[KBD] != 0 (if key is pressed)
        @SET_WHITE   // otherwise go to SET WHITE 
        0;JMP

    (SET_BLACK)
        @addr
        A=M
        M=-1     // RAM[addr] = 111111111111111111   (Set 16 pixels to black)
        @LOOP   
        0;JMP                                   

    (SET_WHITE)
        @addr
        A=M
        M=0        // RAM[addr] = 00000000000000000000   (Set 16 pixels to white)
        @LOOP
        0;JMP

    (LOOP)
        @addr
        M=M+1      //addr = addr + +1

        @i
        MD=M+1      // i = i + 1

        @n
        D=D-M
        @CHECK_KBD
        D;JLT       // while i < n (go to loop if (i-n) < 0  

    @SET
    0;JMP           // go back to beginning of the code

    


    

    