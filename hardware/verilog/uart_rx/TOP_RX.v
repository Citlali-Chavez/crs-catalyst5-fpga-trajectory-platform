module TOP_RX (
    input Rx,
    input RST,
    input CLK,
    output EOR,
    output [7:0] D
);

    wire B;
    wire S;
    wire Q;

    BT_RX u_BT_RX (
        .CLK(CLK),
        .RST(RST),
        .B(B)
    );

    CONT_RX u_CONT_RX (
        .S(S),
        .RST(RST),
        .Q(Q)
    );

    REG_RX u_REG_RX (
        .Rx(Rx),
        .S(S),
        .CLK(CLK),
        .RST(RST),
        .R(D)
    );

    FSM_RX u_FSM_RX (
        .Rx(Rx),
        .CLK(CLK),
        .B(B),
        .EOR(EOR),
        .S(S),
        .RST(RST),
        .Q(Q)
    );

endmodule
