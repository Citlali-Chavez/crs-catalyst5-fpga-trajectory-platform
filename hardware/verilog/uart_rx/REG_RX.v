module REG_RX (
    input Rx,
    input S,
    input CLK,
    input RST,
    output [7:0] R
);

    reg [9:0] Data_reg;

    always @(posedge CLK or negedge RST) begin
        if (!RST)
            Data_reg <= 10'b0;
        else if (S)
            // Shift right; serial data is received least-significant bit first.
            Data_reg <= {Rx, Data_reg[9:1]};
    end

    // R exposes the eight data bits, excluding start and stop bits.
    assign R = Data_reg[8:1];

endmodule
