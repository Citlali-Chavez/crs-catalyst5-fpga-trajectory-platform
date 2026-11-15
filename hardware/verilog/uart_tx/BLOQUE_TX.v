module BLOQUE_TX (
    input CLK,
    input RST,
    input STT,
    input [7:0] D,
    output Tx,
    output EOT
);

    wire w_B;
    wire [3:0] w_M;

    BT_TX u_bt_tx (
        .CLK(CLK),
        .RST(RST),
        .B(w_B)
    );

    FSM_TX u_fsm_tx (
        .CLK(CLK),
        .RST(RST),
        .STT(STT),
        .B(w_B),
        .EOT(EOT),
        .M(w_M)
    );

    MUX_TX u_mux_tx (
        .D(D),
        .M(w_M),
        .Tx(Tx)
    );

endmodule
