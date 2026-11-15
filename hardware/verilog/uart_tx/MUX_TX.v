module MUX_TX (
    input [7:0] D,
    input [3:0] M,
    output reg Tx
);

    always @(*) begin
        case (M)
            0: Tx = 1'b0; // Start bit.
            1: Tx = D[0];
            2: Tx = D[1];
            3: Tx = D[2];
            4: Tx = D[3];
            5: Tx = D[4];
            6: Tx = D[5];
            7: Tx = D[6];
            8: Tx = D[7];
            9: Tx = 1'b1; // Stop bit.
            10: Tx = 1'b1; // Idle state (EOT).
            default: Tx = 1'b1;
        endcase
    end

endmodule
