////////////////////////////////////////////////////////////////////////////////
// Dual-Channel Calibration Register
// ARM writes calibration values via system bus, FPGA reads them
// Verilog-2001 compatible version
// Register map:
//   0x00: ADC A calibration gain (Q16.16 fixed-point)
//   0x04: ADC B calibration gain (Q16.16 fixed-point)
////////////////////////////////////////////////////////////////////////////////

module calib_register (
    // System signals
    input  wire        clk,
    input  wire        rstn,
    
    // Calibration outputs (Q16.16 fixed-point)
    output wire [31:0] calib_gain_a,  // ADC channel A calibration
    output wire [31:0] calib_gain_b,  // ADC channel B calibration
    
    // System bus interface
    input  wire [19:0] sys_addr,
    input  wire [31:0] sys_wdata,
    input  wire        sys_wen,
    input  wire        sys_ren,
    output reg  [31:0] sys_rdata,
    output wire        sys_err,
    output reg         sys_ack
);

// Default calibration: 1.0 in Q16.16 = 65536 = 0x00010000
localparam [31:0] DEFAULT_CALIB = 32'h00010000;

// Registers for calibration values
reg [31:0] calib_reg_a;  // ADC channel A
reg [31:0] calib_reg_b;  // ADC channel B

// Initialize to default
initial begin
    calib_reg_a = DEFAULT_CALIB;
    calib_reg_b = DEFAULT_CALIB;
end

// System bus write
always @(posedge clk) begin
    if (~rstn) begin
        calib_reg_a <= DEFAULT_CALIB;
        calib_reg_b <= DEFAULT_CALIB;
    end else if (sys_wen) begin
        // Address 0x00: ADC A calibration gain
        if (sys_addr[19:2] == 18'h0) begin
            calib_reg_a <= sys_wdata;
        end
        // Address 0x04: ADC B calibration gain
        else if (sys_addr[19:2] == 18'h1) begin
            calib_reg_b <= sys_wdata;
        end
    end
end

// System bus read
always @(posedge clk) begin
    if (~rstn) begin
        sys_rdata <= 32'h0;
        sys_ack <= 1'b0;
    end else begin
        sys_ack <= sys_wen | sys_ren;
        if (sys_ren) begin
            case (sys_addr[19:2])
                18'h0: sys_rdata <= calib_reg_a;  // Read ADC A calibration
                18'h1: sys_rdata <= calib_reg_b;  // Read ADC B calibration
                default: sys_rdata <= 32'h0;
            endcase
        end
    end
end

assign sys_err = 1'b0;

// Output the calibration values
assign calib_gain_a = calib_reg_a;
assign calib_gain_b = calib_reg_b;

endmodule