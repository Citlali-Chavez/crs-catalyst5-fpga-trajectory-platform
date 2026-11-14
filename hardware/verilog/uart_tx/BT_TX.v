module BT_TX #(parameter n=26) (CLK, RST, B);
    input CLK, RST;
    output B;

    reg [n-1:0] OUT;
    wire z;

    assign z = (OUT == 868) ? 1 : 0;
    assign B = z;

    always @(posedge CLK or negedge RST)
        if (!RST)
            OUT <= 0;
        else if (z == 1)
            OUT <= 0;
        else
            OUT <= OUT + 1;

endmodule
