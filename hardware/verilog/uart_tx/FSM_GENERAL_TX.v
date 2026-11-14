module FSM_GENERAL_TX (
    input CLK,
    input RST,
    input START,
    input EOT,
    input FIN,
    output reg STT,
    output reg EN_CONT
);

    reg [2:0] Estado_Actual, Estado_Siguiente;
    reg [31:0] timer;

    // 150 ms pause at 50 MHz (7,500,000 clock cycles).
    wire fin_pausa = (timer == 32'd7_500_000);

    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            Estado_Actual <= 0;
            timer <= 0;
        end else begin
            Estado_Actual <= Estado_Siguiente;
            if (Estado_Actual == 5)
                timer <= timer + 1;
            else
                timer <= 0;
        end
    end

    always @(*) begin
        Estado_Siguiente = Estado_Actual;
        case (Estado_Actual)
            0: if (START == 0) Estado_Siguiente = 1;
            1: if (EOT == 0) Estado_Siguiente = 2;
            2: if (EOT == 1) Estado_Siguiente = 5;
            5: if (fin_pausa) Estado_Siguiente = 3;
            3: Estado_Siguiente = 4;
            4: begin
                if (FIN == 1)
                    Estado_Siguiente = 6;
                else
                    Estado_Siguiente = 1;
            end
            // Remain here until START is deasserted (logic high).
            6: if (START == 1) Estado_Siguiente = 0;
            default: Estado_Siguiente = 0;
        endcase
    end

    always @(*) begin
        case (Estado_Actual)
            0: begin STT = 0; EN_CONT = 0; end
            1: begin STT = 1; EN_CONT = 0; end
            2: begin STT = 0; EN_CONT = 0; end
            5: begin STT = 0; EN_CONT = 0; end
            3: begin STT = 0; EN_CONT = 0; end
            4: begin STT = 0; EN_CONT = 1; end
            6: begin STT = 0; EN_CONT = 0; end
            default: begin STT = 0; EN_CONT = 0; end
        endcase
    end

endmodule
