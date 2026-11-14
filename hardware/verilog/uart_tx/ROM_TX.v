module ROM_TX (
    input [6:0] direccion,
    output reg [7:0] dato
);

    always @(*) begin
        case (direccion)
            0: dato = 8'h62; // ASCII 'b'.
            1: dato = 8'h6F; // ASCII 'o'.
            2: dato = 8'h6F; // ASCII 'o'.
            3: dato = 8'h74; // ASCII 't'.
            4: dato = 8'h0D; // Carriage return.
            default: dato = 8'h00;
        endcase
    end

endmodule
