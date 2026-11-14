module CONT_DIRECCIONES (
    input CLK,
    input RST,
    input EN_CONT,
    output reg [6:0] direccion,
    output FIN
);

    assign FIN = (direccion == 4) ? 1'b1 : 1'b0;

    always @(posedge CLK or negedge RST) begin
        if (!RST)
            direccion <= 0;
        else if (EN_CONT == 1) begin
            if (direccion == 4)
                direccion <= 0;
            else
                direccion <= direccion + 1;
        end
    end

endmodule
