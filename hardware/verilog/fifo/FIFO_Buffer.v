module FIFO_Buffer (
    input CLK,
    input RST,
    input wr_en,
    input rd_en,
    input [7:0] data_in,
    output reg [7:0] data_out,
    output empty,
    output full
);

    // 256-entry, 8-bit-wide storage.
    reg [7:0] memoria [0:255];

    reg [7:0] wr_ptr;
    reg [7:0] rd_ptr;
    reg [8:0] contador_datos;

    assign empty = (contador_datos == 0) ? 1'b1 : 1'b0;
    assign full = (contador_datos == 256) ? 1'b1 : 1'b0;

    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            wr_ptr <= 0;
            rd_ptr <= 0;
            contador_datos <= 0;
        end else begin
            // Simultaneous write and read: occupancy remains unchanged.
            if (wr_en && !full && rd_en && !empty) begin
                memoria[wr_ptr] <= data_in;
                wr_ptr <= wr_ptr + 1;
                rd_ptr <= rd_ptr + 1;
            end
            // Write only.
            else if (wr_en && !full) begin
                memoria[wr_ptr] <= data_in;
                wr_ptr <= wr_ptr + 1;
                contador_datos <= contador_datos + 1;
            end
            // Read only.
            else if (rd_en && !empty) begin
                rd_ptr <= rd_ptr + 1;
                contador_datos <= contador_datos - 1;
            end
        end
    end

    always @(posedge CLK or negedge RST) begin
        if (!RST)
            data_out <= 8'b0;
        else if (rd_en && !empty)
            data_out <= memoria[rd_ptr];
    end

endmodule
