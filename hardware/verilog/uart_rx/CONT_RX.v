module CONT_RX #(parameter n=4)(
    input S,
    input RST,
    output Q
);

    reg [n-1:0] OUT;
    wire z;

    // Counts the ten UART frame bits: start, eight data bits and stop.
    assign z = (OUT == 9) ? 1'b1 : 1'b0;
    assign Q = z;

    always @(posedge S or negedge RST) begin
        if (!RST)
            OUT <= 0;
        else if (z == 1'b1)
            OUT <= 0;
        else
            OUT <= OUT + 1;
    end

endmodule
