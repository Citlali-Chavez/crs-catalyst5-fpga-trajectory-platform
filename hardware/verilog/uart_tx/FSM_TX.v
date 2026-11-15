module FSM_TX (
    input CLK,
    input RST,
    input STT,
    input B,
    output reg EOT,
    output reg [3:0] M
);

    reg [3:0] Estado_Actual, Estado_Siguiente;

    always @(posedge CLK or negedge RST) begin
        if (!RST)
            Estado_Actual <= 0;
        else
            Estado_Actual <= Estado_Siguiente;
    end

    always @(*) begin
        Estado_Siguiente = Estado_Actual;
        case (Estado_Actual)
            0: if (STT == 1 && B == 1) Estado_Siguiente = 1;
            1: if (B == 1) Estado_Siguiente = 2;
            2: if (B == 1) Estado_Siguiente = 3;
            3: if (B == 1) Estado_Siguiente = 4;
            4: if (B == 1) Estado_Siguiente = 5;
            5: if (B == 1) Estado_Siguiente = 6;
            6: if (B == 1) Estado_Siguiente = 7;
            7: if (B == 1) Estado_Siguiente = 8;
            8: if (B == 1) Estado_Siguiente = 9;
            9: if (B == 1) Estado_Siguiente = 10;
            10: if (B == 1) Estado_Siguiente = 0;
            default: Estado_Siguiente = 0;
        endcase
    end

    always @(*) begin
        case (Estado_Actual)
            0:  begin M = 10; EOT = 1; end
            1:  begin M = 0;  EOT = 0; end
            2:  begin M = 1;  EOT = 0; end
            3:  begin M = 2;  EOT = 0; end
            4:  begin M = 3;  EOT = 0; end
            5:  begin M = 4;  EOT = 0; end
            6:  begin M = 5;  EOT = 0; end
            7:  begin M = 6;  EOT = 0; end
            8:  begin M = 7;  EOT = 0; end
            9:  begin M = 8;  EOT = 0; end
            10: begin M = 9;  EOT = 0; end
            default: begin M = 10; EOT = 1; end
        endcase
    end

endmodule
