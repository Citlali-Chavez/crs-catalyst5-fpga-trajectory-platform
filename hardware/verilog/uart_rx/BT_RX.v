module BT_RX #(parameter n=10)(
    input CLK,
    input RST,
    output B
);

    reg [n-1:0] OUT;
    wire z;

    // Timing pulse used by the receiver sampling state machine.
    // The original source compares against 217 at a 50 MHz clock.
    assign z = (OUT == 217) ? 1'b1 : 1'b0;
    assign B = z;

    always @(posedge CLK or negedge RST) begin
        if (!RST)
            OUT <= 0;
        else if (z == 1'b1)
            OUT <= 0;
        else
            OUT <= OUT + 1;
    end

endmodule
