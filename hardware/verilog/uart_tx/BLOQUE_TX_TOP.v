module BLOQUE_TX_TOP (
    input CLK,
    input RST,
    input START,
    output Tx
);

    wire w_EOT;
    wire w_STT;
    wire w_FIN;
    wire w_EN_CONT;
    wire [6:0] w_direccion;
    wire [7:0] w_dato;

    CONT_DIRECCIONES u_contador (
        .CLK(CLK),
        .RST(RST),
        .EN_CONT(w_EN_CONT),
        .direccion(w_direccion),
        .FIN(w_FIN)
    );

    ROM_TX u_rom (
        .direccion(w_direccion),
        .dato(w_dato)
    );

    FSM_GENERAL_TX u_fsm_maestra (
        .CLK(CLK),
        .RST(RST),
        .START(START),
        .EOT(w_EOT),
        .FIN(w_FIN),
        .STT(w_STT),
        .EN_CONT(w_EN_CONT)
    );

    BLOQUE_TX u_uart_tx (
        .CLK(CLK),
        .RST(RST),
        .STT(w_STT),
        .D(w_dato),
        .Tx(Tx),
        .EOT(w_EOT)
    );

endmodule
