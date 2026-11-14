module FSM_RX (Rx, CLK, B, EOR, S, RST, Q);
    input Rx, B, RST, CLK, Q;
    output reg EOR, S;

    reg [3:0] Estado;
    reg [3:0] contador;

    // State transitions are synchronized to the system clock.
    always @(negedge RST or posedge CLK)
        if (!RST) begin
            Estado <= 0;
            contador <= 0;
        end
        else
            case (Estado)
                0: begin
                    case ({Rx,B})
                        2'b00: Estado <= 1;
                        2'b01: Estado <= 1;
                        2'b10: Estado <= Estado;
                        2'b11: Estado <= Estado;
                    endcase
                end
                1: begin
                    case ({Rx,B})
                        2'b00: Estado <= Estado;
                        2'b01: Estado <= 2;
                        2'b10: Estado <= Estado;
                        2'b11: Estado <= 2;
                    endcase
                end
                2: begin
                    case ({Rx,B})
                        2'b00: Estado <= Estado;
                        2'b01: Estado <= 3;
                        2'b10: Estado <= Estado;
                        2'b11: Estado <= 3;
                    endcase
                end
                3: Estado <= 4;
                4: begin
                    case ({Rx,B})
                        2'b00: Estado <= Estado;
                        2'b01: Estado <= 5;
                        2'b10: Estado <= Estado;
                        2'b11: Estado <= 5;
                    endcase
                end
                5: begin
                    case ({Rx,B})
                        2'b00: Estado <= Estado;
                        2'b01: Estado <= 6;
                        2'b10: Estado <= Estado;
                        2'b11: Estado <= 6;
                    endcase
                end
                6: begin
                    case (Q)
                        1'b1: Estado <= 7;
                        1'b0: Estado <= 1;
                    endcase
                end
                7: begin
                    case ({Rx,B})
                        2'b00: Estado <= Estado;
                        2'b01: Estado <= 8;
                        2'b10: Estado <= Estado;
                        2'b11: Estado <= 8;
                    endcase
                end
                8: begin
                    case ({Rx,B})
                        2'b00: Estado <= Estado;
                        2'b01: Estado <= 9;
                        2'b10: Estado <= Estado;
                        2'b11: Estado <= 9;
                    endcase
                end
                9: Estado <= 0;
            endcase

    always @(*)
        case (Estado)
            0: {EOR,S} <= 2'b00;
            1: {EOR,S} <= 2'b00;
            2: {EOR,S} <= 2'b00;
            3: {EOR,S} <= 2'b01;
            4: {EOR,S} <= 2'b00;
            5: {EOR,S} <= 2'b00;
            6: {EOR,S} <= 2'b00;
            7: {EOR,S} <= 2'b00;
            8: {EOR,S} <= 2'b00;
            9: {EOR,S} <= 2'b10;
        endcase

endmodule
